/*
   Estacao meteorologica - ESP32 + DHT11 + BMP280 + Firebase RTDB

   - Envia uma leitura imediatamente apos o Firebase ficar pronto
   - Depois envia a cada 5 minutos
   - Mantem a ultima leitura em /sensores
   - Mantem todas as leituras em /historico usando pushJSON
   - Grava data/hora de Brasilia e timestamp do servidor Firebase
*/

#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <time.h>

#include "addons/TokenHelper.h"
#include "addons/RTDBHelper.h"

// ============================================================
// WIFI
// ============================================================
#define WIFI_SSID "SUA_REDE_WIFI"
#define WIFI_PASSWORD "SUA_SENHA_WIFI"

// ============================================================
// FIREBASE
// Valores conferidos diretamente no firebaseConfig do projeto.
// ============================================================
#define API_KEY "SUA_CHAVE_API"
#define DATABASE_URL "https://SEU_PROJETO-default-rtdb.firebaseio.com/"
// Project ID: [CONFIGURAR]
// App ID: [CONFIGURAR]
#define USER_EMAIL "SEU_EMAIL"
#define USER_PASSWORD "SUA_SENHA_FIREBASE"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

// ============================================================
// DHT11
// ============================================================
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

// ============================================================
// BMP280
// ============================================================
Adafruit_BMP280 bmp;

// ============================================================
// INTERVALO: 5 MINUTOS
// ============================================================
const unsigned long INTERVALO_MEDICAO = 300000UL;
unsigned long ultimaMedicao = 0;

// ============================================================
// HORARIO DE BRASILIA: UTC-3
// ============================================================
const long GMT_OFFSET_SEC = -3L * 3600L;
const int DAYLIGHT_OFFSET_SEC = 0;

String obterDataHoraBrasilia()
{
  struct tm timeinfo;

  if (!getLocalTime(&timeinfo, 5000))
    return "horario_indisponivel";

  char texto[20];
  strftime(texto, sizeof(texto), "%d/%m/%Y %H:%M:%S", &timeinfo);
  return String(texto);
}

String obterDataBrasilia()
{
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 5000))
    return "indisponivel";

  char texto[11];
  strftime(texto, sizeof(texto), "%d/%m/%Y", &timeinfo);
  return String(texto);
}

String obterHoraBrasilia()
{
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 5000))
    return "indisponivel";

  char texto[9];
  strftime(texto, sizeof(texto), "%H:%M:%S", &timeinfo);
  return String(texto);
}

