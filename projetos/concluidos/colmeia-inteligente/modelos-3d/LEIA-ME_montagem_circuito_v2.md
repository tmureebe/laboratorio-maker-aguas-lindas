# Montagem 3D — revisão B / v2

Abra **montagem_circuito_colmeia_v2.scad** no OpenSCAD e pressione **F5**.

A versão anterior permanece em `montagem_circuito_colmeia.scad`, sem alterações. Seu LEIA-ME também foi preservado.

## Conferência elétrica

A pinagem nomeada da primeira versão correspondia ao firmware. O retorno do boost era representado por duas conexões separadas, dependendo da continuidade interna entre IN− e OUT−. A v2 desenha essa ligação explicitamente, em concordância com o GND comum do esquema.

A v2 passou por uma comparação automática entre as ligações usadas para gerar os fios 3D e as **14 redes** de `../circuito/esquema_profissional/conexoes.csv`:

| Item | Resultado |
|---|---|
| Duas células em paralelo, BAT+ para B+ e BAT− para B− | Conforme |
| P+ para chave; saída da chave para boost e divisor | Conforme |
| P− como retorno protegido; sem ligação externa a BAT− | Conforme |
| Saída 5 V para VIN/5V, separada do barramento 3V3 | Conforme |
| DHT11 externo / interno | GPIO4 / GPIO21 |
| INMP441 WS / SCK / SD | GPIO25 / GPIO26 / GPIO33 |
| INMP441 L/R | GND |
| MC-38 | GPIO27 e GND |
| Divisor R1/R2, 100 kΩ + 100 kΩ | Ponto médio para GPIO34 |
| C1 e pull-ups, quando exibidos | Redes correspondentes do esquema |

Não foram detectadas redes interrompidas nem uniões lógicas indevidas. A conferência também passou com os componentes opcionais ocultos e na vista explodida. Esses testes verificam as redes nomeadas; a posição física dos headers continua representativa e precisa ser conferida nas peças reais.

## Organização dos fios

- BMS, chave e conversor foram aproximados no lado esquerdo da placa.
- Barramentos de 3V3 e GND foram posicionados junto ao lado direito do ESP32.
- Cada DHT11 recebeu um grupo próprio de três fios.
- Os resistores de pull-up foram colocados junto aos DHT11, com jumpers locais. Essa é uma escolha de disposição da nova ilustração; não comprova a localização na montagem original.
- As três vias I²S contornam o ESP32, evitando atravessar a antena e a blindagem.
- O par do MC-38 segue a periferia. O cruzamento remanescente tem separação em Z.
- Os fios usam trajetos definidos, com cantos arredondados, em lugar de arcos largos.
- Os terminais metálicos dos resistores foram separados em duas pernas. A versão anterior desenhava uma haste contínua oculta dentro do corpo, inadequada como representação física do resistor.

O número de fios não diminuiu: a melhoria é a disposição em trajetos curtos, locais ou paralelos, com um retorno explícito adicional.

## Arquivos de conferência

- `fiacao_montagem_v2.svg`: projeção superior dos pontos realmente usados nos fios 3D. Pode ser aberta no navegador. As alturas não são mostradas nessa projeção.
- `conferencia_montagem_v2.json`: resultado da conferência e hash do arquivo original.
- `conferir_montagem_v2.py`: script reproduzível; depende de Python, NumPy e OpenSCAD.

Para repetir:

```bash
python objetos3d/conferir_montagem_v2.py
```

O SCAD também oferece `auditar_conexoes=true`, que imprime os terminais e conexões no console. A tabela de terminais e as chamadas `ligar(...)` são usadas diretamente na geometria, evitando manter uma lista de ligações independente do desenho.

## Alcance da validação

O OpenSCAD compilou a montagem, a vista explodida e a variante sem passivos opcionais. Foi inspecionada a projeção superior da fiação. A checagem geométrica por amostragem de 0,4 mm, incluindo os dois barramentos, não detectou sobreposição nem folga inferior a 0,2 mm entre fios de redes distintas na montagem normal. Trata-se de uma checagem aproximada, não de tolerância de fabricação.

Não houve simulação elétrica, medição na montagem real ou verificação completa de colisões com todos os corpos dos componentes. A renderização 3D via OpenGL continua indisponível neste ambiente.

Permanecem as ressalvas da revisão anterior: dimensões e modelos comerciais aproximados; confirmação da alimentação dos DHT11, dos pull-ups e do capacitor de 100 nF na montagem real. O projeto é uma ilustração 3D editável, não um gabarito de montagem ou fabricação.
