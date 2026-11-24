// Estacao meteorologica: coleta a cada 5 minutos, salva na flash e tenta
// enviar imediatamente entre 06h e 18h (horario de Brasilia, UTC-3).
// Das 18h ate as 06h, entra em deep sleep e nao coleta dados.
// Pendencias sobrevivem a reinicios e sao reenviadas em ordem de coleta.
//
// Arduino IDE: escolha uma particao com sistema de arquivos, por exemplo
// "Default 4MB with spiffs". LittleFS utiliza essa area, sem cartao SD.
// Comunicacao Firebase via HTTPClient e WiFiClientSecure do Arduino-ESP32.
// Nao depende de Firebase_ESP_Client nem ArduinoJson. Instale apenas as
// bibliotecas dos sensores DHT e BMP280; as demais fazem parte do ESP32.

#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <Wire.h>
#include <Adafruit_BMP280.h>
#include <LittleFS.h>
#include <Preferences.h>
#include <esp_system.h>
#include <esp_timer.h>
#include <esp_sleep.h>
#include <time.h>
#include <math.h>
#include <stddef.h>

//================ WIFI ==================
const char* ssid = "SUA_REDE";
const char* password = "SUA_SENHA";

//================ FIREBASE ==============
#define DATABASE_URL "https://SEU-PROJETO-default-rtdb.firebaseio.com/"

// Acesso REST sem autenticacao: requer regras de escrita que permitam
// os caminhos /historico e /sensores, como configurado durante os testes.
String firebaseLastError;
const unsigned long HTTPS_TIMEOUT_MS = 15000UL;