void conectarWiFi()
{
  Serial.println();
  Serial.print("Conectando ao Wi-Fi: ");
  Serial.println(WIFI_SSID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED)
  {
    Serial.print(".");
    delay(500);
  }

  Serial.println();
  Serial.println("Wi-Fi conectado.");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

bool iniciarBMP280()
{
  if (bmp.begin(0x76))
  {
    Serial.println("BMP280 encontrado em 0x76.");
    return true;
  }

  if (bmp.begin(0x77))
  {
    Serial.println("BMP280 encontrado em 0x77.");
    return true;
  }

  return false;
}

void realizarMedicao()
{
  float temperaturaDHT = dht.readTemperature();
  float umidade = dht.readHumidity();

  if (isnan(temperaturaDHT) || isnan(umidade))
  {
    Serial.println("ERRO: falha na leitura do DHT11.");
    return;
  }

  float temperaturaBMP = bmp.readTemperature();
  float pressao = bmp.readPressure() / 100.0F;

  if (isnan(temperaturaBMP) || isnan(pressao))
  {
    Serial.println("ERRO: falha na leitura do BMP280.");
    return;
  }

  String data = obterDataBrasilia();
  String hora = obterHoraBrasilia();
  String dataHora = obterDataHoraBrasilia();

  Serial.println();
  Serial.println("========== NOVA LEITURA ==========");
  Serial.print("Data/hora Brasilia: ");
  Serial.println(dataHora);
  Serial.print("Temperatura DHT11: ");
  Serial.print(temperaturaDHT, 2);
  Serial.println(" C");
  Serial.print("Umidade: ");
  Serial.print(umidade, 2);
  Serial.println(" %");
  Serial.print("Temperatura BMP280: ");
  Serial.print(temperaturaBMP, 2);
  Serial.println(" C");
  Serial.print("Pressao: ");
  Serial.print(pressao, 2);
  Serial.println(" hPa");

  FirebaseJson leitura;

  // Nomes compativeis com a estrutura simples usada originalmente.
  leitura.set("temperatura", temperaturaDHT);
  leitura.set("umidade", umidade);
  leitura.set("pressao", pressao);

  // Campo adicional: temperatura medida pelo BMP280.
  leitura.set("temperatura_bmp280", temperaturaBMP);

  // Data e hora no fuso de Brasilia.
  leitura.set("data", data);
  leitura.set("hora", hora);
  leitura.set("data_hora_brasilia", dataHora);
  leitura.set("fuso_horario", "America/Sao_Paulo (UTC-03:00)");

  // O servidor do Firebase substitui este marcador pelo Unix timestamp em ms.
  leitura.set("timestamp/.sv", "timestamp");

  Serial.println("Enviando ao Firebase...");

  // 1) HISTORICO: push cria uma chave nova e nao apaga leituras antigas.
  if (Firebase.RTDB.pushJSON(&fbdo, "/historico", &leitura))
  {
    Serial.println("Historico salvo com sucesso.");
    Serial.print("Chave: ");
    Serial.println(fbdo.pushName());
  }
  else
  {
    Serial.print("ERRO ao salvar /historico: ");
    Serial.println(fbdo.errorReason());
  }

  // 2) ULTIMA LEITURA: sobrescrita propositalmente para consulta rapida.
  if (Firebase.RTDB.setJSON(&fbdo, "/sensores", &leitura))
  {
    Serial.println("/sensores atualizado com sucesso.");
  }
  else
  {
    Serial.print("ERRO ao atualizar /sensores: ");
    Serial.println(fbdo.errorReason());
  }

  Serial.println("===================================");
}

void setup()
{
  Serial.begin(115200);
  delay(1000);

  Serial.println();
  Serial.println("ESTACAO METEOROLOGICA");

  dht.begin();
  delay(2000);

  Wire.begin(21, 22);

  if (!iniciarBMP280())
  {
    Serial.println("ERRO: BMP280 nao encontrado em 0x76 nem 0x77.");
    while (true)
      delay(1000);
  }

  conectarWiFi();

  // NTP em UTC-3 (Brasilia).
  configTime(
    GMT_OFFSET_SEC,
    DAYLIGHT_OFFSET_SEC,
    "pool.ntp.org",
    "time.nist.gov"
  );

  Serial.print("Sincronizando horario");
  struct tm timeinfo;
  int tentativas = 0;
  while (!getLocalTime(&timeinfo, 1000) && tentativas < 15)
  {
    Serial.print(".");
    tentativas++;
  }
  Serial.println();

  if (getLocalTime(&timeinfo))
  {
    Serial.print("Horario de Brasilia: ");
    Serial.println(obterDataHoraBrasilia());
  }
  else
  {
    Serial.println("AVISO: NTP ainda nao sincronizou.");
  }

  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;

  Serial.print("Firebase Database URL: ");
  Serial.println(DATABASE_URL);
  Serial.print("Usuario Firebase Auth: ");
  Serial.println(USER_EMAIL);

  // Ajuda no diagnostico de autenticacao no Monitor Serial.
  config.token_status_callback = tokenStatusCallback;

  fbdo.setBSSLBufferSize(2048, 1024);
  Firebase.reconnectNetwork(true);
  Firebase.begin(&config, &auth);

  Serial.println("Firebase iniciado. Aguardando autenticacao...");
}

void loop()
{
  if (WiFi.status() != WL_CONNECTED)
  {
    Serial.println("Wi-Fi desconectado. Reconectando...");
    conectarWiFi();
  }

  if (!Firebase.ready())
  {
    // tokenStatusCallback mostrara informacoes mais detalhadas no Serial.
    delay(1000);
    return;
  }

  // Primeira leitura imediatamente; depois, a cada 5 minutos.
  if (ultimaMedicao == 0 || millis() - ultimaMedicao >= INTERVALO_MEDICAO)
  {
    ultimaMedicao = millis();
    realizarMedicao();
  }

  delay(100);
}
