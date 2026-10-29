// Versão didática da 2.9. Leia primeiro setup(): ele mostra o ciclo completo.
// ESP32 com Arduino-ESP32 3.x, DHT, ArduinoJson e partição com LittleFS.
// Preencha as credenciais abaixo antes de gravar na placa.

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <DHT.h>
#include <LittleFS.h>
#include "driver/i2s_std.h"
#include "driver/rtc_io.h"
#include "esp_sleep.h"
#include "esp_system.h"
#include <math.h>
#include <stddef.h>
#include <time.h>

// 1. Configuração: estes são os valores que o aluno provavelmente irá alterar.
const char* WIFI_SSID = "CONFIGURE_LOCALMENTE";
const char* WIFI_PASSWORD = "CONFIGURE_LOCALMENTE";
const char* FIREBASE_URL = "https://SEU-PROJETO-default-rtdb.firebaseio.com";
const char* FIREBASE_API_KEY = "CONFIGURE_LOCALMENTE";
const char* FIREBASE_EMAIL = "PREENCHER";
const char* FIREBASE_PASSWORD = "PREENCHER";
const char* HIVE_ID = "colmeia_01";

const int PIN_DHT_EXTERNO = 4;
const int PIN_DHT_INTERNO = 21;
const int PIN_TAMPA = 27;
const int PIN_BATERIA = 34;
const int PIN_AUDIO_WS = 25;
const int PIN_AUDIO_BCLK = 26;
const int PIN_AUDIO_DOUT = 33;

const uint32_t COLETA_S = 10 * 60;       // 10 minutos de sono entre coletas
const uint32_t TAMPA_ABERTA_S = 60;       // com tampa aberta, acorda em 1 minuto
const uint32_t ENVIO_S = 2 * 60 * 60;    // tentativas a cada 2 horas
const int PRIMEIRA_HORA = 6;             // horário local UTC-3
const int ULTIMA_HORA = 22;              // horários: 06, 08, ..., 22
const int FUSO_S = -3 * 60 * 60;
const int AUDIO_HZ = 16000;
const uint32_t AUDIO_MS = 3000;
const int TAMANHO_LOTE = 12;
const int MAX_MEDICOES = 2016;           // até 14 dias de coletas regulares

const char* FILA = "/fila_didatica.bin";
const char* TEMP = "/fila_didatica.tmp";
const char* BACKUP = "/fila_didatica.bak";
const uint32_t ASSINATURA_MEDICAO = 0xC01A2901;
const uint32_t ASSINATURA_RTC = 0xC01A2902;

// Um registro pequeno por coleta. Ele sobrevive ao deep sleep na flash.
// Este formato é diferente do arquivo binário da versão 2.9 original.
struct Medicao {
  uint32_t assinatura;
  uint32_t checksum;
  uint32_t id1, id2;
  int64_t horarioUnix;
  float temperaturaExterna, umidadeExterna;
  float temperaturaInterna, umidadeInterna;
  float bateriaV, bateriaPct;
  float audioRms, audioDbfs, cruzamentosHz;
  uint32_t amostrasAudio;
  int8_t leituraTampa;
  uint8_t despertouPelaTampa;
};

// Declarações explícitas para o Arduino reconhecer o tipo Medicao.
void lerTemperatura(Medicao& m);
void lerBateria(Medicao& m);
void lerAudio(Medicao& m);
uint32_t checksumDaMedicao(const Medicao& m);
Medicao coletar();
bool guardar(Medicao& m);
String chave(const Medicao& m);
String jsonDaMedicao(const Medicao& m);
bool enviarUma(const Medicao& m);
void enviarEventoTampa(const Medicao& m);

DHT dhtExterno(PIN_DHT_EXTERNO, DHT11);
DHT dhtInterno(PIN_DHT_INTERNO, DHT11);
WiFiClientSecure clienteSeguro;
String tokenFirebase;
bool flashPronta = false;