// Raizes de confianca obtidas de https://pki.goog/roots.pem em 03/11/2026.
// Inclui o conjunto completo publicado pelo Google nesta data. Atualize este
// conjunto ao atualizar o firmware, pois as autoridades podem mudar.
// O cliente valida a cadeia do servidor e o nome do host; nao usa setInsecure.
static const char GOOGLE_ROOT_CERTIFICATES[] PROGMEM = R"GOOGLE_CA(
-----BEGIN CERTIFICATE-----
MIIFVzCCAz+gAwIBAgINAgPlk28xsBNJiGuiFzANBgkqhkiG9w0BAQwFADBHMQsw
CQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEU
MBIGA1UEAxMLR1RTIFJvb3QgUjEwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAw
MDAwWjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZp
Y2VzIExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjEwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQC2EQKLHuOhd5s73L+UPreVp0A8of2C+X0yBoJx9vaMf/vo
27xqLpeXo4xL+Sv2sfnOhB2x+cWX3u+58qPpvBKJXqeqUqv4IyfLpLGcY9vXmX7w
Cl7raKb0xlpHDU0QM+NOsROjyBhsS+z8CZDfnWQpJSMHobTSPS5g4M/SCYe7zUjw
TcLCeoiKu7rPWRnWr4+wB7CeMfGCwcDfLqZtbBkOtdh+JhpFAz2weaSUKK0Pfybl
qAj+lug8aJRT7oM6iCsVlgmy4HqMLnXWnOunVmSPlk9orj2XwoSPwLxAwAtcvfaH
szVsrBhQf4TgTM2S0yDpM7xSma8ytSmzJSq0SPly4cpk9+aCEI3oncKKiPo4Zor8
Y/kB+Xj9e1x3+naH+uzfsQ55lVe0vSbv1gHR6xYKu44LtcXFilWr06zqkUspzBmk
MiVOKvFlRNACzqrOSbTqn3yDsEB750Orp2yjj32JgfpMpf/VjsPOS+C12LOORc92
wO1AK/1TD7Cn1TsNsYqiA94xrcx36m97PtbfkSIS5r762DL8EGMUUXLeXdYWk70p
aDPvOmbsB4om3xPXV2V4J95eSRQAogB/mqghtqmxlbCluQ0WEdrHbEg8QOB+DVrN
VjzRlwW5y0vtOUucxD/SVRNuJLDWcfr0wbrM7Rv1/oFB2ACYPTrIrnqYNxgFlQID
AQABo0IwQDAOBgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4E
FgQU5K8rJnEaK0gnhS9SZizv8IkTcT4wDQYJKoZIhvcNAQEMBQADggIBAJ+qQibb
C5u+/x6Wki4+omVKapi6Ist9wTrYggoGxval3sBOh2Z5ofmmWJyq+bXmYOfg6LEe
QkEzCzc9zolwFcq1JKjPa7XSQCGYzyI0zzvFIoTgxQ6KfF2I5DUkzps+GlQebtuy
h6f88/qBVRRiClmpIgUxPoLW7ttXNLwzldMXG+gnoot7TiYaelpkttGsN/H9oPM4
7HLwEXWdyzRSjeZ2axfG34arJ45JK3VmgRAhpuo+9K4l/3wV3s6MJT/KYnAK9y8J
ZgfIPxz88NtFMN9iiMG1D53Dn0reWVlHxYciNuaCp+0KueIHoI17eko8cdLiA6Ef
MgfdG+RCzgwARWGAtQsgWSl4vflVy2PFPEz0tv/bal8xa5meLMFrUKTX5hgUvYU/
Z6tGn6D/Qqc6f1zLXbBwHSs09dR2CQzreExZBfMzQsNhFRAbd03OIozUhfJFfbdT
6u9AWpQKXCBfTkBdYiJ23//OYb2MI3jSNwLgjt7RETeJ9r/tSQdirpLsQBqvFAnZ
0E6yove+7u7Y/9waLd64NnHi/Hm3lCXRSHNboTXns5lndcEZOitHTtNCjv0xyBZm
2tIMPNuzjsmhDYAPexZ3FL//2wmUspO8IFgV6dtxQ/PeEMMA3KgqlbbC1j+Qa3bb
bP6MvPJwNQzcmRk13NfIRmPVNnGuV/u3gm3c
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFVzCCAz+gAwIBAgINAgPlrsWNBCUaqxElqjANBgkqhkiG9w0BAQwFADBHMQsw
CQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEU
MBIGA1UEAxMLR1RTIFJvb3QgUjIwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAw
MDAwWjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZp
Y2VzIExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjIwggIiMA0GCSqGSIb3DQEBAQUA
A4ICDwAwggIKAoICAQDO3v2m++zsFDQ8BwZabFn3GTXd98GdVarTzTukk3LvCvpt
nfbwhYBboUhSnznFt+4orO/LdmgUud+tAWyZH8QiHZ/+cnfgLFuv5AS/T3KgGjSY
6Dlo7JUle3ah5mm5hRm9iYz+re026nO8/4Piy33B0s5Ks40FnotJk9/BW9BuXvAu
MC6C/Pq8tBcKSOWIm8Wba96wyrQD8Nr0kLhlZPdcTK3ofmZemde4wj7I0BOdre7k
RXuJVfeKH2JShBKzwkCX44ofR5GmdFrS+LFjKBC4swm4VndAoiaYecb+3yXuPuWg
f9RhD1FLPD+M2uFwdNjCaKH5wQzpoeJ/u1U8dgbuak7MkogwTZq9TwtImoS1mKPV
+3PBV2HdKFZ1E66HjucMUQkQdYhMvI35ezzUIkgfKtzra7tEscszcTJGr61K8Yzo
dDqs5xoic4DSMPclQsciOzsSrZYuxsN2B6ogtzVJV+mSSeh2FnIxZyuWfoqjx5RW
Ir9qS34BIbIjMt/kmkRtWVtd9QCgHJvGeJeNkP+byKq0rxFROV7Z+2et1VsRnTKa
G73VululycslaVNVJ1zgyjbLiGH7HrfQy+4W+9OmTN6SpdTi3/UGVN4unUu0kzCq
gc7dGtxRcw1PcOnlthYhGXmy5okLdWTK1au8CcEYof/UVKGFPP0UJAOyh9OktwID
AQABo0IwQDAOBgNVHQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4E
FgQUu//KjiOfT5nK2+JopqUVJxce2Q4wDQYJKoZIhvcNAQEMBQADggIBAB/Kzt3H
vqGf2SdMC9wXmBFqiN495nFWcrKeGk6c1SuYJF2ba3uwM4IJvd8lRuqYnrYb/oM8
0mJhwQTtzuDFycgTE1XnqGOtjHsB/ncw4c5omwX4Eu55MaBBRTUoCnGkJE+M3DyC
B19m3H0Q/gxhswWV7uGugQ+o+MePTagjAiZrHYNSVc61LwDKgEDg4XSsYPWHgJ2u
NmSRXbBoGOqKYcl3qJfEycel/FVL8/B/uWU9J2jQzGv6U53hkRrJXRqWbTKH7QMg
yALOWr7Z6v2yTcQvG99fevX4i8buMTolUVVnjWQye+mew4K6Ki3pHrTgSAai/Gev
HyICc/sgCq+dVEuhzf9gR7A/Xe8bVr2XIZYtCtFenTgCR2y59PYjJbigapordwj6
xLEokCZYCDzifqrXPW+6MYgKBesntaFJ7qBFVHvmJ2WZICGoo7z7GJa7Um8M7YNR
TOlZ4iBgxcJlkoKM8xAfDoqXvneCbT+PHV28SSe9zE8P4c52hgQjxcCMElv924Sg
JPFI/2R80L5cFtHvma3AH/vLrrw4IgYmZNralw4/KBVEqE8AyvCazM90arQ+POuV
7LXTWtiBmelDGDfrs7vRWGJB82bSj6p4lVQgw1oudCvV0b4YacCs1aTPObpRhANl
6WLAYv7YTVWW4tAR+kg0Eeye7QUd5MjWHYbL
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICCTCCAY6gAwIBAgINAgPluILrIPglJ209ZjAKBggqhkjOPQQDAzBHMQswCQYD
VQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEUMBIG
A1UEAxMLR1RTIFJvb3QgUjMwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAwMDAw
WjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2Vz
IExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjMwdjAQBgcqhkjOPQIBBgUrgQQAIgNi
AAQfTzOHMymKoYTey8chWEGJ6ladK0uFxh1MJ7x/JlFyb+Kf1qPKzEUURout736G
jOyxfi//qXGdGIRFBEFVbivqJn+7kAHjSxm65FSWRQmx1WyRRK2EE46ajA2ADDL2
4CejQjBAMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQW
BBTB8Sa6oC2uhYHP0/EqEr24Cmf9vDAKBggqhkjOPQQDAwNpADBmAjEA9uEglRR7
VKOQFhG/hMjqb2sXnh5GmCCbn9MN2azTL818+FsuVbu/3ZL3pAzcMeGiAjEA/Jdm
ZuVDFhOD3cffL74UOO0BzrEXGhF16b0DjyZ+hOXJYKaV11RZt+cRLInUue4X
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICCTCCAY6gAwIBAgINAgPlwGjvYxqccpBQUjAKBggqhkjOPQQDAzBHMQswCQYD
VQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2VzIExMQzEUMBIG
A1UEAxMLR1RTIFJvb3QgUjQwHhcNMTYwNjIyMDAwMDAwWhcNMzYwNjIyMDAwMDAw
WjBHMQswCQYDVQQGEwJVUzEiMCAGA1UEChMZR29vZ2xlIFRydXN0IFNlcnZpY2Vz
IExMQzEUMBIGA1UEAxMLR1RTIFJvb3QgUjQwdjAQBgcqhkjOPQIBBgUrgQQAIgNi
AATzdHOnaItgrkO4NcWBMHtLSZ37wWHO5t5GvWvVYRg1rkDdc/eJkTBa6zzuhXyi
QHY7qca4R9gq55KRanPpsXI5nymfopjTX15YhmUPoYRlBtHci8nHc8iMai/lxKvR
HYqjQjBAMA4GA1UdDwEB/wQEAwIBhjAPBgNVHRMBAf8EBTADAQH/MB0GA1UdDgQW
BBSATNbrdP9JNqPV2Py1PsVq8JQdjDAKBggqhkjOPQQDAwNpADBmAjEA6ED/g94D
9J+uHXqnLrmvT/aDHQ4thQEd0dlq7A/Cr8deVl5c1RxYIigL9zC2L7F8AjEA8GE8
p/SgguMh1YQdc4acLa/KNJvxn7kjNuK8YAOdgLOaVsjh4rsUecrNIdSUtUlD
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIB3DCCAYOgAwIBAgINAgPlfvU/k/2lCSGypjAKBggqhkjOPQQDAjBQMSQwIgYD
VQQLExtHbG9iYWxTaWduIEVDQyBSb290IENBIC0gUjQxEzARBgNVBAoTCkdsb2Jh
bFNpZ24xEzARBgNVBAMTCkdsb2JhbFNpZ24wHhcNMTIxMTEzMDAwMDAwWhcNMzgw
MTE5MDMxNDA3WjBQMSQwIgYDVQQLExtHbG9iYWxTaWduIEVDQyBSb290IENBIC0g
UjQxEzARBgNVBAoTCkdsb2JhbFNpZ24xEzARBgNVBAMTCkdsb2JhbFNpZ24wWTAT
BgcqhkjOPQIBBggqhkjOPQMBBwNCAAS4xnnTj2wlDp8uORkcA6SumuU5BwkWymOx
uYb4ilfBV85C+nOh92VC/x7BALJucw7/xyHlGKSq2XE/qNS5zowdo0IwQDAOBgNV
HQ8BAf8EBAMCAYYwDwYDVR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUVLB7rUW44kB/
+wpu+74zyTyjhNUwCgYIKoZIzj0EAwIDRwAwRAIgIk90crlgr/HmnKAWBVBfw147
bmF0774BxL4YSFlhgjICICadVGNA3jdgUM/I2O2dgq43mLyjj0xMqTQrbO/7lZsm
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDljCCAn6gAwIBAgIQC5McOtY5Z+pnI7/Dr5r0SzANBgkqhkiG9w0BAQsFADBl
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSQwIgYDVQQDExtEaWdpQ2VydCBBc3N1cmVkIElEIFJv
b3QgRzIwHhcNMTMwODAxMTIwMDAwWhcNMzgwMTE1MTIwMDAwWjBlMQswCQYDVQQG
EwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNl
cnQuY29tMSQwIgYDVQQDExtEaWdpQ2VydCBBc3N1cmVkIElEIFJvb3QgRzIwggEi
MA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDZ5ygvUj82ckmIkzTz+GoeMVSA
n61UQbVH35ao1K+ALbkKz3X9iaV9JPrjIgwrvJUXCzO/GU1BBpAAvQxNEP4Htecc
biJVMWWXvdMX0h5i89vqbFCMP4QMls+3ywPgym2hFEwbid3tALBSfK+RbLE4E9Hp
EgjAALAcKxHad3A2m67OeYfcgnDmCXRwVWmvo2ifv922ebPynXApVfSr/5Vh88lA
bx3RvpO704gqu52/clpWcTs/1PPRCv4o76Pu2ZmvA9OPYLfykqGxvYmJHzDNw6Yu
YjOuFgJ3RFrngQo8p0Quebg/BLxcoIfhG69Rjs3sLPr4/m3wOnyqi+RnlTGNAgMB
AAGjQjBAMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/BAQDAgGGMB0GA1UdDgQW
BBTOw0q5mVXyuNtgv6l+vVa1lzan1jANBgkqhkiG9w0BAQsFAAOCAQEAyqVVjOPI
QW5pJ6d1Ee88hjZv0p3GeDgdaZaikmkuOGybfQTUiaWxMTeKySHMq2zNixya1r9I
0jJmwYrA8y8678Dj1JGG0VDjA9tzd29KOVPt3ibHtX2vK0LRdWLjSisCx1BL4Gni
lmwORGYQRI+tBev4eaymG+g3NJ1TyWGqolKvSnAWhsI6yLETcDbYz+70CjTVW0z9
B5yiutkBclzzTcHdDrEcDcRjvq30FPuJ7KJBDkzMyFdA0G4Dqs0MjomZmWzwPDCv
ON9vvKO+KSAnq3T/EyJ43pdSVR6DtVQgA+6uwE9W3jfMw3+qBCe703e4YtsXfJwo
IhNzbM8m9Yop5w==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICRjCCAc2gAwIBAgIQC6Fa+h3foLVJRK/NJKBs7DAKBggqhkjOPQQDAzBlMQsw
CQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cu
ZGlnaWNlcnQuY29tMSQwIgYDVQQDExtEaWdpQ2VydCBBc3N1cmVkIElEIFJvb3Qg
RzMwHhcNMTMwODAxMTIwMDAwWhcNMzgwMTE1MTIwMDAwWjBlMQswCQYDVQQGEwJV
UzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNlcnQu
Y29tMSQwIgYDVQQDExtEaWdpQ2VydCBBc3N1cmVkIElEIFJvb3QgRzMwdjAQBgcq
hkjOPQIBBgUrgQQAIgNiAAQZ57ysRGXtzbg/WPuNsVepRC0FFfLvC/8QdJ+1YlJf
Zn4f5dwbRXkLzMZTCp2NXQLZqVneAlr2lSoOjThKiknGvMYDOAdfVdp+CW7if17Q
RSAPWXYQ1qAk8C3eNvJsKTmjQjBAMA8GA1UdEwEB/wQFMAMBAf8wDgYDVR0PAQH/
BAQDAgGGMB0GA1UdDgQWBBTL0L2p4ZgFUaFNN6KDec6NHSrkhDAKBggqhkjOPQQD
AwNnADBkAjAlpIFFAmsSS3V0T8gj43DydXLefInwz5FyYZ5eEJJZVrmDxxDnOOlY
JjZ91eQ0hjkCMHw2U/Aw5WJjOpnitqM7mzT6HtoQknFekROn3aRukswy1vUhZscv
6pZjamVFkpUBtA==
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDjjCCAnagAwIBAgIQAzrx5qcRqaC7KGSxHQn65TANBgkqhkiG9w0BAQsFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH
MjAeFw0xMzA4MDExMjAwMDBaFw0zODAxMTUxMjAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IEcyMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuzfNNNx7a8myaJCtSnX/RrohCgiN9RlUyfuI
2/Ou8jqJkTx65qsGGmvPrC3oXgkkRLpimn7Wo6h+4FR1IAWsULecYxpsMNzaHxmx
1x7e/dfgy5SDN67sH0NO3Xss0r0upS/kqbitOtSZpLYl6ZtrAGCSYP9PIUkY92eQ
q2EGnI/yuum06ZIya7XzV+hdG82MHauVBJVJ8zUtluNJbd134/tJS7SsVQepj5Wz
tCO7TG1F8PapspUwtP1MVYwnSlcUfIKdzXOS0xZKBgyMUNGPHgm+F6HmIcr9g+UQ
vIOlCsRnKPZzFBQ9RnbDhxSJITRNrw9FDKZJobq7nMWxM4MphQIDAQABo0IwQDAP
BgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBhjAdBgNVHQ4EFgQUTiJUIBiV
5uNu5g/6+rkS7QYXjzkwDQYJKoZIhvcNAQELBQADggEBAGBnKJRvDkhj6zHd6mcY
1Yl9PMWLSn/pvtsrF9+wX3N3KjITOYFnQoQj8kVnNeyIv/iPsGEMNKSuIEyExtv4
NeF22d+mQrvHRAiGfzZ0JFrabA0UWTW98kndth/Jsw1HKj2ZL7tcu7XUIOGZX1NG
Fdtom/DzMNU+MeKNhJ7jitralj41E6Vf8PlwUHBHQRFXGU7Aj64GxJUTFy8bJZ91
8rGOmaFvE7FBcf6IKshPECBV1/MUReXgRPTqh5Uykw7+U0b6LJ3/iyK5S9kJRaTe
pLiaWN0bfVKfjllDiIGknibVb63dDcY3fe0Dkhvld1927jyNxF1WW6LZZm6zNTfl
MrY=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICPzCCAcWgAwIBAgIQBVVWvPJepDU1w6QP1atFcjAKBggqhkjOPQQDAzBhMQsw
CQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cu
ZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBHMzAe
Fw0xMzA4MDExMjAwMDBaFw0zODAxMTUxMjAwMDBaMGExCzAJBgNVBAYTAlVTMRUw
EwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5jb20x
IDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IEczMHYwEAYHKoZIzj0CAQYF
K4EEACIDYgAE3afZu4q4C/sLfyHS8L6+c/MzXRq8NOrexpu80JX28MzQC7phW1FG
fp4tn+6OYwwX7Adw9c+ELkCDnOg/QW07rdOkFFk2eJ0DQ+4QE2xy3q6Ip6FrtUPO
Z9wj/wMco+I+o0IwQDAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBhjAd
BgNVHQ4EFgQUs9tIpPmhxdiuNkHMEWNpYim8S8YwCgYIKoZIzj0EAwMDaAAwZQIx
AK288mw/EkrRLTnDCgmXc/SINoyIJ7vmiI1Qhadj+Z4y3maTD/HMsQmP3Wyr+mt/
oAIwOWZbwmSNuJ5Q3KjVSaLtx9zRSX8XAbjIho9OjIgrqJqpisXRAL34VOKa5Vt8
sycX
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFkDCCA3igAwIBAgIQBZsbV56OITLiOQe9p3d1XDANBgkqhkiG9w0BAQwFADBi
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSEwHwYDVQQDExhEaWdpQ2VydCBUcnVzdGVkIFJvb3Qg
RzQwHhcNMTMwODAxMTIwMDAwWhcNMzgwMTE1MTIwMDAwWjBiMQswCQYDVQQGEwJV
UzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3d3cuZGlnaWNlcnQu
Y29tMSEwHwYDVQQDExhEaWdpQ2VydCBUcnVzdGVkIFJvb3QgRzQwggIiMA0GCSqG
SIb3DQEBAQUAA4ICDwAwggIKAoICAQC/5pBzaN675F1KPDAiMGkz7MKnJS7JIT3y
ithZwuEppz1Yq3aaza57G4QNxDAf8xukOBbrVsaXbR2rsnnyyhHS5F/WBTxSD1If
xp4VpX6+n6lXFllVcq9ok3DCsrp1mWpzMpTREEQQLt+C8weE5nQ7bXHiLQwb7iDV
ySAdYyktzuxeTsiT+CFhmzTrBcZe7FsavOvJz82sNEBfsXpm7nfISKhmV1efVFiO
DCu3T6cw2Vbuyntd463JT17lNecxy9qTXtyOj4DatpGYQJB5w3jHtrHEtWoYOAMQ
jdjUN6QuBX2I9YI+EJFwq1WCQTLX2wRzKm6RAXwhTNS8rhsDdV14Ztk6MUSaM0C/
CNdaSaTC5qmgZ92kJ7yhTzm1EVgX9yRcRo9k98FpiHaYdj1ZXUJ2h4mXaXpI8OCi
EhtmmnTK3kse5w5jrubU75KSOp493ADkRSWJtppEGSt+wJS00mFt6zPZxd9LBADM
fRyVw4/3IbKyEbe7f/LVjHAsQWCqsWMYRJUadmJ+9oCw++hkpjPRiQfhvbfmQ6QY
uKZ3AeEPlAwhHbJUKSWJbOUOUlFHdL4mrLZBdd56rF+NP8m800ERElvlEFDrMcXK
chYiCd98THU/Y+whX8QgUWtvsauGi0/C1kVfnSD8oR7FwI+isX4KJpn15GkvmB0t
9dmpsh3lGwIDAQABo0IwQDAPBgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIB
hjAdBgNVHQ4EFgQU7NfjgtJxXWRM3y5nP+e6mK4cD08wDQYJKoZIhvcNAQEMBQAD
ggIBALth2X2pbL4XxJEbw6GiAI3jZGgPVs93rnD5/ZpKmbnJeFwMDF/k5hQpVgs2
SV1EY+CtnJYYZhsjDT156W1r1lT40jzBQ0CuHVD1UvyQO7uYmWlrx8GnqGikJ9yd
+SeuMIW59mdNOj6PWTkiU0TryF0Dyu1Qen1iIQqAyHNm0aAFYF/opbSnr6j3bTWc
fFqK1qI4mfN4i/RN0iAL3gTujJtHgXINwBQy7zBZLq7gcfJW5GqXb5JQbZaNaHqa
sjYUegbyJLkJEVDXCLG4iXqEI2FCKeWjzaIgQdfRnGTZ6iahixTXTBmyUEFxPT9N
cCOGDErcgdLMMpSEDQgJlxxPwO5rIHQw0uA5NBCFIRUBCOhVMt5xSdkoF1BN5r5N
0XWs0Mr7QbhDparTwwVETyw2m+L64kW4I1NsBm9nVX9GtUw/bihaeSbSpKhil9Ie
4u1Ki7wb/UdKDd9nZn6yW0HQO+T0O/QEY+nvwlQAUaCKKsnOeMzV6ocEGLPOr0mI
r/OSmbaz5mEP0oUA51Aa5BuVnRmhuZyxm7EAHu/QD09CbMkKvO5D+jpxpchNJqU1
/YldvIViHTLSoCtU7ZpXwdv6EM8Zt4tKG48BtieVU+i2iW1bvGjUI+iLUaJW+fCm
gKDWHrO8Dw9TdSmq6hN35N6MgSGtBxBHEa2HPQfRdbzP82Z+
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDXzCCAkegAwIBAgILBAAAAAABIVhTCKIwDQYJKoZIhvcNAQELBQAwTDEgMB4G
A1UECxMXR2xvYmFsU2lnbiBSb290IENBIC0gUjMxEzARBgNVBAoTCkdsb2JhbFNp
Z24xEzARBgNVBAMTCkdsb2JhbFNpZ24wHhcNMDkwMzE4MTAwMDAwWhcNMjkwMzE4
MTAwMDAwWjBMMSAwHgYDVQQLExdHbG9iYWxTaWduIFJvb3QgQ0EgLSBSMzETMBEG
A1UEChMKR2xvYmFsU2lnbjETMBEGA1UEAxMKR2xvYmFsU2lnbjCCASIwDQYJKoZI
hvcNAQEBBQADggEPADCCAQoCggEBAMwldpB5BngiFvXAg7aEyiie/QV2EcWtiHL8
RgJDx7KKnQRfJMsuS+FggkbhUqsMgUdwbN1k0ev1LKMPgj0MK66X17YUhhB5uzsT
gHeMCOFJ0mpiLx9e+pZo34knlTifBtc+ycsmWQ1z3rDI6SYOgxXG71uL0gRgykmm
KPZpO/bLyCiR5Z2KYVc3rHQU3HTgOu5yLy6c+9C7v/U9AOEGM+iCK65TpjoWc4zd
QQ4gOsC0p6Hpsk+QLjJg6VfLuQSSaGjlOCZgdbKfd/+RFO+uIEn8rUAVSNECMWEZ
XriX7613t2Saer9fwRPvm2L7DWzgVGkWqQPabumDk3F2xmmFghcCAwEAAaNCMEAw
DgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB/wQFMAMBAf8wHQYDVR0OBBYEFI/wS3+o
LkUkrk1Q+mOai97i3Ru8MA0GCSqGSIb3DQEBCwUAA4IBAQBLQNvAUKr+yAzv95ZU
RUm7lgAJQayzE4aGKAczymvmdLm6AC2upArT9fHxD4q/c2dKg8dEe3jgr25sbwMp
jjM5RcOO5LlXbKr8EpbsU8Yt5CRsuZRj+9xTaGdWPoO4zzUhw8lo/s7awlOqzJCK
6fBdRoyV3XpYKBovHd7NADdBj+1EbddTKJd+82cEHhXXipa0095MJ6RMG3NzdvQX
mcIfeg7jLQitChws/zyrVQ4PkX4268NXSb7hLi18YIvDQVETI53O9zJrlAGomecs
Mx86OyXShkDOOyyGeMlhLxS67ttVb9+E7gUJTb0o2HLO02JQZR7rkpeDMdmztcpH
WD9f
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICHjCCAaSgAwIBAgIRYFlJ4CYuu1X5CneKcflK2GwwCgYIKoZIzj0EAwMwUDEk
MCIGA1UECxMbR2xvYmFsU2lnbiBFQ0MgUm9vdCBDQSAtIFI1MRMwEQYDVQQKEwpH
bG9iYWxTaWduMRMwEQYDVQQDEwpHbG9iYWxTaWduMB4XDTEyMTExMzAwMDAwMFoX
DTM4MDExOTAzMTQwN1owUDEkMCIGA1UECxMbR2xvYmFsU2lnbiBFQ0MgUm9vdCBD
QSAtIFI1MRMwEQYDVQQKEwpHbG9iYWxTaWduMRMwEQYDVQQDEwpHbG9iYWxTaWdu
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAER0UOlvt9Xb/pOdEh+J8LttV7HpI6SFkc
8GIxLcB6KP4ap1yztsyX50XUWPrRd21DosCHZTQKH3rd6zwzocWdTaRvQZU4f8ke
hOvRnkmSh5SHDDqFSmafnVmTTZdhBoZKo0IwQDAOBgNVHQ8BAf8EBAMCAQYwDwYD
VR0TAQH/BAUwAwEB/zAdBgNVHQ4EFgQUPeYpSJvqB8ohREom3m7e0oPQn1kwCgYI
KoZIzj0EAwMDaAAwZQIxAOVpEslu28YxuglB4Zf4+/2a4n0Sye18ZNPLBSWLVtmg
515dTguDnFt2KaAJJiFqYgIwcdK1j1zqO+F4CYWodZI7yFz9SO8NdCKoCOJuxUnO
xwy8p2Fp8fc74SrL+SvzZpA3
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFgzCCA2ugAwIBAgIORea7A4Mzw4VlSOb/RVEwDQYJKoZIhvcNAQEMBQAwTDEg
MB4GA1UECxMXR2xvYmFsU2lnbiBSb290IENBIC0gUjYxEzARBgNVBAoTCkdsb2Jh
bFNpZ24xEzARBgNVBAMTCkdsb2JhbFNpZ24wHhcNMTQxMjEwMDAwMDAwWhcNMzQx
MjEwMDAwMDAwWjBMMSAwHgYDVQQLExdHbG9iYWxTaWduIFJvb3QgQ0EgLSBSNjET
MBEGA1UEChMKR2xvYmFsU2lnbjETMBEGA1UEAxMKR2xvYmFsU2lnbjCCAiIwDQYJ
KoZIhvcNAQEBBQADggIPADCCAgoCggIBAJUH6HPKZvnsFMp7PPcNCPG0RQssgrRI
xutbPK6DuEGSMxSkb3/pKszGsIhrxbaJ0cay/xTOURQh7ErdG1rG1ofuTToVBu1k
ZguSgMpE3nOUTvOniX9PeGMIyBJQbUJmL025eShNUhqKGoC3GYEOfsSKvGRMIRxD
aNc9PIrFsmbVkJq3MQbFvuJtMgamHvm566qjuL++gmNQ0PAYid/kD3n16qIfKtJw
LnvnvJO7bVPiSHyMEAc4/2ayd2F+4OqMPKq0pPbzlUoSB239jLKJz9CgYXfIWHSw
1CM69106yqLbnQneXUQtkPGBzVeS+n68UARjNN9rkxi+azayOeSsJDa38O+2HBNX
k7besvjihbdzorg1qkXy4J02oW9UivFyVm4uiMVRQkQVlO6jxTiWm05OWgtH8wY2
SXcwvHE35absIQh1/OZhFj931dmRl4QKbNQCTXTAFO39OfuD8l4UoQSwC+n+7o/h
bguyCLNhZglqsQY6ZZZZwPA1/cnaKI0aEYdwgQqomnUdnjqGBQCe24DWJfncBZ4n
WUx2OVvq+aWh2IMP0f/fMBH5hc8zSPXKbWQULHpYT9NLCEnFlWQaYw55PfWzjMpY
rZxCRXluDocZXFSxZba/jJvcE+kNb7gu3GduyYsRtYQUigAZcIN5kZeR1Bonvzce
MgfYFGM8KEyvAgMBAAGjYzBhMA4GA1UdDwEB/wQEAwIBBjAPBgNVHRMBAf8EBTAD
AQH/MB0GA1UdDgQWBBSubAWjkxPioufi1xzWx/B/yGdToDAfBgNVHSMEGDAWgBSu
bAWjkxPioufi1xzWx/B/yGdToDANBgkqhkiG9w0BAQwFAAOCAgEAgyXt6NH9lVLN
nsAEoJFp5lzQhN7craJP6Ed41mWYqVuoPId8AorRbrcWc+ZfwFSY1XS+wc3iEZGt
Ixg93eFyRJa0lV7Ae46ZeBZDE1ZXs6KzO7V33EByrKPrmzU+sQghoefEQzd5Mr61
55wsTLxDKZmOMNOsIeDjHfrYBzN2VAAiKrlNIC5waNrlU/yDXNOd8v9EDERm8tLj
vUYAGm0CuiVdjaExUd1URhxN25mW7xocBFymFe944Hn+Xds+qkxV/ZoVqW/hpvvf
cDDpw+5CRu3CkwWJ+n1jez/QcYF8AOiYrg54NMMl+68KnyBr3TsTjxKM4kEaSHpz
oHdpx7Zcf4LIHv5YGygrqGytXm3ABdJ7t+uA/iU3/gKbaKxCXcPu9czc8FB10jZp
nOZ7BN9uBmm23goJSFmH63sUYHpkqmlD75HHTOwY3WzvUy2MmeFe8nI+z1TIvWfs
pA9MRf/TuTAjB0yPEL+GltmZWrSZVxykzLsViVO6LAUP5MSeGbEYNNVMnbrt9x+v
JJUEeKgDu+6B5dpffItKoZB0JaezPkvILFa9x8jvOOJckvB595yEunQtYQEgfn7R
8k8HWV+LLUNS60YMlOH1Zkd5d9VUWx+tJDfLRVpOoERIyNiwmcUVhAn21klJwGW4
5hpxbqCo8YLoRT5s1gLXCmeDBVrJpBA=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIDxTCCAq2gAwIBAgIBADANBgkqhkiG9w0BAQsFADCBgzELMAkGA1UEBhMCVVMx
EDAOBgNVBAgTB0FyaXpvbmExEzARBgNVBAcTClNjb3R0c2RhbGUxGjAYBgNVBAoT
EUdvRGFkZHkuY29tLCBJbmMuMTEwLwYDVQQDEyhHbyBEYWRkeSBSb290IENlcnRp
ZmljYXRlIEF1dGhvcml0eSAtIEcyMB4XDTA5MDkwMTAwMDAwMFoXDTM3MTIzMTIz
NTk1OVowgYMxCzAJBgNVBAYTAlVTMRAwDgYDVQQIEwdBcml6b25hMRMwEQYDVQQH
EwpTY290dHNkYWxlMRowGAYDVQQKExFHb0RhZGR5LmNvbSwgSW5jLjExMC8GA1UE
AxMoR28gRGFkZHkgUm9vdCBDZXJ0aWZpY2F0ZSBBdXRob3JpdHkgLSBHMjCCASIw
DQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBAL9xYgjx+lk09xvJGKP3gElY6SKD
E6bFIEMBO4Tx5oVJnyfq9oQbTqC023CYxzIBsQU+B07u9PpPL1kwIuerGVZr4oAH
/PMWdYA5UXvl+TW2dE6pjYIT5LY/qQOD+qK+ihVqf94Lw7YZFAXK6sOoBJQ7Rnwy
DfMAZiLIjWltNowRGLfTshxgtDj6AozO091GB94KPutdfMh8+7ArU6SSYmlRJQVh
GkSBjCypQ5Yj36w6gZoOKcUcqeldHraenjAKOc7xiID7S13MMuyFYkMlNAJWJwGR
tDtwKj9useiciAF9n9T521NtYJ2/LOdYq7hfRvzOxBsDPAnrSTFcaUaz4EcCAwEA
AaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYE
FDqahQcQZyi27/a9BUFuIMGU2g/eMA0GCSqGSIb3DQEBCwUAA4IBAQCZ21151fmX
WWcDYfF+OwYxdS2hII5PZYe096acvNjpL9DbWu7PdIxztDhC2gV7+AJ1uP2lsdeu
9tfeE8tTEH6KRtGX+rcuKxGrkLAngPnon1rpN5+r5N9ss4UXnT3ZJE95kTXWXwTr
gIOrmgIttRD02JDHBHNA7XIloKmf7J6raBKZV8aPEjoJpL1E/QYVN8Gb5DKj7Tjo
2GTzLH4U/ALqn83/B2gX2yKQOC16jdFU8WnjXzPKej17CuPKf1855eJ1usV2GDPO
LPAvTK33sefOT6jEm0pUBsV/fdUID+Ic/n4XuKxe9tQWskMJDE32p2u0mYRlynqI
4uJEvlz36hz1
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIID3TCCAsWgAwIBAgIBADANBgkqhkiG9w0BAQsFADCBjzELMAkGA1UEBhMCVVMx
EDAOBgNVBAgTB0FyaXpvbmExEzARBgNVBAcTClNjb3R0c2RhbGUxJTAjBgNVBAoT
HFN0YXJmaWVsZCBUZWNobm9sb2dpZXMsIEluYy4xMjAwBgNVBAMTKVN0YXJmaWVs
ZCBSb290IENlcnRpZmljYXRlIEF1dGhvcml0eSAtIEcyMB4XDTA5MDkwMTAwMDAw
MFoXDTM3MTIzMTIzNTk1OVowgY8xCzAJBgNVBAYTAlVTMRAwDgYDVQQIEwdBcml6
b25hMRMwEQYDVQQHEwpTY290dHNkYWxlMSUwIwYDVQQKExxTdGFyZmllbGQgVGVj
aG5vbG9naWVzLCBJbmMuMTIwMAYDVQQDEylTdGFyZmllbGQgUm9vdCBDZXJ0aWZp
Y2F0ZSBBdXRob3JpdHkgLSBHMjCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoC
ggEBAL3twQP89o/8ArFvW59I2Z154qK3A2FWGMNHttfKPTUuiUP3oWmb3ooa/RMg
nLRJdzIpVv257IzdIvpy3Cdhl+72WoTsbhm5iSzchFvVdPtrX8WJpRBSiUZV9Lh1
HOZ/5FSuS/hVclcCGfgXcVnrHigHdMWdSL5stPSksPNkN3mSwOxGXn/hbVNMYq/N
Hwtjuzqd+/x5AJhhdM8mgkBj87JyahkNmcrUDnXMN/uLicFZ8WJ/X7NfZTD4p7dN
dloedl40wOiWVpmKs/B/pM293DIxfJHP4F8R+GuqSVzRmZTRouNjWwl2tVZi4Ut0
HZbUJtQIBFnQmA4O5t78w+wfkPECAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAO
BgNVHQ8BAf8EBAMCAQYwHQYDVR0OBBYEFHwMMh+n2TB/xH1oo2Kooc6rB1snMA0G
CSqGSIb3DQEBCwUAA4IBAQARWfolTwNvlJk7mh+ChTnUdgWUXuEok21iXQnCoKjU
sHU48TRqneSfioYmUeYs0cYtbpUgSpIB7LiKZ3sx4mcujJUDJi5DnUox9g61DLu3
4jd/IroAow57UvtruzvE03lRTs2Q9GcHGcg8RnoNAX3FWOdt5oUwF5okxBDgBPfg
8n/Uqgr/Qh037ZTlZFkSIHc40zI+OIF1lnP6aI+xy84fxez6nH7PfrHxBy22/L/K
pL/QlwVKvOoYKAKQvVR4CSFx09F9HdkWsKlhPdAKACL8x3vLCWRFCztAgfd9fDL1
mMpYjn0q7pBZc2T5NnReJaH1ZgUufzkVqSr7UIuOhWn0
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICiTCCAg+gAwIBAgIQH0evqmIAcFBUTAGem2OZKjAKBggqhkjOPQQDAzCBhTEL
MAkGA1UEBhMCR0IxGzAZBgNVBAgTEkdyZWF0ZXIgTWFuY2hlc3RlcjEQMA4GA1UE
BxMHU2FsZm9yZDEaMBgGA1UEChMRQ09NT0RPIENBIExpbWl0ZWQxKzApBgNVBAMT
IkNPTU9ETyBFQ0MgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMDgwMzA2MDAw
MDAwWhcNMzgwMTE4MjM1OTU5WjCBhTELMAkGA1UEBhMCR0IxGzAZBgNVBAgTEkdy
ZWF0ZXIgTWFuY2hlc3RlcjEQMA4GA1UEBxMHU2FsZm9yZDEaMBgGA1UEChMRQ09N
T0RPIENBIExpbWl0ZWQxKzApBgNVBAMTIkNPTU9ETyBFQ0MgQ2VydGlmaWNhdGlv
biBBdXRob3JpdHkwdjAQBgcqhkjOPQIBBgUrgQQAIgNiAAQDR3svdcmCFYX7deSR
FtSrYpn1PlILBs5BAH+X4QokPB0BBO490o0JlwzgdeT6+3eKKvUDYEs2ixYjFq0J
cfRK9ChQtP6IHG4/bC8vCVlbpVsLM5niwz2J+Wos77LTBumjQjBAMB0GA1UdDgQW
BBR1cacZSBm8nZ3qQUfflMRId5nTeTAOBgNVHQ8BAf8EBAMCAQYwDwYDVR0TAQH/
BAUwAwEB/zAKBggqhkjOPQQDAwNoADBlAjEA7wNbeqy3eApyt4jf/7VGFAkK+qDm
fQjGGoe9GKhzvSbKYAydzpmfz1wPMOG+FDHqAjAU9JM8SaczepBGR7NjfRObTrdv
GDeAU/7dIOA1mjbRxwG55tzd8/8dLDoWV9mSOdY=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIF2DCCA8CgAwIBAgIQTKr5yttjb+Af907YWwOGnTANBgkqhkiG9w0BAQwFADCB
hTELMAkGA1UEBhMCR0IxGzAZBgNVBAgTEkdyZWF0ZXIgTWFuY2hlc3RlcjEQMA4G
A1UEBxMHU2FsZm9yZDEaMBgGA1UEChMRQ09NT0RPIENBIExpbWl0ZWQxKzApBgNV
BAMTIkNPTU9ETyBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTAwMTE5
MDAwMDAwWhcNMzgwMTE4MjM1OTU5WjCBhTELMAkGA1UEBhMCR0IxGzAZBgNVBAgT
EkdyZWF0ZXIgTWFuY2hlc3RlcjEQMA4GA1UEBxMHU2FsZm9yZDEaMBgGA1UEChMR
Q09NT0RPIENBIExpbWl0ZWQxKzApBgNVBAMTIkNPTU9ETyBSU0EgQ2VydGlmaWNh
dGlvbiBBdXRob3JpdHkwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIKAoICAQCR
6FSS0gpWsawNJN3Fz0RndJkrN6N9I3AAcbxT38T6KhKPS38QVr2fcHK3YX/JSw8X
pz3jsARh7v8Rl8f0hj4K+j5c+ZPmNHrZFGvnnLOFoIJ6dq9xkNfs/Q36nGz637CC
9BR++b7Epi9Pf5l/tfxnQ3K9DADWietrLNPtj5gcFKt+5eNu/Nio5JIk2kNrYrhV
/erBvGy2i/MOjZrkm2xpmfh4SDBF1a3hDTxFYPwyllEnvGfDyi62a+pGx8cgoLEf
Zd5ICLqkTqnyg0Y3hOvozIFIQ2dOciqbXL1MGyiKXCJ7tKuY2e7gUYPDCUZObT6Z
+pUX2nwzV0E8jVHtC7ZcryxjGt9XyD+86V3Em69FmeKjWiS0uqlWPc9vqv9JWL7w
qP/0uK3pN/u6uPQLOvnoQ0IeidiEyxPx2bvhiWC4jChWrBQdnArncevPDt09qZah
SL0896+1DSJMwBGB7FY79tOi4lu3sgQiUpWAk2nojkxl8ZEDLXB0AuqLZxUpaVIC
u9ffUGpVRr+goyhhf3DQw6KqLCGqR84onAZFdr+CGCe01a60y1Dma/RMhnEw6abf
Fobg2P9A3fvQQoh/ozM6LlweQRGBY84YcWsr7KaKtzFcOmpH4MN5WdYgGq/yapiq
crxXStJLnbsQ/LBMQeXtHT1eKJ2czL+zUdqnR+WEUwIDAQABo0IwQDAdBgNVHQ4E
FgQUu69+Aj36pvE8hI6t7jiY7NkyMtQwDgYDVR0PAQH/BAQDAgEGMA8GA1UdEwEB
/wQFMAMBAf8wDQYJKoZIhvcNAQEMBQADggIBAArx1UaEt65Ru2yyTUEUAJNMnMvl
wFTPoCWOAvn9sKIN9SCYPBMtrFaisNZ+EZLpLrqeLppysb0ZRGxhNaKatBYSaVqM
4dc+pBroLwP0rmEdEBsqpIt6xf4FpuHA1sj+nq6PK7o9mfjYcwlYRm6mnPTXJ9OV
2jeDchzTc+CiR5kDOF3VSXkAKRzH7JsgHAckaVd4sjn8OoSgtZx8jb8uk2Intzna
FxiuvTwJaP+EmzzV1gsD41eeFPfR60/IvYcjt7ZJQ3mFXLrrkguhxuhoqEwWsRqZ
CuhTLJK7oQkYdQxlqHvLI7cawiiFwxv/0Cti76R7CZGYZ4wUAc1oBmpjIXUDgIiK
boHGhfKppC3n9KUkEEeDys30jXlYsQab5xoq2Z0B15R97QNKyvDb6KkBPvVWmcke
jkk9u+UJueBPSZI9FoJAzMxZxuY67RIuaTxslbH9qh17f4a+Hg4yRvv7E491f0yL
S0Zj/gA0QHDBw7mh3aZw4gSzQbzpgJHqZJx64SIDqZxubw5lT2yHh17zbqD5daWb
QOhTsiedSrnAdyGN/4fy3ryM7xfft0kL0fJuMAsaDk527RH89elWsn2/x20Kk4yl
0MC2Hb46TpSi125sC8KKfPog88Tk5c0NqMuRkrF8hey1FGlmDoLnzc7ILaZRfyHB
NVOFBkpdn627G190
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICjzCCAhWgAwIBAgIQXIuZxVqUxdJxVt7NiYDMJjAKBggqhkjOPQQDAzCBiDEL
MAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNl
eSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMT
JVVTRVJUcnVzdCBFQ0MgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTAwMjAx
MDAwMDAwWhcNMzgwMTE4MjM1OTU5WjCBiDELMAkGA1UEBhMCVVMxEzARBgNVBAgT
Ck5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVUaGUg
VVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMTJVVTRVJUcnVzdCBFQ0MgQ2VydGlm
aWNhdGlvbiBBdXRob3JpdHkwdjAQBgcqhkjOPQIBBgUrgQQAIgNiAAQarFRaqflo
I+d61SRvU8Za2EurxtW20eZzca7dnNYMYf3boIkDuAUU7FfO7l0/4iGzzvfUinng
o4N+LZfQYcTxmdwlkWOrfzCjtHDix6EznPO/LlxTsV+zfTJ/ijTjeXmjQjBAMB0G
A1UdDgQWBBQ64QmG1M8ZwpZ2dEl23OA1xmNjmjAOBgNVHQ8BAf8EBAMCAQYwDwYD
VR0TAQH/BAUwAwEB/zAKBggqhkjOPQQDAwNoADBlAjA2Z6EWCNzklwBBHU6+4WMB
zzuqQhFkoJ2UOQIReVx7Hfpkue4WQrO/isIJxOzksU0CMQDpKmFHjFJKS04YcPbW
RNZu9YO6bVi9JNlWSOrvxKJGgYhqOkbRqZtNyWHa0V1Xahg=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIF3jCCA8agAwIBAgIQAf1tMPyjylGoG7xkDjUDLTANBgkqhkiG9w0BAQwFADCB
iDELMAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0pl
cnNleSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNV
BAMTJVVTRVJUcnVzdCBSU0EgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTAw
MjAxMDAwMDAwWhcNMzgwMTE4MjM1OTU5WjCBiDELMAkGA1UEBhMCVVMxEzARBgNV
BAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVU
aGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMTJVVTRVJUcnVzdCBSU0EgQ2Vy
dGlmaWNhdGlvbiBBdXRob3JpdHkwggIiMA0GCSqGSIb3DQEBAQUAA4ICDwAwggIK
AoICAQCAEmUXNg7D2wiz0KxXDXbtzSfTTK1Qg2HiqiBNCS1kCdzOiZ/MPans9s/B
3PHTsdZ7NygRK0faOca8Ohm0X6a9fZ2jY0K2dvKpOyuR+OJv0OwWIJAJPuLodMkY
tJHUYmTbf6MG8YgYapAiPLz+E/CHFHv25B+O1ORRxhFnRghRy4YUVD+8M/5+bJz/
Fp0YvVGONaanZshyZ9shZrHUm3gDwFA66Mzw3LyeTP6vBZY1H1dat//O+T23LLb2
VN3I5xI6Ta5MirdcmrS3ID3KfyI0rn47aGYBROcBTkZTmzNg95S+UzeQc0PzMsNT
79uq/nROacdrjGCT3sTHDN/hMq7MkztReJVni+49Vv4M0GkPGw/zJSZrM233bkf6
c0Plfg6lZrEpfDKEY1WJxA3Bk1QwGROs0303p+tdOmw1XNtB1xLaqUkL39iAigmT
Yo61Zs8liM2EuLE/pDkP2QKe6xJMlXzzawWpXhaDzLhn4ugTncxbgtNMs+1b/97l
c6wjOy0AvzVVdAlJ2ElYGn+SNuZRkg7zJn0cTRe8yexDJtC/QV9AqURE9JnnV4ee
UB9XVKg+/XRjL7FQZQnmWEIuQxpMtPAlR1n6BB6T1CZGSlCBst6+eLf8ZxXhyVeE
Hg9j1uliutZfVS7qXMYoCAQlObgOK6nyTJccBz8NUvXt7y+CDwIDAQABo0IwQDAd
BgNVHQ4EFgQUU3m/WqorSs9UgOHYm8Cd8rIDZsswDgYDVR0PAQH/BAQDAgEGMA8G
A1UdEwEB/wQFMAMBAf8wDQYJKoZIhvcNAQEMBQADggIBAFzUfA3P9wF9QZllDHPF
Up/L+M+ZBn8b2kMVn54CVVeWFPFSPCeHlCjtHzoBN6J2/FNQwISbxmtOuowhT6KO
VWKR82kV2LyI48SqC/3vqOlLVSoGIG1VeCkZ7l8wXEskEVX/JJpuXior7gtNn3/3
ATiUFJVDBwn7YKnuHKsSjKCaXqeYalltiz8I+8jRRa8YFWSQEg9zKC7F4iRO/Fjs
8PRF/iKz6y+O0tlFYQXBl2+odnKPi4w2r78NBc5xjeambx9spnFixdjQg3IM8WcR
iQycE0xyNN+81XHfqnHd4blsjDwSXWXavVcStkNr/+XeTWYRUc+ZruwXtuhxkYze
Sf7dNXGiFSeUHM9h4ya7b6NnJSFd5t0dCy5oGzuCr+yDZ4XUmFF0sbmZgIn/f3gZ
XHlKYC6SQK5MNyosycdiyA5d9zZbyuAlJQG03RoHnHcAP9Dc1ew91Pq7P8yF1m9/
qS3fuQL39ZeatTXaw2ewh0qpKJ4jjv9cJ2vhsE/zB+4ALtRZh8tSQZXq9EfX7mRB
VXyNWQKV3WKdwrnuWih0hKWbt5DHDAff9Yk2dDLWKMGwsAvgnEzDHNb842m1R0aB
L6KCq9NjRHDEjf8tM7qtj3u1cIiuPhnPQCjY/MiQu12ZIvVS5ljFH4gxQ+6IHdfG
jjxDah2nGN59PRbxYvnKkKj9
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIIFjzCCA3egAwIBAgIQdq/uiJMVRbZQU5uAnKTfmjANBgkqhkiG9w0BAQsFADBR
MQswCQYDVQQGEwJVUzEYMBYGA1UECgwPU1NMIENvcnBvcmF0aW9uMSgwJgYDVQQD
DB9TU0wuY29tIENsaWVudCBSU0EgUm9vdCBDQSAyMDIyMB4XDTIyMDgyNTE2MzEw
N1oXDTQ2MDgxOTE2MzEwNlowUTELMAkGA1UEBhMCVVMxGDAWBgNVBAoMD1NTTCBD
b3Jwb3JhdGlvbjEoMCYGA1UEAwwfU1NMLmNvbSBDbGllbnQgUlNBIFJvb3QgQ0Eg
MjAyMjCCAiIwDQYJKoZIhvcNAQEBBQADggIPADCCAgoCggIBALhY20Yw+8k/48jw
ATM04tpIqBjpIG6a1wHh1SmPMLQjauTLYrC+4p8gvT5UoDlox4Y3ZnQGBu90K9rc
n4SpUi+Q0u5+fPulIq1vcEZnlj0p1KO7VnsUBFnBIWNEHrIfElyQh2UNiPYeiCLi
Y1S78zb41n/c2v8pNanGbg5pWz/YvoKHFXBdsMdcEg9jpjjNz3O5ww6JJjcbP2Ic
MmnRm9n/VZAx3rFj3c/FdHf874ghU78AMRomLAAwpV9s4+T2AIrKmIecdAN6i2bs
fv2jjzUlXHils6T7PW2pivBsiIKL/UrQb+TXo7SONEk4vs5F5dIcyl7CNxSLzWZW
Mzed5WvsQ5JkoELadW/AFez5ab00uYp7+hb7Vf5SIOgEBFZWZfU3RJjIikbpt6y4
6L5ijlQ2W/c7cL9d7i26X95CGYbwf4vrCMvYvuoOQkKgNnNXF+0y6tCN6Acbm5no
xJpiBA5I9zwSuvdYwZqM6cewIzZWNB3LbNq6B4Qd/dGsn+bCie/DuWwYs2mHV1+1
DDhbpyEkKjunNJGetFTqKE/TwaOL5OYr1fKdv5thACLd1ktEHz9dVv7enHjMmVuq
5L2620NLrUwmTKNNNIpsdDYT22L8m7IFgf+uPwzN9hui9DnnyvVMXPtUdzWAWsAS
oRMBM2c9nYGhqfWFJFiIeOf042hVAgMBAAGjYzBhMA8GA1UdEwEB/wQFMAMBAf8w
HwYDVR0jBBgwFoAU8DhClDSpPAB/Uu45pfdLDbxqfSMwHQYDVR0OBBYEFPA4QpQ0
qTwAf1LuOaX3Sw28an0jMA4GA1UdDwEB/wQEAwIBhjANBgkqhkiG9w0BAQsFAAOC
AgEAmU/b8OrWEfoq/cirbeQOc2LSQp8V/nxwUj9kh4IxP0VALuEinwZmKfyW0y2N
tjjH2fMnwVkpoIz2cyQPKCLXTmHdE93bnzJSk/tPzOo4PJhqA6sWryHRQq59RSvq
xM+KWZ+CcHY6+GImyRCXWEAkpC25LymAJ+GJa3LKSQhxN1MF8YDO00IC0vzC0ZQG
7gfi9oPif5/nu1bDW7/dlZMJHiTBzybNraSuwrRp56q17TeU6d3RY4VrmnpKVnbc
GYUo1OTGpNi4lkF30LRZ8UYFh4cCH2m5ghjQQ9km2hpnqNZ1durybQ5C/4gmom6E
/n5iG/DGPe3AHGrHkda4ADdJm7mEBaHNbjHWROpTi7pTmB2hkIrphfgb8pNYw8jc
miZPPiDPT0PzEIx/EGF6NsqqC33Mn0dEWa6llcaZU+MHaz1JELAY/10OhUMUS+dr
00q1smBh3GlJAiNd6JJxw5yfRWd5HtwyhrqqVTxkbzK1EEAV3nJAeOBucLtu6wno
OdmsupJ13UPKugGVrRqBKzrw48UvDBhNEMauwO3+BVJ/GQXLqa81CAw4IuT+VuVT
Pr/k1rPZCMM91TMygSTFqeFlEbgyMzBxGEkdGkXGmhSKWDkobvPLUblJJmR4A8eR
EYOpuZA0tm+qBZ6FKFeZvn8nBkliTaH8CeErRglMFJtWj0U=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE-----
MIICQDCCAcagAwIBAgIQdvhIHq7wPHAf4D8lVAGD1TAKBggqhkjOPQQDAzBRMQsw
CQYDVQQGEwJVUzEYMBYGA1UECgwPU1NMIENvcnBvcmF0aW9uMSgwJgYDVQQDDB9T
U0wuY29tIENsaWVudCBFQ0MgUm9vdCBDQSAyMDIyMB4XDTIyMDgyNTE2MzAzMloX
DTQ2MDgxOTE2MzAzMVowUTELMAkGA1UEBhMCVVMxGDAWBgNVBAoMD1NTTCBDb3Jw
b3JhdGlvbjEoMCYGA1UEAwwfU1NMLmNvbSBDbGllbnQgRUNDIFJvb3QgQ0EgMjAy
MjB2MBAGByqGSM49AgEGBSuBBAAiA2IABC1Tfp+LPrM2ulDizOvcuiaK04wGP2cP
7/UX5dSumkYqQQEHaedncfHCAzbG8CtSjs8UkmikPnBREmmNeKKCyikUwOSUIrJE
kmBvyASkZ9Wi0PPQ1+qOPA+60kBHkDTufaNjMGEwDwYDVR0TAQH/BAUwAwEB/zAf
BgNVHSMEGDAWgBS3/i1ixYFTzVIaL11goMNd+7IcHDAdBgNVHQ4EFgQUt/4tYsWB
U81SGi9dYKDDXfuyHBwwDgYDVR0PAQH/BAQDAgGGMAoGCCqGSM49BAMDA2gAMGUC
ME0HES0R+7kmwyHdcuEX/MHPFOpJznGHjtZT3BHNXVSKr9kt9IxR6rxmR+J/lYNg
ZQIxAIwhTE+75bBQ35BiSebMkdv4P11xkQiOT5LJf6Zc6hN+7W3E6MMqb1wR4aXz
alqaTQ==
-----END CERTIFICATE-----
)GOOGLE_CA";

