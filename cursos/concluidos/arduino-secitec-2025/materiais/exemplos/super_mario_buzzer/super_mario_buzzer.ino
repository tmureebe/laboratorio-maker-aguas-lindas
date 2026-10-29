/* Super Mario – trecho do tema Overworld
   Buzzer passivo no pino 8 (módulo 3 pinos: VCC=5V, I/O=8, GND=GND)
   Testado para placas AVR (UNO/Nano). Funciona também em ESP32/STM32 com ajustes mínimos.
*/

#define BUZZER_PIN 8

// Tabela de frequências (Hz). Se quiser mais oitavas, acrescente conforme necessário.
#define NOTE_B0  31
#define NOTE_C1  33
#define NOTE_CS1 35
#define NOTE_D1  37
#define NOTE_DS1 39
#define NOTE_E1  41
#define NOTE_F1  44
#define NOTE_FS1 46
#define NOTE_G1  49
#define NOTE_GS1 52
#define NOTE_A1  55
#define NOTE_AS1 58
#define NOTE_B1  62
#define NOTE_C2  65
#define NOTE_CS2 69
#define NOTE_D2  73
#define NOTE_DS2 78
#define NOTE_E2  82
#define NOTE_F2  87
#define NOTE_FS2 93
#define NOTE_G2  98
#define NOTE_GS2 104
#define NOTE_A2  110
#define NOTE_AS2 117
#define NOTE_B2  123
#define NOTE_C3  131
#define NOTE_CS3 139
#define NOTE_D3  147
#define NOTE_DS3 156
#define NOTE_E3  165
#define NOTE_F3  175
#define NOTE_FS3 185
#define NOTE_G3  196
#define NOTE_GS3 208
#define NOTE_A3  220
#define NOTE_AS3 233
#define NOTE_B3  247
#define NOTE_C4  262
#define NOTE_CS4 277
#define NOTE_D4  294
#define NOTE_DS4 311
#define NOTE_E4  330
#define NOTE_F4  349
#define NOTE_FS4 370
#define NOTE_G4  392
#define NOTE_GS4 415
#define NOTE_A4  440
#define NOTE_AS4 466
#define NOTE_B4  494
#define NOTE_C5  523
#define NOTE_CS5 554
#define NOTE_D5  587
#define NOTE_DS5 622
#define NOTE_E5  659
#define NOTE_F5  698
#define NOTE_FS5 740
#define NOTE_G5  784
#define NOTE_GS5 831
#define NOTE_A5  880
#define NOTE_AS5 932
#define NOTE_B5  988
#define NOTE_C6  1047
#define NOTE_CS6 1109
#define NOTE_D6  1175
#define NOTE_DS6 1245
#define NOTE_E6  1319
#define NOTE_F6  1397
#define NOTE_FS6 1480
#define NOTE_G6  1568
#define NOTE_GS6 1661
#define NOTE_A6  1760
#define NOTE_AS6 1865
#define NOTE_B6  1976
#define NOTE_C7  2093
#define NOTE_CS7 2217
#define NOTE_D7  2349
#define NOTE_DS7 2489
#define NOTE_E7  2637
#define NOTE_F7  2794
#define NOTE_FS7 2960
#define NOTE_G7  3136
#define NOTE_GS7 3322
#define NOTE_A7  3520
#define NOTE_AS7 3729
#define NOTE_B7  3951

// Para pausas:
#define REST     0

// Tempo base: quanto menor, mais rápido. 180–220 dá um “feeling” típico do Mario.
const int TEMPO_BPM = 196;

// Fator de staccato: 0.85 = 85% do tempo da nota soando, 15% de pausa
const float STACCATO = 0.85;

// Função para calcular duração (ms) de uma nota dada a figura rítmica.
// Usamos denominadores: 4=semínima, 8=colcheia, 16=semicolcheia etc.
int dur_ms(int denom) {
  // duração de 1 semibreve em ms = 240000 / BPM
  // semínima = semibreve/4, colcheia = semibreve/8, ...
  long whole_ms = 240000L / TEMPO_BPM;
  return (int)(whole_ms / denom);
}

// Melodia do tema Overworld (trecho clássico). Cada par: {nota, figura rítmica}
struct Note { int freq; int denom; };

Note mario[] = {
  // Introdução: E7 E7 (pausa) E7 (pausa) C7 E7 (pausa) G7 (pausa) G6
  {NOTE_E7, 8}, {NOTE_E7, 8}, {REST, 8}, {NOTE_E7, 8}, {REST, 8},
  {NOTE_C7, 8}, {NOTE_E7, 8}, {REST, 8}, {NOTE_G7, 4}, {REST, 4},
  {NOTE_G6, 4}, {REST, 4},

  // Frase 1
  {NOTE_C7, 4}, {REST, 8}, {NOTE_G6, 8}, {REST, 8}, {NOTE_E6, 8}, {REST, 8},
  {NOTE_A6, 8}, {REST, 8}, {NOTE_B6, 8}, {REST, 8}, {NOTE_AS6, 8}, {NOTE_A6, 8},
  {NOTE_G6, 8}, {NOTE_E7, 8}, {NOTE_G7, 8}, {NOTE_A7, 8}, {REST, 4},
  {NOTE_F7, 8}, {NOTE_G7, 8}, {REST, 8}, {NOTE_E7, 8}, {REST, 8},
  {NOTE_C7, 8}, {NOTE_D7, 8}, {NOTE_B6, 4},

  // Pequena cadência
  {REST, 8}, {NOTE_C7, 8}, {REST, 8}, {NOTE_G6, 8}, {REST, 8}, {NOTE_E6, 8},
  {REST, 8}, {NOTE_A6, 8}, {NOTE_B6, 8}, {REST, 8}, {NOTE_AS6, 8}, {NOTE_A6, 8},
  {NOTE_G6, 8}, {NOTE_E7, 8}, {NOTE_G7, 8}, {NOTE_A7, 8}, {REST, 4},
  {NOTE_F7, 8}, {NOTE_G7, 8}, {REST, 8}, {NOTE_E7, 8}, {REST, 8},
  {NOTE_C7, 8}, {NOTE_D7, 8}, {NOTE_B6, 4},
};

const int N_NOTES = sizeof(mario) / sizeof(mario[0]);

void playNote(int freq, int denom) {
  int d = dur_ms(denom);
  if (freq == REST) {
    noTone(BUZZER_PIN);
    delay(d);
  } else {
    int on_ms = (int)(d * STACCATO);
    int off_ms = d - on_ms;
    tone(BUZZER_PIN, freq, on_ms);
    delay(on_ms + off_ms);
  }
}

void setup() {
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {
  for (int i = 0; i < N_NOTES; i++) playNote(mario[i].freq, mario[i].denom);

  // Pausa entre repetições
  delay(800);
}