// Somente estes valores precisam sobreviver ao deep sleep.
RTC_DATA_ATTR uint32_t assinaturaRtc = 0;
RTC_DATA_ATTR int64_t proximoEnvioUnix = 0;
RTC_DATA_ATTR uint32_t segundosSemTentar = 0;
RTC_DATA_ATTR uint32_t ultimoSonoPlanejado = 0;

bool horarioValido() {
  return time(nullptr) >= 1704067200;  // 01/01/2024; evita o horário de 1970
}

int horaLocal(time_t agora) {
  time_t local = agora + FUSO_S;
  struct tm partes;
  gmtime_r(&local, &partes);
  return partes.tm_hour;
}

bool horarioDeEnvio(time_t agora) {
  int hora = horaLocal(agora);
  return hora >= PRIMEIRA_HORA && hora <= ULTIMA_HORA;
}

// Calcula o próximo horário da grade: 06, 08, ..., 22; depois, 06 do outro dia.
int64_t calcularProximoEnvio(time_t agora) {
  time_t local = agora + FUSO_S;
  struct tm partes;
  gmtime_r(&local, &partes);
  int segundosHoje = partes.tm_hour * 3600 + partes.tm_min * 60 + partes.tm_sec;
  int64_t inicioDoDiaUtc = (int64_t)agora - segundosHoje;

  if (partes.tm_hour < PRIMEIRA_HORA)
    return inicioDoDiaUtc + PRIMEIRA_HORA * 3600LL;
  if (partes.tm_hour >= ULTIMA_HORA)
    return inicioDoDiaUtc + 86400LL + PRIMEIRA_HORA * 3600LL;

  int intervaloHoras = ENVIO_S / 3600;
  int proximaHora = PRIMEIRA_HORA +
                    ((partes.tm_hour - PRIMEIRA_HORA) / intervaloHoras + 1) * intervaloHoras;
  if (proximaHora > ULTIMA_HORA)
    return inicioDoDiaUtc + 86400LL + PRIMEIRA_HORA * 3600LL;
  return inicioDoDiaUtc + proximaHora * 3600LL;
}

// Sem NTP, contamos o tempo planejado de sono para não ligar o Wi-Fi a cada coleta.
bool chegouHoraDeConsultar() {
  time_t agora = time(nullptr);
  if (horarioValido())
    return horarioDeEnvio(agora) &&
           (proximoEnvioUnix == 0 || agora >= proximoEnvioUnix);
  return esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_UNDEFINED ||
         segundosSemTentar >= ENVIO_S;
}

void prepararRelogioRtc() {
  if (assinaturaRtc != ASSINATURA_RTC) {
    assinaturaRtc = ASSINATURA_RTC;
    proximoEnvioUnix = 0;
    segundosSemTentar = 0;
    ultimoSonoPlanejado = 0;
  } else if (esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_TIMER) {
    uint64_t total = (uint64_t)segundosSemTentar + ultimoSonoPlanejado;
    segundosSemTentar = total > 604800 ? 604800 : total;
  }
}

void marcarTentativa() {
  segundosSemTentar = 0;
  proximoEnvioUnix = horarioValido() ? calcularProximoEnvio(time(nullptr)) : 0;
}

// 2. Sensores: cada função preenche uma parte da mesma medição.
void lerTemperatura(Medicao& m) {
  m.temperaturaExterna = dhtExterno.readTemperature();
  m.umidadeExterna = dhtExterno.readHumidity();
  m.temperaturaInterna = dhtInterno.readTemperature();
  m.umidadeInterna = dhtInterno.readHumidity();
  if (isnan(m.temperaturaExterna) || isnan(m.umidadeExterna))
    m.temperaturaExterna = m.umidadeExterna = NAN;
  if (isnan(m.temperaturaInterna) || isnan(m.umidadeInterna))
    m.temperaturaInterna = m.umidadeInterna = NAN;
  // O DHT devolve NAN quando falha; o JSON converterá isso em null.
}