//================ SENSORES ==============
#define DHTPIN 4
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);
Adafruit_BMP280 bmp;

//================ INTERVALOS ============
const unsigned long COLLECTION_INTERVAL_MS = 300000UL; // 5 minutos
const unsigned long WIFI_TIMEOUT_MS = 20000UL;
const unsigned long NTP_TIMEOUT_MS = 10000UL;
const unsigned long UPLOAD_BUDGET_MS = 45000UL;
const size_t READINGS_PER_BATCH = 12;

//================ HORARIO ===============
const char* ntpServer = "pool.ntp.org";
const long gmtOffset_sec = -10800;
const int daylightOffset_sec = 0;
const int COLLECTION_START_HOUR = 6;
const int COLLECTION_END_HOUR = 18;
const uint32_t UNKNOWN_CLOCK_RETRY_SECONDS = 5UL * 60UL;

//================ FILA LOCAL ============
// 4032 coletas de 5 em 5 minutos, das 06h as 18h: cerca de 28 dias sem internet.
// Quando cheia, descarta a mais antiga e avisa no monitor serial.
const size_t MAX_STORED_READINGS = 4032;
const char* QUEUE_FILE = "/fila_meteorologica.bin";
const char* QUEUE_TEMP = "/fila_meteorologica.tmp";
const char* QUEUE_BACKUP = "/fila_meteorologica.bak";
const uint32_t READING_MAGIC = 0x4D455431UL;
const uint16_t READING_VERSION = 1;

