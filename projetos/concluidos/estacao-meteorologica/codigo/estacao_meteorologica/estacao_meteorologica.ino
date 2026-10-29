#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <time.h>

//================ WIFI ==================
const char* ssid = "CONFIGURE_LOCALMENTE";
const char* password = "CONFIGURE_LOCALMENTE";

//================ FIREBASE ==============
#define DATABASE_URL "CONFIGURE_LOCALMENTE"

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;

//================ DHT11 =================
#define DHTPIN 4
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

//================ BMP280 ================
Adafruit_BMP280 bmp;

//================ NTP ===================
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -10800;      // Horário de Brasília
const int daylightOffset_sec = 0;

void setup() {

  Serial.begin(115200);

  Serial.println();
  Serial.println("=================================");
  Serial.println("ESTACAO METEOROLOGICA");
  Serial.println("=================================");

  // DHT11
  dht.begin();

  // BMP280
  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 nao encontrado!");
    while (true);
  }

  // WiFi
  WiFi.begin(ssid, password);

  Serial.print("Conectando ao WiFi");

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }

  Serial.println();
  Serial.println("WiFi conectado!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());

  // Data e hora
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer);

  struct tm timeinfo;

  Serial.print("Sincronizando horario");

  while (!getLocalTime(&timeinfo)) {
    Serial.print(".");
    delay(1000);
  }

  Serial.println();
  Serial.println("Horario sincronizado!");

  // Firebase
  config.database_url = DATABASE_URL;
  config.signer.test_mode = true;

  Firebase.begin(&config, &auth);
  Firebase.reconnectWiFi(true);

  Serial.println("Firebase conectado!");
}

void loop() {

  float temperaturaDHT = dht.readTemperature();
  float umidade = dht.readHumidity();

  float temperaturaBMP = bmp.readTemperature();
  float pressao = bmp.readPressure() / 100.0F;

  if (isnan(temperaturaDHT) || isnan(umidade)) {
    Serial.println("Erro ao ler DHT11!");
    delay(5000);
    return;
  }

  struct tm timeinfo;
  char dataHora[25] = "";

  if (getLocalTime(&timeinfo)) {
    strftime(dataHora, sizeof(dataHora), "%d/%m/%Y %H:%M:%S", &timeinfo);
  }

  Serial.println();
  Serial.println("========== DADOS ==========");

  Serial.print("Data/Hora: ");
  Serial.println(dataHora);

  Serial.print("Temperatura DHT11: ");
  Serial.print(temperaturaDHT);
  Serial.println(" °C");

  Serial.print("Umidade: ");
  Serial.print(umidade);
  Serial.println(" %");

  Serial.print("Temperatura BMP280: ");
  Serial.print(temperaturaBMP);
  Serial.println(" °C");

  Serial.print("Pressao: ");
  Serial.print(pressao);
  Serial.println(" hPa");

  bool ok = true;

  ok &= Firebase.RTDB.setFloat(&fbdo, "/sensores/temperatura_dht", temperaturaDHT);
  ok &= Firebase.RTDB.setFloat(&fbdo, "/sensores/umidade", umidade);
  ok &= Firebase.RTDB.setFloat(&fbdo, "/sensores/temperatura_bmp", temperaturaBMP);
  ok &= Firebase.RTDB.setFloat(&fbdo, "/sensores/pressao", pressao);
  ok &= Firebase.RTDB.setString(&fbdo, "/sensores/data_hora", dataHora);

  if (ok) {
    Serial.println();
    Serial.println("Dados enviados ao Firebase com sucesso!");
  } else {
    Serial.println();
    Serial.print("Erro ao enviar: ");
    Serial.println(fbdo.errorReason());
  }

  Serial.println("----------------------------------");
  Serial.println("Proxima leitura em 5 minutos");
  Serial.println();

  delay(300000); // 5 minutos
}