void lerBateria(Medicao& m) {
  uint32_t somaMv = 0;
  for (int i = 0; i < 30; i++) {
    somaMv += analogReadMilliVolts(PIN_BATERIA);
    delay(5);
  }
  // Divisor com dois resistores de 100 kΩ: a tensão lida é a metade.
  m.bateriaV = (somaMv / 30.0f / 1000.0f) * 2.0f;
  m.bateriaPct = constrain(100.0f * (m.bateriaV - 3.20f) / (4.15f - 3.20f),
                           0.0f, 100.0f);
}

void lerAudio(Medicao& m) {
  m.audioRms = m.audioDbfs = m.cruzamentosHz = NAN;
  m.amostrasAudio = 0;

  i2s_chan_handle_t canal = nullptr;
  i2s_chan_config_t cfg = I2S_CHANNEL_DEFAULT_CONFIG(I2S_NUM_0, I2S_ROLE_MASTER);
  cfg.dma_desc_num = 4;
  cfg.dma_frame_num = 512;
  if (i2s_new_channel(&cfg, nullptr, &canal) != ESP_OK) return;

  i2s_std_config_t padrao = {
    .clk_cfg = I2S_STD_CLK_DEFAULT_CONFIG(AUDIO_HZ),
    .slot_cfg = I2S_STD_PHILIPS_SLOT_DEFAULT_CONFIG(I2S_DATA_BIT_WIDTH_32BIT,
                                                    I2S_SLOT_MODE_MONO),
    .gpio_cfg = {
      .mclk = I2S_GPIO_UNUSED,
      .bclk = (gpio_num_t)PIN_AUDIO_BCLK,
      .ws = (gpio_num_t)PIN_AUDIO_WS,
      .dout = I2S_GPIO_UNUSED,
      .din = (gpio_num_t)PIN_AUDIO_DOUT,
      .invert_flags = {.mclk_inv = false, .bclk_inv = false, .ws_inv = false}
    }
  };
  padrao.slot_cfg.slot_mask = I2S_STD_SLOT_LEFT; // L/R do INMP441 ligado ao GND
  if (i2s_channel_init_std_mode(canal, &padrao) != ESP_OK ||
      i2s_channel_enable(canal) != ESP_OK) {
    i2s_del_channel(canal);
    return;
  }

  int32_t buffer[512];
  double soma = 0, somaQuadrados = 0;
  uint32_t cruzamentos = 0;
  int sinalAnterior = 0;
  unsigned long inicio = millis();
  while (millis() - inicio < AUDIO_MS) {
    size_t bytes = 0;
    if (i2s_channel_read(canal, buffer, sizeof(buffer), &bytes, 1000) != ESP_OK)
      continue;
    int quantidade = bytes / sizeof(int32_t);
    for (int i = 0; i < quantidade; i++) {
      double x = (buffer[i] >> 8) / 8388608.0;
      soma += x;
      somaQuadrados += x * x;
      m.amostrasAudio++;
      int sinal = x > 0.0005 ? 1 : (x < -0.0005 ? -1 : 0);
      if (sinal != 0) {
        if (sinalAnterior != 0 && sinal != sinalAnterior) cruzamentos++;
        sinalAnterior = sinal;
      }
    }
  }
  i2s_channel_disable(canal);
  i2s_del_channel(canal);

  if (m.amostrasAudio == 0) return;
  double media = soma / m.amostrasAudio;
  double variancia = somaQuadrados / m.amostrasAudio - media * media;
  m.audioRms = sqrt(variancia > 0 ? variancia : 0);
  m.audioDbfs = m.audioRms > 0.0000001 ? 20 * log10(m.audioRms) : -120;
  m.cruzamentosHz = cruzamentos * (float)AUDIO_HZ / m.amostrasAudio / 2;
}