struct StoredReading {
  uint32_t magic;
  uint32_t checksum;
  uint32_t sessionHigh;
  uint32_t sessionLow;
  uint32_t sequence;
  uint32_t reserved;
  int64_t measurementUnixS; // zero = horario ainda desconhecido
  uint64_t uptimeMs;
  float temperaturaDHT;
  float umidade;
  float temperaturaBMP;
  float pressao;
  uint16_t formatVersion;
  uint16_t recordSize;
  uint32_t reserved2;
};
static_assert(sizeof(StoredReading) == 64, "Formato da fila local alterado.");

bool storageReady = false;
uint32_t sessionHigh = 0;
uint32_t sessionLow = 0;
uint32_t readingSequence = 0;
unsigned long lastCollectionMs = 0;
bool firstCollection = true;

// Prototipos explicitos para compatibilidade com o preprocessador Arduino.
uint32_t readingChecksum(const StoredReading& reading);
bool readingIsValid(const StoredReading& reading);
bool removeFirstRecords(size_t count);
bool appendReading(const StoredReading& reading);
String readingKey(const StoredReading& reading);
String readingJson(const StoredReading& reading);

uint32_t readingChecksum(const StoredReading& reading) {
  const uint8_t* bytes = reinterpret_cast<const uint8_t*>(&reading);
  uint32_t hash = 2166136261UL;
  for (size_t i = 0; i < sizeof(StoredReading); ++i) {
    // O checksum nao participa de seu proprio calculo.
    if (i >= offsetof(StoredReading, checksum) &&
        i < offsetof(StoredReading, checksum) + sizeof(reading.checksum)) continue;
    hash ^= bytes[i];
    hash *= 16777619UL;
  }
  return hash;
}

