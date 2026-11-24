# Maquete — STL para impressão 3D

Imprimir **uma unidade de cada um dos 13 STL** desta pasta, em **milímetros e escala 100%**. As peças estão separadas, orientadas com a face de montagem para baixo e apoiadas em **Z=0**.

## Lista de peças

| Arquivo | Dimensões X × Y × Z (mm) |
|---|---|
| 01_Bloco_administrativo.stl | 175.55 × 36.53 × 16.53 |
| 02_Bloco_de_ensino.stl | 36.03 × 111.70 × 16.53 |
| 03_Restaurante.stl | 38.50 × 67.55 × 11.87 |
| 04_Quadra_poliesportiva.stl | 50.88 × 79.77 × 19.87 |
| 05_Passarelas_rede_central.stl | 169.35 × 111.63 × 5.00 |
| 06_Passarela_continuacao_norte.stl | 5.01 × 97.96 × 5.00 |
| 07_Acesso_entrada.stl | 23.84 × 52.77 × 5.00 |
| 08_Piso_entrada_principal.stl | 26.67 × 28.33 × 8.50 |
| 09_Piso_estacionamento.stl | 58.33 × 30.00 × 8.50 |
| 10_Piso_bicicletario.stl | 65.00 × 30.00 × 8.50 |
| 11_Rampa.stl | 34.17 × 56.67 × 15.33 |
| 12_Escada_administrativo.stl | 13.33 × 16.67 × 4.00 |
| 13_Escada_ensino.stl | 13.33 × 11.67 × 4.00 |

## Impressão e montagem

Importar cada STL no fatiador e conferir a prévia das camadas, a adesão das peças estreitas e as pontes sobre os canais inferiores. A maior dimensão na mesa de cada arquivo é inferior a 256 mm; verificar a área útil da sua impressora antes de fatiar.

Os alojamentos, assentos, cavidades de acesso à solda e números fazem parte dos edifícios e pisos. Os botões KFC-A06 são componentes físicos. O tampo de MDF é cortado na CNC com 72 furos de 2,6 mm, quatro por botão, alinhados aos terminais.

As duas escadas são impressas separadamente e coladas sobre os respectivos edifícios, conforme o modelo completo. A rampa e as três peças de circulação são montadas ao redor dos blocos. Usar o SCAD principal como referência de posicionamento.

Cada botão tem uma cavidade inferior de 15,3 × 12,5 mm, aberta até 1,2 mm abaixo do corpo. O assento é fechado no centro, com quatro rasgos de terminais de 2,8 × 2,8 mm. O assento e as paredes de pelo menos 1,2 mm continuam sustentando o botão. Fazer a soldagem pela face inferior com o relevo fora do MDF, ou soldar antes de encaixar. Passar cada fio pelo furo de MDF alinhado ao seu terminal antes de fixar o relevo. Os canais e furos foram dimensionados para fios e soldas; conectores fêmea com capa plástica precisam de dimensionamento próprio. Conferir primeiro com o botão, os fios e a ponta de ferro reais.

Esta pasta contém as 13 peças principais da maquete. As legendas externas opcionais de texto/Braille continuam disponíveis no SCAD como `tipo_peca="legenda"`.

## Conferência

Todos os STL foram relidos e conferidos: malha fechada, orientação coerente, volume positivo, uma peça conectada por arquivo e base em Z=0. As dimensões e hashes estão em `VERIFICACAO.json`; a lista resumida está em `Lista_de_impressao.csv`.

Fonte: `../construcoes_vista_aerea.scad`. Para regenerar, executar `python ../exportar_stl_maquete.py` a partir desta pasta. A exportação anterior será preservada no histórico.