uint32_t checksumDaMedicao(const Medicao& m) {
  // Verifica os mesmos bytes gravados, sem copiar a estrutura nem alterá-la.
  const uint8_t* bytes = (const uint8_t*)&m;
  uint32_t hash = 2166136261UL;
  for (size_t i = 0; i < sizeof(m); i++) {
    bool campoChecksum = i >= offsetof(Medicao, checksum) &&
                         i < offsetof(Medicao, checksum) + sizeof(m.checksum);
    uint8_t byte = campoChecksum ? 0 : bytes[i];
    hash = (hash ^ byte) * 16777619UL;
  }
  return hash;
}

Medicao coletar() {
  Medicao m = {};
  m.assinatura = ASSINATURA_MEDICAO;
  m.id1 = esp_random();
  m.id2 = esp_random();
  m.despertouPelaTampa = esp_sleep_get_wakeup_cause() == ESP_SLEEP_WAKEUP_EXT0;
  m.leituraTampa = digitalRead(PIN_TAMPA); // HIGH significa tampa aberta
  lerBateria(m);
  lerTemperatura(m);
  lerAudio(m);
  return m;
}

// 3. Fila local: gravamos primeiro; só retiramos após confirmação do Firebase.
bool iniciarFlash() {
  if (!LittleFS.begin(true)) return false;
  if (!LittleFS.exists(FILA) && LittleFS.exists(BACKUP))
    LittleFS.rename(BACKUP, FILA);
  if (LittleFS.exists(FILA) && LittleFS.exists(BACKUP)) LittleFS.remove(BACKUP);
  if (LittleFS.exists(TEMP)) LittleFS.remove(TEMP);
  return true;
}

size_t itensNaFila() {
  if (!flashPronta || !LittleFS.exists(FILA)) return 0;
  File arq = LittleFS.open(FILA, FILE_READ);
  if (!arq) return 0;
  size_t quantidade = arq.size() / sizeof(Medicao);
  arq.close();
  return quantidade;
}

bool retirarDaFila(size_t quantidade) {
  if (!flashPronta || !LittleFS.exists(FILA)) return false;
  File origem = LittleFS.open(FILA, FILE_READ);
  if (!origem) return false;
  size_t pular = quantidade * sizeof(Medicao);
  size_t restantes = pular < origem.size() ? origem.size() - pular : 0;
  size_t bytesCompletos = restantes - restantes % sizeof(Medicao);
  if (bytesCompletos == 0) {
    origem.close();
    return LittleFS.remove(FILA);
  }
  if (!origem.seek(pular)) { origem.close(); return false; }
  LittleFS.remove(TEMP);
  File destino = LittleFS.open(TEMP, FILE_WRITE);
  if (!destino) { origem.close(); return false; }
  uint8_t buffer[256];
  bool copiado = true;
  while (bytesCompletos > 0) {
    size_t pedir = bytesCompletos < sizeof(buffer) ? bytesCompletos : sizeof(buffer);
    size_t lidos = origem.read(buffer, pedir);
    if (lidos == 0 || destino.write(buffer, lidos) != lidos) {
      copiado = false;
      break;
    }
    bytesCompletos -= lidos;
  }
  destino.flush();
  destino.close();
  origem.close();
  if (!copiado) { LittleFS.remove(TEMP); return false; }
  LittleFS.remove(BACKUP);
  if (!LittleFS.rename(FILA, BACKUP)) { LittleFS.remove(TEMP); return false; }
  if (!LittleFS.rename(TEMP, FILA)) {
    LittleFS.rename(BACKUP, FILA);
    return false;
  }
  LittleFS.remove(BACKUP);
  return true;
}

bool guardar(Medicao& m) {
  if (!flashPronta) return false;
  // Uma queda de energia pode deixar bytes incompletos no fim do arquivo.
  if (LittleFS.exists(FILA)) {
    File arq = LittleFS.open(FILA, FILE_READ);
    if (!arq) return false;
    bool caudaIncompleta = arq.size() % sizeof(Medicao) != 0;
    arq.close();
    if (caudaIncompleta && !retirarDaFila(0)) return false;
  }
  if (itensNaFila() >= MAX_MEDICOES && !retirarDaFila(1)) return false;
  m.checksum = checksumDaMedicao(m);
  File arq = LittleFS.open(FILA, FILE_APPEND);
  if (!arq) return false;
  bool completo = arq.write((const uint8_t*)&m, sizeof(m)) == sizeof(m);
  arq.flush();
  arq.close();
  return completo;
}