bool readingIsValid(const StoredReading& reading) {
  return reading.magic == READING_MAGIC &&
         reading.formatVersion == READING_VERSION &&
         reading.recordSize == sizeof(StoredReading) &&
         reading.checksum == readingChecksum(reading);
}

// Retorna false em erro de leitura, em vez de confundir erro com fila vazia.
bool queueCount(size_t& count) {
  count = 0;
  if (!storageReady) return false;
  if (!LittleFS.exists(QUEUE_FILE)) return true;
  File file = LittleFS.open(QUEUE_FILE, FILE_READ);
  if (!file) return false;
  count = file.size() / sizeof(StoredReading);
  file.close();
  return true;
}

// Reescreve apenas registros completos. O original fica em .bak ate a troca
// estar concluida; no proximo boot, uma troca interrompida e recuperada.
// count=0 permite reparar uma cauda incompleta sem remover coletas completas.
bool removeFirstRecords(size_t count) {
  if (!storageReady) return false;
  if (!LittleFS.exists(QUEUE_FILE)) return true;
  File source = LittleFS.open(QUEUE_FILE, FILE_READ);
  if (!source) return false;
  const size_t completeRecords = source.size() / sizeof(StoredReading);
  if (count > completeRecords) count = completeRecords;
  const size_t bytesToCopy = (completeRecords - count) * sizeof(StoredReading);

  if (bytesToCopy == 0) {
    source.close();
    return LittleFS.remove(QUEUE_FILE);
  }

  if (LittleFS.exists(QUEUE_TEMP) && !LittleFS.remove(QUEUE_TEMP)) {
    source.close();
    return false;
  }
  File destination = LittleFS.open(QUEUE_TEMP, FILE_WRITE);
  if (!destination || !source.seek(count * sizeof(StoredReading))) {
    source.close();
    if (destination) destination.close();
    return false;
  }

  uint8_t buffer[256];
  size_t remaining = bytesToCopy;
  bool ok = true;
  while (remaining > 0) {
    size_t chunk = remaining < sizeof(buffer) ? remaining : sizeof(buffer);
    size_t got = source.read(buffer, chunk);
    if (got != chunk || destination.write(buffer, got) != got) {
      ok = false;
      break;
    }
    remaining -= got;
  }
  destination.flush();
  ok = ok && destination.size() == bytesToCopy;
  destination.close();
  source.close();
  if (!ok) {
    LittleFS.remove(QUEUE_TEMP);
    return false;
  }

  if (LittleFS.exists(QUEUE_BACKUP) && !LittleFS.remove(QUEUE_BACKUP)) return false;
  if (!LittleFS.rename(QUEUE_FILE, QUEUE_BACKUP)) return false;
  if (!LittleFS.rename(QUEUE_TEMP, QUEUE_FILE)) {
    if (!LittleFS.rename(QUEUE_BACKUP, QUEUE_FILE)) storageReady = false;
    return false;
  }
  // Se a limpeza falhar, a inicializacao reconhece a fila principal como nova.
  if (!LittleFS.remove(QUEUE_BACKUP)) storageReady = false;
  return true;
}

