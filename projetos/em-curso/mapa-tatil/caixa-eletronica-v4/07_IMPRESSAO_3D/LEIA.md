# Tacos para parafusos de 3,5 × 12 ou 3,5 × 20 mm

Os oito tacos são iguais. Cada peça mede **20 × 20 × 44 mm** e tem um furo-guia cego de **Ø2,8 mm por 18 mm de profundidade**, com 2 mm de plástico no fundo.

- [STL de uma unidade para teste](Taco_20x20x44_1un.stl)
- [STL do lote de oito](Tacos_20x20x44_8un.stl)
- [Modelo OpenSCAD](../04_MODELO_3D/Taco_impressao_3D.scad)
- [Verificação das malhas e da furação](VALIDACAO_TACOS.json)
- [Desenho dos parafusos e arruelas em escala real](../05_GUIA/Parafusos_e_arruelas_escala_1_1.pdf)

A tabela considera parafuso para madeira de cabeça panela, comprimento medido sob a cabeça, parede de MDF de 3 mm e arruela lisa de 0,8 mm. O taco fica encostado à parede.

| Parafuso | Entrada nominal da ponta no taco | Folga até o fundo do furo |
|---|---:|---:|
| 3,5 × 12 mm | 8,2 mm | 9,8 mm |
| 3,5 × 20 mm | 16,2 mm | 1,8 mm |

Imprima uma unidade em escala de 100%, na orientação do STL, com a abertura para cima. Antes de imprimir o lote, monte a amostra com o parafuso, a arruela e o MDF reais. Confira se a cabeça assenta e a rosca segura no plástico sem espanar nem abrir a peça. A passagem nas paredes C2/C3 mede Ø3,5 mm no corte. Se o parafuso prender no MDF, retire o taco e alargue **somente o MDF** para Ø4 mm.

Centros dos tacos, em milímetros desde o canto dianteiro esquerdo da caixa:

| Parede | y | x dos quatro tacos |
|---|---:|---|
| Frente | 13 | 30, 150, 400, 470 |
| Traseira | 367 | 30, 150, 270, 470 |

**O taco traseiro que ficava em x=400 agora fica em x=270.** Girar os tacos traseiros 180° em torno de z para que os furos fiquem voltados para a parede traseira. O eixo dos parafusos é z=35 e os tacos são colados somente à tampa. O [guia revisado](../05_GUIA/Guia_de_montagem.pdf) mostra a montagem completa; `tacos_impressos=true` nos modelos exibe a forma com os furos-guia.