// 4. Internet: só é ligada quando a agenda ou a tampa pedem.
bool conectarWifi() {
  WiFi.mode(WIFI_STA);
  WiFi.setSleep(true);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  unsigned long inicio = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - inicio < 20000)
    delay(250);
  return WiFi.status() == WL_CONNECTED;
}

void sincronizarRelogio() {
  configTime(FUSO_S, 0, "pool.ntp.org", "time.google.com");
  unsigned long inicio = millis();
  while (!horarioValido() && millis() - inicio < 10000) delay(250);
}

bool autenticarFirebase() {
  HTTPClient http;
  http.setConnectTimeout(15000);
  http.setTimeout(15000);
  String url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=";
  url += FIREBASE_API_KEY;
  if (!http.begin(clienteSeguro, url)) return false;
  http.addHeader("Content-Type", "application/json");
  DynamicJsonDocument pedido(512);
  pedido["email"] = FIREBASE_EMAIL;
  pedido["password"] = FIREBASE_PASSWORD;
  pedido["returnSecureToken"] = true;
  String corpo;
  serializeJson(pedido, corpo);
  int codigo = http.POST(corpo);
  if (codigo < 200 || codigo >= 300) { http.end(); return false; }
  String respostaJson = http.getString();
  http.end();
  DynamicJsonDocument resposta(4096);
  DeserializationError erro = deserializeJson(resposta, respostaJson);
  if (erro) return false;
  tokenFirebase = resposta["idToken"].as<String>();
  return tokenFirebase.length() > 0;
}

bool pedirFirebase(const char* metodo, const String& caminho, const String& corpo) {
  // Uma fila grande pode atravessar as 23h: confira antes de cada requisição.
  if (WiFi.status() != WL_CONNECTED || !horarioValido() ||
      !horarioDeEnvio(time(nullptr))) return false;
  if (tokenFirebase.isEmpty() && !autenticarFirebase()) return false;
  if (!horarioDeEnvio(time(nullptr))) return false;
  HTTPClient http;
  http.setConnectTimeout(15000);
  http.setTimeout(15000);
  String url = String(FIREBASE_URL) + caminho + ".json?auth=" + tokenFirebase;
  if (!http.begin(clienteSeguro, url)) return false;
  http.addHeader("Content-Type", "application/json");
  int codigo = http.sendRequest(metodo, corpo);
  http.end();
  return codigo >= 200 && codigo < 300;
}

String chave(const Medicao& m) {
  char texto[24];
  snprintf(texto, sizeof(texto), "m_%08lx%08lx",
           (unsigned long)m.id1, (unsigned long)m.id2);
  return String(texto);
}

String numeroOuNull(float numero, int casas) {
  return isfinite(numero) ? String(numero, casas) : String("null");
}

