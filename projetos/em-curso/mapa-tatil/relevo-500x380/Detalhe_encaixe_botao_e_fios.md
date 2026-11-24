# Inspeção do encaixe e das soldas do botão

Abrir **[Detalhe_encaixe_botao_e_fios.scad](Detalhe_encaixe_botao_e_fios.scad)** no OpenSCAD e usar F5 para cores e transparência. O arquivo recorta a peça real do mapa ao redor do botão escolhido, mostra o KFC-A06, seus quatro terminais e dois fios conectados. Não modifica nenhum arquivo de fabricação.

[Prévia em corte do acesso inferior à solda](Previa_acesso_solda.png).

No personalizador:

- `numero_botao`: selecionar de 1 a 18. Começar pelo 4, sobre edifício, e pelo 1, sobre piso baixo.
- `vista="corte"`: remove a metade de trás do suporte e do trecho de MDF para enxergar o assento e as passagens. O botão permanece inteiro.
- `vista="explodida"`: levanta botão, fios e soldas para mostrar o alojamento e a superfície de apoio em verde.
- `vista="montada"`: encaixe completo, suporte transparente e interferências em vermelho.
- `vista="inferior"`: olhar pelo lado de baixo da tampa.
- `vista="soldagem"`: botão fora da peça, com a ponta do ferro ilustrando a aproximação antes do encaixe.
- `mostrar_mdf=false`: esconder o trecho da tampa e examinar somente o suporte impresso.
- `mostrar_mdf=false` e `mostrar_ponta_ferro=true`, em `corte` ou `montada`: mostrar o acesso pela cavidade inferior com o botão no suporte.
- Alterar diâmetro do fio isolado, condutor e envelope da solda conforme os materiais e o processo reais. A ponta do ferro é um envelope nominal; a verificação automática descrita abaixo confere esse envelope nas peças reais do modelo.

**Verde:** superfície real do impresso imediatamente abaixo do corpo, limitada à planta do botão. O assento sustenta o corpo na pressão para baixo. O encaixe atual não tem trava: sozinho, não impede que o botão saia por cima.

**Vermelho:** interseção volumétrica entre os fios/soldas e o suporte ou MDF, na posição montada. A checagem usa as peças inteiras, mesmo na vista em corte. Na vista explodida esse destaque fica desligado para não confundir a posição montada com a de inspeção.

## O que o detalhe revela

Os terminais medem nominalmente 3,5 mm abaixo do corpo. A base dos botões mais baixos (1–3) está agora em z=5 mm; as pontas terminam em z=1,5 mm, inteiramente acima do MDF. Nos demais pontos, a altura depende do edifício. Os canais verticais e as soldas ficam nas peças impressas.

A tampa tem **quatro furos de 2,6 mm por botão**, um sob cada terminal: x=±6,25 e y=±2,5 mm em relação ao centro. São 72 furos no total, sem furo central. Os dois fios representados atravessam diretamente os furos alinhados aos seus terminais; as outras duas passagens ficam disponíveis.

A cavidade na face inferior do relevo foi ampliada para **15,3 × 12,5 mm** e chega até **1,2 mm abaixo do corpo**. O assento e as paredes de pelo menos 1,2 mm continuam sustentando o botão. Com o relevo separado do MDF, a cavidade dá acesso aos quatro terminais para soldar por baixo. A ponta ilustrada entra inclinada 15° em direção ao centro da cavidade.

O centro do assento é fechado, sem furo circular. Os únicos furos no assento são os quatro rasgos dos terminais, de 2,8 × 2,8 mm. Essa dimensão foi definida para terminal e solda; a capa plástica de um jumper fêmea e o comprimento do conector não foram incluídos na validação.

A inspeção usa fio isolado de 1,4 mm, condutor de 0,5 mm e envelope de solda de 2 mm de diâmetro por 1,6 mm de altura. Esses valores são editáveis, não medidas confirmadas do material físico. Os canais verticais têm 2,8 × 2,8 mm. Os centros 14 e 15 permanecem afastados 0,5 mm cada em x para conservar a parede entre eles.

Soldar pela face inferior com o botão no suporte, antes de fixar o relevo ao MDF, ou soldar fora da peça antes de encaixar. Conferir as juntas, acomodá-las nos canais e passar cada fio pelo furo de MDF alinhado ao terminal. Os terminais sem fio também ficam acima do MDF. Conferir a folga com a ponta do ferro e os componentes reais antes de colar os relevos.

Executar `python validar_encaixe_botao.py` para conferir as peças reais por CGAL: ausência de interseção dos fios/soldas com impresso/MDF, acesso da ponta nominal de 3 mm aos quatro terminais com o MDF removido e área de apoio sob cada corpo. Resultados em [VERIFICACAO_DETALHE_BOTAO.json](VERIFICACAO_DETALHE_BOTAO.json).

Os dois fios estão nos terminais da fileira y=-2,5, nos lados x opostos. A representação é mecânica: confirmar com multímetro que os terminais escolhidos pertencem a contatos distintos antes de fazer a ligação elétrica.

O suporte e o botão são importados dos SCAD atuais. Os centros e alturas usados para selecionar os 18 pontos correspondem à integração de 09/11/2026. Se o mapa mudar, atualizar também essa tabela no detalhe. As dimensões complementares do botão e dos terminais continuam nominais e precisam de conferência na peça física.