bool repairIncompleteTail() {
  if (!LittleFS.exists(QUEUE_FILE)) return true;
  File file = LittleFS.open(QUEUE_FILE, FILE_READ);
  if (!file) return false;
  bool partial = file.size() % sizeof(StoredReading) != 0;
  file.close();
  if (!partial) return true;
  Serial.println("Gravacao interrompida: recuperando registros completos da fila.");
  return removeFirstRecords(0);
}

bool initializeStorage() {
  // Uma marca na NVS permite formatar somente na primeira utilizacao.
  // Depois disso, falha de montagem nao apaga automaticamente as pendencias.
  Preferences preferences;
  if (!preferences.begin("meteo-fs", false)) return false;
  bool initialized = preferences.getBool("initialized", false);
  bool mounted = LittleFS.begin(false);
  if (!mounted && !initialized) {
    Serial.println("Primeira utilizacao: preparando a particao LittleFS.");
    mounted = LittleFS.begin(true);
  }
  if (!mounted) {
    preferences.end();
    Serial.println("Falha no LittleFS. Confira a particao; a fila nao foi apagada.");
    return false;
  }
  bool marked = preferences.putBool("initialized", true) == 1;
  preferences.end();
  if (!marked) return false;
  storageReady = true;

  if (!LittleFS.exists(QUEUE_FILE) && LittleFS.exists(QUEUE_BACKUP)) {
    if (!LittleFS.rename(QUEUE_BACKUP, QUEUE_FILE)) return false;
  }
  if (LittleFS.exists(QUEUE_FILE) && LittleFS.exists(QUEUE_BACKUP)) {
    if (!LittleFS.remove(QUEUE_BACKUP)) return false;
  }
  if (LittleFS.exists(QUEUE_TEMP) && !LittleFS.remove(QUEUE_TEMP)) return false;
  if (!repairIncompleteTail()) return false;
  Serial.println("Armazenamento local pronto.");
  return true;
}

