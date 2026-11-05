# Circuito montado na estrutura integrada

Abra **estacao_integrada_com_circuito.scad** no OpenSCAD e pressione **F5**. Mantenha `estacao_integrada.scad` na mesma pasta: o novo arquivo reutiliza seus módulos, preservando a geometria R2 e os STL de fabricação.

O arquivo inicia em corte: somente a metade frontal da estrutura é removida da visualização; a eletrônica aparece inteira. No Customizador, `vista` permite `corte`, `montado`, `eletronica` e `caixa_aberta`. `mostrar_fios` e `mostrar_rotulos` controlam os detalhes. A vista `caixa_aberta` omite tampa e abrigo, mas mantém os sensores na posição de montagem.

A montagem segue o esquema em `../../circuito/esquema_circuito_estacao_meteorologica.png` e os sensores do firmware v2: ESP32, DHT11 e BMP280. A lista antiga com apenas BME280 não foi adotada.

- ESP32 encaixado na breadboard, com jumpers e módulos TP4056 e conversor elevador sobre adaptadores isolantes/headers ilustrativos.
- Breadboard com corpo de **83 × 35 × 9 mm**, correspondente ao corpo central de uma placa de 400 pontos com **ambas as réguas de alimentação removidas**, restando 300 contatos. Uma breadboard inteira de 83 × 55 mm não cabe neste arranjo ao lado do suporte. Escolha um modelo com réguas destacáveis e confira as medidas reais.
- Uma célula 18650 de **Ø18,5 × 65 mm** dentro de suporte aproximado de **78 × 22 × 22 mm**, colado ao fundo com camada de 0,5 mm. A célula continua removível.
- ESP32 aproximado de **49 × 28 mm**, TP4056 de **26 × 17 mm** e step-up de **34 × 17 mm**. O step-up avança ligeiramente além da borda da breadboard. Adaptadores precisam ser compatíveis com as placas adquiridas; o desenho não define sua fabricação ou fiação interna.
- Sensores sobre espaçadores de 4 mm na base superior do abrigo, com abraçadeiras ilustrativas nos rasgos existentes. Chicote de sete vias passa pelo furo de 20 mm e pelo tubo. A acomodação final das abraçadeiras deve deixar as aberturas dos sensores livres.
- Chave liga/desliga interna, acessível abrindo a caixa. Não foram acrescentados furos para a chave ou para os conectores USB.

Os fios representam o percurso e as funções do esquema: bateria → TP4056 protegido → chave → step-up → ESP32; sensores alimentados pelo ESP32. Vermelho representa alimentação, preto terra, laranja DATA do DHT11/GPIO4, verde SDA/GPIO21 e amarelo SCL/GPIO22. Vermelho é usado tanto nos trechos da bateria e de 5 V quanto nos trechos de 3,3 V; não significa que todas essas linhas sejam o mesmo nó.

Este é um **modelo de disposição física**, com dimensões presumidas e terminais ilustrativos, não um esquema de pinagem ou uma simulação elétrica. Contatos internos da breadboard, derivações de alimentação, configuração de CSB/SDO do BMP280 e componentes dos módulos não estão detalhados. Confira a pinagem real pelo esquema e pelos módulos antes de montar. Os jumpers não devem ser reproduzidos apenas pela posição gráfica de suas pontas.

Não imprima o conjunto com o circuito como um único STL. Para fabricar a estrutura, use as peças e instruções originais de `LEIA-ME.md`. Meça a breadboard, o ESP32, os módulos e o suporte reais antes de usar esta disposição como gabarito.

Verificação: as quatro vistas foram compiladas em CSG no OpenSCAD com `--hardwarnings`, sem avisos. Essa verificação confirma a compilação, não a ausência de interferências volumétricas nem o encaixe dos componentes reais. A exportação de prévia PNG não estava disponível por falta de conexão OpenGL/X neste ambiente.
