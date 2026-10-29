# Pedestal revisado — estrutura e tampo 500 × 380 mm a laser

**Montagem passo a passo:** [guia ilustrado com dicas de colagem — PDF A4, 15 páginas](05_GUIA/Manual_ilustrado/Guia_ilustrado_montagem_pedestal.pdf). Inclui os códigos das 47 peças, setas de encaixe, detalhes dos apoios, orientação de prensagem e interface com a caixa eletrônica V4. [Visão geral das páginas](05_GUIA/Manual_ilustrado/Visao_geral_do_manual.png).

Use esta pasta para fabricar a revisão. A pasta `Pedestal_MDF_17_pecas` contém a versão antiga.

## Medidas e material

- Tampo: **500 × 380 mm**, uma camada de MDF 3 mm, inclinação 9.09°.
- Corpo: **340 × 300 mm**. Frente 860 mm / traseira 908 mm acima da base laminada.
- Base no chão: **440 × 340 mm**, três camadas coladas de MDF, total 9 mm.
- Altura no centro do tampo: 89.6 cm. Borda baixa/alta aproximadamente 86.6/92.6 cm.
- 15 chapas de 600 × 400 mm para o pedestal: 46 peças, incluindo reforços e apoios. O tampo é adicional.
- Área útil **560 × 360 mm**: 40 mm de folga total em cada dimensão, 20 mm por borda. Intervalo mínimo de 8 mm entre peças.
- Todas as peças são do mesmo MDF; as três bases viram uma única peça laminada de 9 mm. Divisórias H e grelha G também são de 3 mm.

## Arquivos para o laser

`01_CHAPAS_DXF` e `02_CHAPAS_SVG` são alternativas do mesmo corte. Cada arquivo numerado é uma chapa; as peças pequenas já estão incluídas. Os oito primeiros arquivos levam **duas peças grandes de parede em cada chapa**. Corte uma vez cada arquivo de 01 a 15.

Vetores em milímetros, escala 1:1, contornos fechados; furos e perímetros separados. Não há molduras nem textos de gravação nos arquivos de corte. A página SVG mede 600 × 400; a origem e o eixo Y no DXF são os usuais de CAD (o SVG tem Y invertido para representar a mesma disposição). Nomes e posição das peças aparecem em `05_GUIA/Mapa_das_15_chapas.pdf` e `.png`. `Lista_de_pecas.csv` informa todas as peças e chapas.

Os arquivos não têm compensação da largura do feixe. A folga total nominal é 0.15 mm nas ranhuras e nos cantos. Faça a compensação **uma vez no CAM**, exterior dos perímetros e interior dos furos. Use espessura medida, não redimensione o desenho. `06_TESTE_ENCAIXE` é um cupom de fabricação; as ranhuras, de baixo para cima, têm larguras 2.9, 3, 3.1, 3.15, 3.2, 3.25, 3.3 mm. Ajuste a espessura/folga no gerador se necessário. As emendas coplanares das paredes têm dentes nominais complementares, sem folga incorporada: dependem da compensação do feixe.

## Tampo inteiro para CNC a laser

Use `08_TAMPO_LASER_500x380/TAMPO_INTEIRO_500x380.dxf` ou o SVG equivalente, em milímetros e escala 1:1. Incluem um perímetro de **500 × 380 mm** e 25 ranhuras passantes. Corte o tampo inteiro na CNC a laser indicada para esta peça, com área útil que comporte o contorno. A estrutura usa as 15 chapas existentes. A medida do tampo supera a antiga área útil de 560 × 360 mm na profundidade; os arquivos do tampo usam página própria de 500 × 380 mm.

A redução retira 10 mm da frente e 10 mm de trás do tampo original, mantendo o centro e a inclinação. Todas as peças do pedestal, incluindo GX e GY, são compatíveis com as anteriores; não é necessário recortá-las. As coordenadas s dos furos diminuem 10 mm. A grelha fica a 18 mm das bordas laterais e 8 mm das bordas dianteira/traseira.