String jsonDaMedicao(const Medicao& m) {
  String j;
  j.reserve(600);
  j = "{\"id_medicao_local\":\"" + chave(m) + "\",";
  j += "\"id_colmeia\":\"" + String(HIVE_ID) + "\",";
  j += "\"timestamp_servidor\":{\".sv\":\"timestamp\"},";
  if (m.horarioUnix > 0) {
    char horario[24];
    time_t local = (time_t)m.horarioUnix + FUSO_S;
    struct tm partes;
    gmtime_r(&local, &partes);
    strftime(horario, sizeof(horario), "%d/%m/%Y %H:%M:%S", &partes);
    char unixTexto[24];
    snprintf(unixTexto, sizeof(unixTexto), "%lld", (long long)m.horarioUnix);
    j += "\"horario_medicao_unix_s\":" + String(unixTexto) + ",";
    j += "\"horario_medicao_local\":\"" + String(horario) + "\",";
  } else {
    j += "\"horario_medicao_unix_s\":null,\"horario_medicao_local\":null,";
  }
  j += "\"fuso_horario_medicao\":\"UTC-03:00\",";
  j += "\"temperatura_externa_c\":" + numeroOuNull(m.temperaturaExterna, 1) + ",";
  j += "\"umidade_externa_pct\":" + numeroOuNull(m.umidadeExterna, 1) + ",";
  j += "\"temperatura_interna_c\":" + numeroOuNull(m.temperaturaInterna, 1) + ",";
  j += "\"umidade_interna_pct\":" + numeroOuNull(m.umidadeInterna, 1) + ",";
  j += "\"tensao_bateria_v\":" + numeroOuNull(m.bateriaV, 3) + ",";
  j += "\"carga_bateria_pct_estimada\":" + numeroOuNull(m.bateriaPct, 1) + ",";
  j += "\"leitura_bruta_mc38\":" + String((int)m.leituraTampa) + ",";
  j += "\"tampa_aberta\":" + String(m.leituraTampa == HIGH ? "true" : "false") + ",";
  j += "\"causa_despertar\":\"" + String(m.despertouPelaTampa ? "tampa_ext0" : "temporizador_ou_reset") + "\",";
  j += "\"audio_rms\":" + numeroOuNull(m.audioRms, 6) + ",";
  j += "\"audio_dbfs\":" + numeroOuNull(m.audioDbfs, 1) + ",";
  j += "\"audio_cruzamentos_zero_hz\":" + numeroOuNull(m.cruzamentosHz, 1) + ",";
  j += "\"amostras_audio_utilizadas\":" + String(m.amostrasAudio) + ",";
  j += "\"intervalo_coleta_s\":" + String(COLETA_S) + ",";
  j += "\"intervalo_envio_s\":" + String(ENVIO_S) + ",";
  j += "\"versao_firmware\":\"2.9 simplificada\"}";
  return j;
}

bool enviarUma(const Medicao& m) {
  String caminho = "/hives/" + String(HIVE_ID);
  String json = jsonDaMedicao(m);
  String lote = "{\"" + chave(m) + "\":" + json + "}";
  if (!pedirFirebase("PATCH", caminho + "/readings", lote)) return false;
  pedirFirebase("PUT", caminho + "/latest", json);
  return true;
}

void enviarFila() {
  String caminho = "/hives/" + String(HIVE_ID);
  while (itensNaFila() > 0) {
    File arq = LittleFS.open(FILA, FILE_READ);
    if (!arq) return;
    String lote = "{";
    int lidos = 0, validos = 0;
    Medicao ultima = {};
    while (lidos < TAMANHO_LOTE && arq.available() >= (int)sizeof(Medicao)) {
      Medicao m;
      if (arq.read((uint8_t*)&m, sizeof(m)) != sizeof(m)) {
        arq.close();
        return; // Falha de leitura: preserva a fila para a próxima tentativa.
      }
      lidos++;
      if (m.assinatura != ASSINATURA_MEDICAO ||
          m.checksum != checksumDaMedicao(m)) continue;
      if (validos > 0) lote += ",";
      lote += "\"" + chave(m) + "\":" + jsonDaMedicao(m);
      validos++;
      ultima = m;
    }
    arq.close();
    lote += "}";
    if (lidos == 0) return;
    if (validos > 0) {
      if (!pedirFirebase("PATCH", caminho + "/readings", lote)) return;
      pedirFirebase("PUT", caminho + "/latest", jsonDaMedicao(ultima));
    }
    if (!retirarDaFila(lidos)) return;
  }
}