bool appendReading(const StoredReading& reading) {
  if (!storageReady || !repairIncompleteTail()) return false;
  size_t count;
  if (!queueCount(count)) return false;
  if (count >= MAX_STORED_READINGS) {
    Serial.println("Fila cheia: descartando a coleta mais antiga.");
    if (!removeFirstRecords(count - MAX_STORED_READINGS + 1)) return false;
  }
  File file = LittleFS.open(QUEUE_FILE, FILE_APPEND);
  if (!file) return false;
  size_t before = file.size();
  size_t written = file.write(reinterpret_cast<const uint8_t*>(&reading), sizeof(reading));
  file.flush();
  bool ok = written == sizeof(reading) && file.size() == before + sizeof(reading);
  file.close();
  return ok;
}

bool clockIsValid() {
  return time(nullptr) >= 1704067200; // 01/01/2024 UTC
}

// Zero durante a janela de coleta; fora dela, segundos ate as proximas 06h.
uint32_t secondsUntilMorning(time_t utcTimestamp) {
  time_t localTimestamp = utcTimestamp + gmtOffset_sec;
  struct tm parts;
  gmtime_r(&localTimestamp, &parts);
  const uint32_t secondsToday = parts.tm_hour * 3600UL +
                                parts.tm_min * 60UL + parts.tm_sec;
  const uint32_t start = COLLECTION_START_HOUR * 3600UL;
  const uint32_t end = COLLECTION_END_HOUR * 3600UL;
  if (secondsToday < start) return start - secondsToday;
  if (secondsToday >= end) return 24UL * 3600UL - secondsToday + start;
  return 0;
}

void sleepForSeconds(uint32_t seconds) {
  // A fila ja esta fechada e gravada na flash. O timer RTC continua contando
  // durante o deep sleep; ao despertar, setup() e executado novamente.
  Serial.print("Entrando em deep sleep por (s): ");
  Serial.println(seconds);
  WiFi.disconnect(true);
  WiFi.mode(WIFI_OFF);
  Serial.flush();
  esp_sleep_disable_wakeup_source(ESP_SLEEP_WAKEUP_ALL);
  esp_sleep_enable_timer_wakeup((uint64_t)seconds * 1000000ULL);
  esp_deep_sleep_start();
}

void enforceCollectionSchedule() {
  if (!clockIsValid()) {
    // Apos falta de energia, o relogio pode voltar a 1970. Sem horario valido,
    // nao coleta: dorme 5 min e tenta obter NTP novamente na inicializacao.
    Serial.println("Horario desconhecido: coleta suspensa ate sincronizar o NTP.");
    sleepForSeconds(UNKNOWN_CLOCK_RETRY_SECONDS);
    return;
  }
  uint32_t sleepSeconds = secondsUntilMorning(time(nullptr));
  if (sleepSeconds > 0) {
    Serial.println("Fora da janela 06h-18h. Retomada prevista para as 06h.");
    sleepForSeconds(sleepSeconds);
  }
}

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.begin(ssid, password);
  unsigned long start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < WIFI_TIMEOUT_MS) {
    delay(250);
  }
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("Sem Wi-Fi: as coletas permanecem na flash.");
    return false;
  }
  Serial.print("Wi-Fi conectado. IP: ");
  Serial.println(WiFi.localIP());
  return true;
}

void waitForClock() {
  if (clockIsValid() || WiFi.status() != WL_CONNECTED) return;
  configTime(gmtOffset_sec, daylightOffset_sec, ntpServer, "time.google.com");
  unsigned long start = millis();
  while (!clockIsValid() && millis() - start < NTP_TIMEOUT_MS) delay(100);
  if (!clockIsValid()) Serial.println("Sem NTP: ainda nao e possivel confirmar o horario de coleta.");
}

// Envia um PATCH REST usando exclusivamente o TLS nativo do ESP32.
// A resposta 204 confirma a escrita; print=silent evita trazer o lote de volta.
bool firebasePatch(const String& path, const String& payload) {
  if (WiFi.status() != WL_CONNECTED || !clockIsValid()) {
    firebaseLastError = "Wi-Fi desconectado ou horario invalido para TLS.";
    return false;
  }
  String base = DATABASE_URL;
  while (base.endsWith("/")) base.remove(base.length() - 1);
  if (!base.startsWith("https://")) {
    firebaseLastError = "DATABASE_URL deve comecar com https://";
    return false;
  }
  String url = base + path + ".json?print=silent";
  WiFiClientSecure client;
  client.setCACert(GOOGLE_ROOT_CERTIFICATES);
  client.setHandshakeTimeout(15); // segundos
  HTTPClient http;
  http.setConnectTimeout(10000);
  http.setTimeout(HTTPS_TIMEOUT_MS);
  http.setReuse(false);
  if (!http.begin(client, url)) {
    firebaseLastError = "Nao foi possivel iniciar HTTPS nativo.";
    return false;
  }
  http.addHeader("Content-Type", "application/json");
  int code = http.sendRequest("PATCH", payload);
  bool ok = code >= 200 && code < 300;
  Serial.printf("Firebase REST %s: HTTP %d\n", path.c_str(), code);
  if (!ok) {
    firebaseLastError = "HTTP " + String(code);
    if (code < 0) {
      firebaseLastError += " - " + HTTPClient::errorToString(code);
      char message[192] = {};
      int tlsCode = client.lastError(message, sizeof(message));
      Serial.printf("Detalhe TLS nativo: codigo %d; %s\n", tlsCode, message);
    } else {
      String response = http.getString();
      if (response.length() > 256) response = response.substring(0, 256);
      firebaseLastError += " - " + response;
      if (code == 401 || code == 403) {
        Serial.println("Conexao HTTPS estabelecida, mas escrita negada pelas regras.");
      }
    }
  } else {
    firebaseLastError = "";
  }
  http.end();
  client.stop();
  return ok;
}

