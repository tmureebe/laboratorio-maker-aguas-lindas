# Mapa tátil de 500 × 380 mm

O arquivo adaptado é **`mapa_tatil_500x380.scad`**. A referência para os ambientes e os 18 pontos é `planta-funcional.pdf`. 

Os quatro edifícios e as quatro passarelas conservam as coordenadas CAD de seus contornos. A implantação inteira recebeu redução uniforme para **1:600**, mantendo as proporções e a entrada na borda inferior do desenho. O painel mede exatamente **500 × 380 × 3 mm**; sua face superior é Z=0.

Foram retirados do SCAD a guarita, a subestação, o reservatório, o anexo e os demais volumes ausentes na planta. O modelo contém o bloco administrativo, o bloco de ensino, o restaurante, a quadra, as circulações, os três pisos de acesso/estacionamento/bicicletário e as duas escadas. A rampa em U foi acrescentada à direita do bloco de ensino. Seu traçado e suas alturas são uma representação tátil esquemática, pois a planta não informa medidas da rampa.

Os botões 11 e 12 ficam sobre a quadra e o restaurante. No ensino, os pontos **17/16 (auditório/pátio)** e **15/14 (refeitório/laboratórios)** estão lado a lado; a saída 18 fica no extremo superior. As legendas foram corrigidas para “Centro de seleção audiovisual” e “Administração — 2º andar”, conforme a planta.

## Botões e fios

Há **18 furos passantes**, cortados efetivamente nos relevos, nos apoios anulares e no painel. Cada abertura percorre a espessura inteira até a face inferior do MDF; os fios podem descer diretamente para a caixa. Os anéis integram as peças dos edifícios/pisos, com superfície plana para o botão, inclusive sobre os telhados.

**O diâmetro padrão de 8,4 mm é uma medida provisória de encaixe**, ajustável no início do SCAD por `diametro_furo_botao_mm`. Ajustar também `diametro_apoio_botao_mm`, `diametro_cabeca_botao_mm` e a altura visual conforme o componente comprado. O arquivo verifica a parede mínima do anel e a distância entre apoios. As dimensões do corpo e o sistema de fixação do botão precisam ser compatíveis com o relevo e o vão interno disponíveis.

A implantação considera as nervuras da caixa V4 em **X=250, Y=110 e Y=240 mm**, de espessura 3 mm. Com os furos padrão, a menor folga horizontal entre uma abertura e essas nervuras é **6,3 mm**. O corpo real do componente deve ser conferido com suas próprias dimensões. Os arquivos anteriores da caixa continuam preservados; os novos furos estão neste SCAD e nos gabaritos desta pasta.

Em **F5**, os componentes azuis ilustram os botões instalados. Em **F6/exportação STL**, aparecem os anéis e seus furos abertos. Os componentes azuis servem como referência de instalação de botões físicos. Os números são relevos integrados às peças. As legendas externas opcionais mantêm texto e Braille.

## Arquivos de conferência

- `vista_superior_500x380.png`: vista superior do modelo, com identificação dos 18 pontos.
- `previa_3D_500x380.png`: prévia 3D da malha real exportada pelo OpenSCAD, com referências azuis dos botões.
- `gabarito_montagem_500x380.svg` e `gabarito_montagem_500x380_1_1.pdf`: contornos de montagem, furos e centros.
- `gabarito_furacao_500x380.svg` e `gabarito_furacao_500x380_1_1.pdf`: painel, furos, centros e números.
- `coordenadas_botoes_mm.csv`: centros medidos desde o canto inferior esquerdo, diâmetros e altura de apoio do botão. A altura refere-se ao topo do anel, antes do componente físico.
- `VERIFICACAO.json`: resultados das verificações geométricas e hash do SCAD conferido.

Os PDFs têm página de **500 × 380 mm**. Imprimir em **100% / tamanho real**, sem ajustar à página. Os contornos são traços de marcação; os centros e diâmetros de furação constam no CSV. Ao editar posições ou diâmetros no SCAD, regenerar os gabaritos; os arquivos prontos representam os parâmetros padrão desta revisão.

## Exportar pelo OpenSCAD

- `modo="maquete"`: conjunto montado, configuração inicial.
- `modo="gabarito"`: desenho 2D de montagem; exportar SVG/DXF/PDF.
- `modo="furacao"`: desenho 2D dos 18 furos e centros; exportar SVG/DXF/PDF.
- `modo="peca"`: exportação STL de uma peça, selecionada por `tipo_peca` e `numero_peca`.

| Tipo | Números das peças |
|---|---|
| `edificio` | 0 administrativo; 1 ensino; 2 restaurante; 3 quadra |
| `passagem` | 0 rede central; 1 continuação junto ao restaurante; 2 acesso da entrada |
| `piso` | 0 entrada; 1 estacionamento; 2 bicicletário |
| `rampa` | 0 |
| `escada` | 0 administrativo; 1 ensino |
| `legenda` | 1 a 18, legendas externas opcionais de 250 × 26 mm |
| `painel` | 0, representação do MDF com seus 18 furos |

As peças de relevo são exportadas com o fundo em Z=0 e cabem em 256 × 256 mm. O painel representa a chapa de MDF. A rede central de passagens é unida antes da divisão em duas peças, evitando sobreposição dos cruzamentos.

Foram conferidos os oito contornos CAD preservados, as dimensões do painel, a posição dos apoios dentro dos volumes, as malhas fechadas e a conexão de cada peça. Na montagem completa, o centro e oito amostras radiais de cada um dos 18 furos foram verificados por raios verticais: **162 trajetos livres em toda a espessura**, incluindo o painel. A validação é digital; o encaixe e o acionamento dependem do botão físico escolhido.

As entregas antigas em `mapa_tatil_v1/` e seus gabaritos de 500 × 500 mm permanecem como histórico. Os arquivos desta pasta correspondem à implantação nova de 500 × 380 mm.