Os vetores representam a peça acabada, **sem compensação da largura do feixe**. No software da sua CNC a laser, corte os encaixes antes do perímetro e aplique compensação uma vez: interna nos furos, externa no contorno. Ajuste potência, velocidade e passes para o MDF medido e o laser utilizado. Os cantos retangulares são adequados ao processo a laser. Confira primeiro um encaixe em retalho do mesmo MDF, usando `06_TESTE_ENCAIXE`. Não escale o desenho para corrigir espessura. Não é necessário dividir o tampo ou reposicionar a chapa durante o corte.

Os **25 encaixes** incluem dentes nas quatro paredes superiores e nas cinco nervuras da grelha. A inclinação foi considerada na projeção dos furos: um dente vertical atravessa um tampo inclinado e precisa de ranhura mais larga que a espessura nominal. `Coordenadas_dos_encaixes.csv` usa x e s medidos **na chapa**, a partir do canto dianteiro esquerdo, olhando a face superior. Não transferir diretamente as coordenadas horizontais do corpo. Os dentes sobem aproximadamente 3 mm, sem deixar espigas altas sobre o mapa; nivelar com lixa após colagem.

## Montagem

1. Identifique com lápis todas as peças conforme o mapa de chapas. F = frente baixa, T = traseira, E/D = laterais. As faixas 1…4 sobem da base ao topo. Antes da cola, confira o encaixe a seco com o MDF real.
2. Cole B1+B2+B3 em superfície plana. B1 é inferior, B2 intermediária, B3 superior com 12 ranhuras. Alinhe as bordas; não deixe cola obstruir as ranhuras. A base deve apoiar **toda a face inferior no chão**, sem pés altos ou pequenos.
3. Una as quatro faixas de cada parede em plano. Cole RF1…RF3 / RT1…RT3 / RE1…RE3 / RD1…RD3 na face interna das respectivas emendas. Tiras de 30 mm centralizadas na linha nominal da emenda; ficam 30 mm afastadas das extremidades.
4. Cole A1F/T/E/D abaixo de H1 e A2F/T/E/D abaixo de H2. H1 e H2 têm face superior a 320 e 620 mm acima da base superior. Portanto, a **borda superior de cada apoio A** fica a 317 / 617 mm (para MDF 3 mm). Apoios com 20 mm de altura: borda inferior a 297 / 597 mm. Cole as faces internas das paredes contra as faces largas dos apoios; a divisória pousa na borda superior de 3 mm de cada apoio. Estas divisórias travam o corpo e reduzem o vão livre das paredes.
5. Monte paredes e base B3 juntas, mantendo cantos soltos até inserir os dentes inferiores. Os dentes entram somente nos 3 mm de B3; B1/B2 ficam inteiros. Insira H1 e H2 **antes de fechar a última parede** e cole suas quatro bordas. Confira diagonais e esquadro.
6. **Antes de fechar H1**, coloque e imobilize o lastro no compartimento inferior, diretamente sobre B3, centralizado e distribuído. Não ponha peso nas divisórias H ou no tampo. Consulte o dimensionamento abaixo. Para uso fixado ao piso, instalar a fixação mecânica adequada antes de fechar o compartimento.
7. Encaixe a grelha: GX1/GX2/GX3 são as travessas em s=90/190/290 mm; GY1/GY2 as longarinas em x=125/375 mm do tampo. Nas interseções entre nervuras, GX tem ranhuras superiores e GY inferiores. Na passagem pelas paredes, todas as nervuras têm ranhuras inferiores e as paredes superiores. Faça um encaixe simultâneo a seco; os dentes de cada nervura ficam para cima. Cole as meias-madeiras e os contatos com as paredes. Os encaixes apenas posicionam, precisam de cola.
8. Passe cola nas bordas superiores das paredes e de todas as nervuras; assente o tampo com os 25 dentes alinhados às respectivas ranhuras. Mantenha pressão distribuída durante a cura conforme a cola. A grelha se estende até 18 mm das bordas laterais e 8 mm da frente/traseira do tampo, sustentando as partes em balanço.
9. As faces horizontais da frente/traseira encontram uma chapa inclinada: pode haver até 0.48 mm de diferença ao longo da espessura. Ajuste a borda por lixa ao ângulo de 9.09° ou preencha a diferença com adesivo apropriado, sem levantar o tampo. Lixe pontas dos dentes até ficarem rentes ao tampo. Só depois da cura, cole o mapa.