String floatJson(float value) {
  return isfinite(value) ? String(value, 5) : String("null");
}

String readingKey(const StoredReading& reading) {
  char key[32];
  snprintf(key, sizeof(key), "m_%08lx%08lx_%08lx",
           (unsigned long)reading.sessionHigh, (unsigned long)reading.sessionLow,
           (unsigned long)reading.sequence);
  return String(key);
}

String readingJson(const StoredReading& reading) {
  int64_t timestamp = reading.measurementUnixS;
  // Se o primeiro NTP so chegou depois da coleta, reconstroi seu horario
  // apenas se ela pertence a esta mesma inicializacao. Apos desligamento,
  // uma coleta sem horario continua explicitamente sem horario.
  bool estimated = false;
  if (timestamp == 0 && clockIsValid() &&
      reading.sessionHigh == sessionHigh && reading.sessionLow == sessionLow) {
    uint64_t nowMs = (uint64_t)esp_timer_get_time() / 1000ULL;
    if (nowMs >= reading.uptimeMs) {
      timestamp = (int64_t)time(nullptr) - (int64_t)((nowMs - reading.uptimeMs) / 1000ULL);
      estimated = true;
    }
  }
  char dateTime[25] = "";
  if (timestamp > 0) {
    time_t localTimestamp = (time_t)(timestamp + gmtOffset_sec);
    struct tm parts;
    gmtime_r(&localTimestamp, &parts);
    strftime(dateTime, sizeof(dateTime), "%d/%m/%Y %H:%M:%S", &parts);
  }
  // Somente nomes fixos, numeros e a data formatada entram neste JSON.
  // Evita outra biblioteca de JSON e preserva os campos do banco existente.
  char unixText[24];
  char uptimeText[24];
  snprintf(unixText, sizeof(unixText), "%lld", (long long)timestamp);
  snprintf(uptimeText, sizeof(uptimeText), "%llu", (unsigned long long)reading.uptimeMs);
  String result;
  result.reserve(512);
  result = "{\"temperatura_dht\":" + floatJson(reading.temperaturaDHT);
  result += ",\"umidade\":" + floatJson(reading.umidade);
  result += ",\"temperatura_bmp\":" + floatJson(reading.temperaturaBMP);
  result += ",\"pressao\":" + floatJson(reading.pressao);
  result += ",\"data_hora\":\"" + String(dateTime) + "\"";
  result += ",\"horario_valido\":";
  result += timestamp > 0 ? "true" : "false";
  result += ",\"horario_estimado\":";
  result += estimated ? "true" : "false";
  result += ",\"horario_medicao_unix_s\":" + String(unixText);
  result += ",\"tempo_ativo_ms\":" + String(uptimeText);
  result += ",\"id_medicao_local\":\"" + readingKey(reading) + "\"}";
  return result;
}

void uploadPendingReadings() {
  enforceCollectionSchedule();
  size_t pending;
  if (!queueCount(pending) || pending == 0 || !connectWiFi()) return;
  waitForClock();
  enforceCollectionSchedule();
  unsigned long start = millis();
  while (storageReady && millis() - start < UPLOAD_BUDGET_MS) {
    enforceCollectionSchedule();
    if (WiFi.status() != WL_CONNECTED) return;
    File file = LittleFS.open(QUEUE_FILE, FILE_READ);
    if (!file) return;

    String payload = "{";
    String latest;
    size_t valid = 0;
    size_t consumed = 0;
    while (file.available() >= (int)sizeof(StoredReading) && valid < READINGS_PER_BATCH) {
      StoredReading reading;
      if (file.read(reinterpret_cast<uint8_t*>(&reading), sizeof(reading)) != sizeof(reading)) {
        file.close();
        return;
      }
      ++consumed;
      if (!readingIsValid(reading)) {
        Serial.println("Registro corrompido ignorado na fila local.");
        continue;
      }
      latest = readingJson(reading);
      if (valid > 0) payload += ",";
      payload += "\"" + readingKey(reading) + "\":" + latest;
      ++valid;
    }
    file.close();
    if (consumed == 0) return;
    payload += "}";

    if (valid > 0) {
      // Nao inicia outro envio se a janela terminou enquanto montava o lote.
      enforceCollectionSchedule();
      Serial.printf("RAM livre antes do envio Firebase: %u bytes\n",
                    (unsigned int)ESP.getFreeHeap());
      // PATCH inclui apenas as chaves deste lote, preservando o historico.
      // IDs persistidos tornam a repeticao do envio idempotente.
      if (!firebasePatch("/historico", payload)) {
        Serial.print("Falha no historico; fila mantida: ");
        Serial.println(firebaseLastError);
        return;
      }
      enforceCollectionSchedule();
      // Mantem os cinco campos originais em /sensores, com a ultima coleta
      // deste lote. A fila e enviada da mais antiga para a mais recente.
      if (!firebasePatch("/sensores", latest)) {
        Serial.print("Falha em /sensores; fila mantida: ");
        Serial.println(firebaseLastError);
        return;
      }
    }

    // So retira registros validos apos confirmar historico e /sensores.
    if (!removeFirstRecords(consumed)) {
      Serial.println("Falha ao atualizar fila local; interrompendo envio.");
      return;
    }
    Serial.print("Coletas confirmadas no Firebase: ");
    Serial.println(valid);
    if (!queueCount(pending) || pending == 0) return;
    delay(1);
  }
  // Limita a drenagem por ciclo para nao impedir as proximas coletas.
  Serial.println("Restam pendencias; envio continua apos a proxima coleta.");
}

void setup() {
  Serial.begin(115200);
  Serial.println("\nESTACAO METEOROLOGICA - FILA LOCAL E ENVIO A CADA COLETA");
  // O relogio do sistema e mantido durante o deep sleep. Se houver despertar
  // antecipado na madrugada, volta a dormir antes de inicializar os sensores.
  if (clockIsValid()) enforceCollectionSchedule();

  WiFi.mode(WIFI_STA);
  WiFi.setAutoReconnect(true);
  // Dois numeros aleatorios identificam esta inicializacao, e um contador
  // distingue suas coletas. A chave completa fica gravada junto aos dados.
  sessionHigh = esp_random();
  sessionLow = esp_random();
  if (connectWiFi()) {
    // Reinicia o NTP em cada despertar para corrigir a deriva do relogio RTC.
    configTime(gmtOffset_sec, daylightOffset_sec, ntpServer, "time.google.com");
    waitForClock();
  }
  enforceCollectionSchedule();

  dht.begin();
  if (!bmp.begin(0x76)) {
    Serial.println("BMP280 nao encontrado!");
    while (true) {
      enforceCollectionSchedule();
      delay(1000);
    }
  }
  storageReady = initializeStorage();
  if (!storageReady) Serial.println("ERRO: armazenamento indisponivel; confira o monitor serial.");

  Serial.println("Firebase REST: TLS nativo com validacao de certificado.");
  Serial.printf("Memoria RAM livre antes do envio: %u bytes\n",
                (unsigned int)ESP.getFreeHeap());
  delay(2000); // estabilizacao do DHT11, inclusive quando nao ha Wi-Fi
}

void loop() {
  // Confere tambem durante a espera entre coletas para dormir as 18h,
  // sem aguardar o proximo intervalo de cinco minutos.
  enforceCollectionSchedule();
  if (!firstCollection && millis() - lastCollectionMs < COLLECTION_INTERVAL_MS) {
    delay(20);
    return;
  }
  firstCollection = false;
  lastCollectionMs = millis();

  enforceCollectionSchedule();
  StoredReading reading = {};
  reading.magic = READING_MAGIC;
  reading.sessionHigh = sessionHigh;
  reading.sessionLow = sessionLow;
  reading.sequence = ++readingSequence;
  reading.formatVersion = READING_VERSION;
  reading.recordSize = sizeof(StoredReading);
  reading.temperaturaDHT = dht.readTemperature();
  reading.umidade = dht.readHumidity();
  reading.temperaturaBMP = bmp.readTemperature();
  reading.pressao = bmp.readPressure() / 100.0F;
  reading.uptimeMs = (uint64_t)esp_timer_get_time() / 1000ULL;
  reading.measurementUnixS = clockIsValid() ? (int64_t)time(nullptr) : 0;
  // Se uma leitura atravessou as 18h, nao a adiciona a fila.
  enforceCollectionSchedule();
  reading.checksum = readingChecksum(reading);

  if (!isfinite(reading.temperaturaDHT) || !isfinite(reading.umidade) ||
      !isfinite(reading.temperaturaBMP) || !isfinite(reading.pressao)) {
    Serial.println("Erro ao ler sensores; nova tentativa em 5 segundos.");
    // Mesmo com falha do sensor, tenta enviar coletas anteriores.
    uploadPendingReadings();
    lastCollectionMs = millis() - COLLECTION_INTERVAL_MS + 5000UL;
    return;
  }

  Serial.println("\n========== DADOS ==========");
  Serial.print("Temperatura DHT11 (C): "); Serial.println(reading.temperaturaDHT);
  Serial.print("Umidade (%): "); Serial.println(reading.umidade);
  Serial.print("Temperatura BMP280 (C): "); Serial.println(reading.temperaturaBMP);
  Serial.print("Pressao (hPa): "); Serial.println(reading.pressao);

  if (appendReading(reading)) {
    size_t count;
    Serial.print("Coleta salva na flash. Pendencias: ");
    if (queueCount(count)) Serial.println(count);
    // Sempre salva primeiro; em seguida tenta enviar dentro da janela diurna.
    uploadPendingReadings();
  } else {
    Serial.println("ERRO: coleta nao salva na flash. Verifique espaco e particao.");
    // Libera espaco enviando pendencias e tenta salvar esta coleta de novo.
    uploadPendingReadings();
    if (appendReading(reading)) uploadPendingReadings();
    else Serial.println("ATENCAO: nao foi possivel preservar esta coleta.");
  }
  enforceCollectionSchedule();
  Serial.println("Proxima coleta em aproximadamente 5 minutos, entre 06h e 18h.");
}

