# Análise da aba e do molhamento da borda

Proposta de geometria para avaliação, baseada na revisão atual com encaixes integrados. O `.scad` e os STL existentes não foram alterados por esta análise.

## Caminho da água

No modelo atual, o prato tem raio externo de 70 mm, trecho plano até raio de 50 mm, queda de 20 mm e espessura vertical de 2,4 mm. A superfície superior drena para fora. Entretanto, água pode contornar a extremidade por molhamento e tensão superficial e alcançar parte da face inferior. Isso não significa que ela necessariamente percorrerá toda a saia para dentro: a face inferior sobe em direção ao centro, o que desfavorece o avanço por gravidade. Vento, respingos e detalhes do acabamento modificam o comportamento.

Uma aba vertical prolonga o caminho de retorno e desloca o ponto de gotejamento para baixo. Uma extremidade bem definida favorece o desprendimento da gota. Uma borda amplamente arredondada pode manter um caminho contínuo de molhamento para a face de dentro. A aba não produz vedação nem elimina, por si só, esse caminho superficial.

O princípio de usar pingadeiras ou sulcos para interromper o escoamento pela face inferior é descrito em [Mind the Drip, de Joseph Lstiburek](https://buildingscience.com/documents/building-science-insights/bsi-131-mind-drip). A aplicação às medidas deste abrigo é uma proposta de projeto, ainda sem ensaio de chuva.

## Proposta inicial

- Aba anular, prolongando a borda **4 mm abaixo da sua posição atual**, sem aumentar o raio externo.
- Parede de **1,6 mm**, afinando pelo lado interno até uma ponta com **0,8 mm** nos últimos 1,5 mm de altura. São dimensões iniciais para protótipo, não valores de eficácia comprovada.
- Arestas definidas no término, sem arredondamento amplo que una suavemente o lado externo ao interno.
- Aba afastada do prato seguinte, preservando um vão aberto de ventilação e drenagem. Não criar contato, encaixe estreito ou canal fechado entre as saias.

A seção sugerida está em [desenho da seção](analise-pingadeira.png). A espessura e a ponta precisam ser conferidas no fatiador para a largura de extrusão efetivamente usada.

## Efeito sobre a ventilação

Com passo de 18 mm e espessura de 2,4 mm, a abertura vertical junto ao raio externo é de **15,6 mm**. Acrescentar 4 mm para baixo reduz essa abertura para **11,6 mm**. Não se trata da menor distância em todo o percurso de ventilação: entre as faces inclinadas há uma restrição adicional. Por exemplo, uma aba de 4 mm com parede de 1,6 mm e ponta quadrada deixa aproximadamente **7,1 mm de distância normal mínima** até a saia inferior no corte radial idealizado. O chanfro da proposta alivia parcialmente essa restrição.

Essas medidas não permitem calcular a vazão de ar nem o erro térmico do sensor. A escolha da altura deve equilibrar a proteção contra gotas e a circulação de ar. Não há motivo geométrico para começar com uma aba longa; 4 mm é uma primeira variante para comparação.

## Adesão e capilaridade nos encaixes

O molhamento da borda e a condução em folgas estreitas são situações distintas. A folga radial nominal dos pinos é de **0,3 mm**. Se essas superfícies forem molháveis e receberem água, os espaços entre pino e receptor podem conduzi-la por capilaridade, além do escoamento por gravidade. A aba protege a região de alimentação de água, mas não veda os encaixes.

A [Universidade de Waterloo](https://uwaterloo.ca/building-engineering-group/building-performance/rain-penetration) descreve a penetração capilar em pequenas aberturas com superfícies molháveis. O [PNNL](https://basc.pnnl.gov/information/building-science-introduction-moisture-flow) explica que a capilaridade também ocorre entre dois materiais não porosos próximos. Não foi medido o molhamento do filamento deste projeto; não se presume que todos os plásticos ou acabamentos se comportem igualmente.

## Verificação prática proposta

Comparar a borda atual com uma variante de aba de 4 mm, usando o mesmo filamento e acabamento. Observar primeiro o escoamento por gravidade e depois borrifação lateral, verificando a face inferior, os encaixes e a câmara central. Água com corante e um indicador seco na região do sensor ajudam a localizar o percurso. A avaliação da ventilação deve comparar as duas geometrias nas mesmas condições de exposição e com referência de temperatura; a imagem da seção não substitui esse ensaio.