## Estabilidade da base reduzida

A base 440 × 340 economiza 40% da área da antiga 500 × 500. A estrutura possui paredes formando uma caixa fechada, 12 reforços de emenda, duas divisórias horizontais, base laminada e grelha superior de cinco nervuras de 70 mm. Isso organiza um caminho de apoio para o tampo fino; o lastro resolve a estabilidade ao tombamento de um pedestal alto.

Dimensionamento estático adotado para orientar o lastro: força horizontal **20 N** (aproximadamente 2 kgf), aplicada a **0,93 m** de altura; fator 1,5 sobre o momento; centro de massa centrado; chão plano. O caso crítico usa metade da profundidade da base, 0,17 m:

`massa total mínima = 1,5 × 20 × 0,93 / (9,81 × 0,17) = 16.73 kg`.

Adote **pelo menos 17 kg de massa total do conjunto** (pedestal + tampo + mapa + lastro), com lastro imobilizado na parte inferior. O MDF foi estimado em 4.69 kg usando densidade 700 kg/m³; a densidade real e a massa do mapa variam. **Pese o conjunto** e complete com lastro até 17 kg. Exemplo: se pedestal+tampo+mapa pesarem 5 kg, usar no mínimo 12 kg de lastro. O compartimento inferior tem aproximadamente 334 × 294 × 317 mm; distribua o peso dentro do corpo, sobre a base apoiada no chão.

Sem lastro ou fixação ao piso, essa base reduzida não atende ao caso estático assumido. O cálculo não é ensaio de carga, não estabelece carga máxima no tampo e não cobre uma pessoa apoiando o peso do corpo. Para interação pública que possa incluir esse apoio, use fixação mecânica ao piso e dimensione a estrutura para as cargas reais. O protótipo de MDF de 3 mm ainda exige avaliação física das colagens e da flexão para o mapa utilizado. Não há certificação estrutural nesta entrega.

## Visualizar e regenerar

Abra `04_MODELOS_3D/Pedestal_MDF.scad` no OpenSCAD. Modo inicial `montado`; para ver as divisórias, desmarque `mostrar_paredes` e `mostrar_tampo`. Modos `explodido`, `peca2d`, `peca3d`, `chapa2d`, `chapas`. Peças 1…47 (a 47ª é o tampo); chapas 1…15. Em modo explodido o tampo é levantado 100 mm. O SCAD contém a montagem exata com todos os reforços; não apenas as peças planas.

Dependências em `07_FONTE/requirements.txt`. Gerar os cortes e o modelo: `python 07_FONTE/gerar_pedestal.py --espessura 3 --folga 0.15`. Gerar as vistas de montagem: `python 07_FONTE/gerar_vistas.py`. Gerar os 47 STL individuais: `python 07_FONTE/exportar_stl.py` (requer OpenSCAD). Os STL são peças planas para visualização; a montagem completa está no SCAD. Espessura altera os encaixes, não a escala geral. Regere em pasta vazia ao mudar os parâmetros. `DIMENSIONAMENTO.json` registra as medidas e as verificações de geração: contornos válidos, inventário, faixas reconstruídas, limites úteis e distâncias entre peças. Não registra ensaios físicos.

Fontes para propriedades de painéis e união por cola: [USDA Wood Handbook](https://research.fs.usda.gov/download/treesearch/37440.pdf). Propriedades do MDF dependem do produto; a estimativa de massa e a equação de tombamento acima são hipóteses deste projeto, sem adoção de resistência tabelada como capacidade de carga.