void enviarEventoTampa(const Medicao& m) {
  if (!m.despertouPelaTampa) return;
  String evento = "{\"timestamp_servidor\":{\".sv\":\"timestamp\"},";
  evento += "\"evento\":\"despertar_por_tampa\",";
  evento += "\"id_medicao_local\":\"" + chave(m) + "\",";
  evento += "\"tampa_aberta\":";
  evento += m.leituraTampa == HIGH ? "true}" : "false}";
  pedirFirebase("POST", "/hives/" + String(HIVE_ID) + "/events/lid", evento);
}

// 5. Dormir: acorda por temporizador ou abertura da tampa.
void dormir(bool tampaAberta) {
  uint32_t segundos = tampaAberta ? TAMPA_ABERTA_S : COLETA_S;
  ultimoSonoPlanejado = segundos;
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  btStop();
  esp_sleep_enable_timer_wakeup((uint64_t)segundos * 1000000ULL);

  rtc_gpio_init((gpio_num_t)PIN_TAMPA);
  rtc_gpio_set_direction((gpio_num_t)PIN_TAMPA, RTC_GPIO_MODE_INPUT_ONLY);
  rtc_gpio_pullup_en((gpio_num_t)PIN_TAMPA);
  rtc_gpio_pulldown_dis((gpio_num_t)PIN_TAMPA);
  esp_sleep_pd_config(ESP_PD_DOMAIN_RTC_PERIPH, ESP_PD_OPTION_ON);
  // Com a tampa já aberta, EXT0 causaria despertar imediato sem parar.
  if (!tampaAberta) esp_sleep_enable_ext0_wakeup((gpio_num_t)PIN_TAMPA, HIGH);
  esp_deep_sleep_start();
}

void setup() {
  // Preparar a placa e recuperar a agenda mantida durante o deep sleep.
  prepararRelogioRtc();
  flashPronta = iniciarFlash();
  clienteSeguro.setInsecure(); // Igual ao protótipo 2.9; exige cuidado em produção.
  rtc_gpio_deinit((gpio_num_t)PIN_TAMPA);
  pinMode(PIN_TAMPA, INPUT_PULLUP);
  analogReadResolution(12);
  analogSetPinAttenuation(PIN_BATERIA, ADC_11db);
  dhtExterno.begin();
  dhtInterno.begin();
  delay(1500);

  // Coletar antes de ligar o Wi-Fi.
  Medicao atual = coletar();
  unsigned long fimDaColeta = millis();
  if (horarioValido()) atual.horarioUnix = time(nullptr);

  // Conectar apenas quando a agenda ou um evento da tampa exigir.
  bool consultar = chegouHoraDeConsultar();
  bool eventoTampa = atual.despertouPelaTampa;
  bool conectar = consultar || (eventoTampa && !horarioValido()) ||
                  (eventoTampa && horarioDeEnvio(time(nullptr)));
  bool conectado = conectar && conectarWifi();
  if (conectado) {
    sincronizarRelogio();
    // A coleta aconteceu antes da conexão. Descontamos o tempo acordado.
    if (horarioValido())
      atual.horarioUnix = time(nullptr) - (millis() - fimDaColeta + 500) / 1000;
  }

  bool guardada = guardar(atual); // Guardar antes de tentar transmitir.

  if (horarioValido()) {
    time_t agora = time(nullptr);
    bool dentroDaJanela = horarioDeEnvio(agora);
    bool envioVencido = proximoEnvioUnix == 0 || agora >= proximoEnvioUnix;
    if (conectado && dentroDaJanela) {
      if (eventoTampa) enviarEventoTampa(atual);
      if (envioVencido) {
        if (guardada) enviarFila();
        else enviarUma(atual); // tentativa direta quando a flash falha
      }
    }
    if (envioVencido && (consultar || conectado)) marcarTentativa();
  } else if (consultar) {
    marcarTentativa(); // sem NTP, só consulta novamente após 2 horas de sono
  }
  dormir(atual.leituraTampa == HIGH); // O próximo despertar recomeça setup().
}

void loop() {} // O despertar do deep sleep reinicia setup().
