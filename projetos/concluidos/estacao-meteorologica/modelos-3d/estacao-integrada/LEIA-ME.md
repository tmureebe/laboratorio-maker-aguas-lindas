# Estação meteorológica integrada por encaixes

## Alça interna no teto — atualização de 05/11/2026

O teto agora tem uma **alça interna integrada**, para suspender os sensores com abraçadeiras ou amarrações. Ela fica sob a cobertura, dentro do abrigo, e não abre furos no teto. Mede 32 mm de largura, 22 mm de projeção para baixo e 6 mm de profundidade, com espessura nominal de 3,2 mm nas laterais. A abertura afunila em direção à ponta; os sensores podem ser presos à alça, sem precisar passar suas placas pelo vão.

No OpenSCAD, use `visualizacao="corte"` para ver a alça montada, ou `visualizacao="teto"` para inspecionar/exportar o teto na posição de impressão. Os parâmetros estão em **Alca interna para sensores**; `alca_sensores=false` recupera o teto sem alça. Na orientação de impressão original, as diagonais da alça fecham o vão a 45°. A adequação ao material e ao perfil deve ser conferida no fatiador.

O arquivo `STL/teto.stl` foi atualizado junto com o SCAD. A alça fica dentro da abertura central de 60 mm das aletas, preservando os encaixes. Os rasgos da base continuam disponíveis como outra posição de fixação. A posição dos sensores e o percurso dos fios no arquivo ilustrativo com circuito não foram ajustados para esta nova opção de suspensão.

A conferência específica desta alteração está em `validacao_alca_teto.json`. Os relatórios R2, o manual e as imagens anteriores documentam a versão anterior do teto.

## Revisão dimensional R2

Use os arquivos atualizados da revisão R2 diretamente nesta pasta. A revisão completa está em **`REVISAO_MEDIDAS_R2.md`**, com medições das malhas em `auditoria_medidas.json`.

- O canal da baioneta agora deixa 0,3 mm acima e abaixo do pino na posição de giro e 0,3 mm sob ele no assento final. Isso evita exigir que o colar e o pino toquem simultaneamente os respectivos assentos.
- A amostra da tampa recebeu uma guia externa para reproduzir a folga de 0,3 mm sem depender do posicionamento manual. A plaqueta continua com 16 mm de altura.
- Arquivos de fabricação alterados: `estacao_integrada.scad`, `STL/tampa_caixa.stl`, `STL/teste_baioneta.stl` e `STL/teste_tampa.stl`. Se já imprimiu os testes de tampa e baioneta anteriores, reimprima esses pares com os arquivos atuais. A tampa final anterior também possui o canal antigo.
- Foram aprovadas 32 verificações de encaixe, movimento e retenção, com 96 segmentos, além da conferência das nove malhas e de cortes dos STL para medir os diâmetros livres.

## Manual ilustrado dos testes

**`manual_testes_encaixes.pdf`** contém seis páginas para uso na bancada: identificação e preparo das amostras, montagem e desmontagem da baioneta, da trava da tampa e dos pinos das aletas, critérios de aprovação, exemplos de ajustes e ficha de registro. As ilustrações mostram as malhas reais das amostras; os cortes explicativos são esquemáticos.

**Revisão da amostra da tampa:** em 04/11/2026, a plaqueta receptora de `STL/teste_tampa.stl` foi corrigida de 20 para 16 mm de altura. A altura anterior impedia que a aba assentasse quando o gancho alcançava a janela. Se já imprimiu a versão de 20 mm, reimprima essa amostra. Naquela correção inicial, as peças finais não foram alteradas; a revisão R2 acima também altera o canal da tampa final. O par revisado foi conferido montado digitalmente, com contato plano e sem sobreposição volumétrica.

Os fontes do manual estão em `manual/`: execute `python manual/gerar_figuras.py` para as imagens e `/usr/bin/python3 manual/gerar_manual.py` para o PDF (requer NumPy/Matplotlib/Pillow no primeiro ambiente e ReportLab no segundo).

Abra **`estacao_integrada.scad`** no OpenSCAD. O arquivo é independente: toda a geometria está nele, sem importar STL ou bibliotecas externas. As medidas estão em milímetros. A visualização inicial mostra o conjunto montado.

O projeto integra a caixa e o abrigo dos sensores com peças desmontáveis:

- **Caixa → tampa:** duas linguetas flexíveis prendem nas janelas das paredes maiores. A saia interna guia e centraliza a tampa. As janelas permitem apertar as linguetas para abrir.
- **Tampa → abrigo:** três pinos no tubo entram no soquete da tampa. Gire 30° e deixe o abrigo descer 1,2 mm até o assento final da baioneta. Para desmontar, levante 1,2 mm, gire de volta e retire. O assento em J bloqueia o giro de retorno enquanto o conjunto está apoiado.
- **Base → aletas → teto:** três pinos bipartidos por união, com janelas para destravar. O teto é fechado.
- **Portinha de serviço:** encaixe por pressão na abertura lateral de 30 × 20 mm, com unha para puxar.

As uniões entre os componentes impressos não usam parafusos ou cola. A base do abrigo tem quatro rasgos de 3 × 9 mm para pequenas abraçadeiras de fixação dos módulos sensores; as dimensões das placas não foram presumidas. A passagem central de cabos tem diâmetro livre nominal de 20 mm.

## Dimensões iniciais

| Elemento | Medida |
| --- | --- |
| Corpo da caixa | 120 × 80 × 50 mm |
| Paredes / fundo | 3 mm / 3 mm |
| Vão interno da caixa antes de considerar os encaixes | 114 × 74 × 47 mm |
| Tampa, incluindo beiral | 124 × 84 mm |
| Profundidade da saia interna | 16 mm |
| Soquete interno da baioneta | Ø livre nominal 42,6 mm; Ø externo 52,2 mm |
| Tubo do abrigo | Ø externo 42 mm; Ø interno 38 mm; comprimento 50 mm |
| Penetração do tubo abaixo do topo da tampa | 18 mm |
| Colar que cobre a entrada da baioneta | Ø 56 mm |
| Diâmetro dos pratos | 140 mm |
| Abertura das aletas / passo | 60 mm / 18 mm |
| Aletas intermediárias | 5 |
| Altura do conjunto montado | 195,4 mm |

A cobertura da porta de serviço avança 5 mm para fora do corpo; o STL da caixa mede, portanto, **125 × 80 × 50 mm** no total. O abrigo determina a largura e a profundidade máximas do conjunto: 140 × 140 mm.

O soquete ocupa a região central dos 15 mm superiores do interior da caixa, e a saia ocupa 16 mm junto às paredes. Considere essas regiões ao posicionar o ESP32, a bateria e os demais módulos.

## Quais peças imprimir

Os STL já estão na orientação de impressão, com Z mínimo igual a zero.

| Arquivo em `STL/` | Quantidade | Orientação |
| --- | ---: | --- |
| `caixa.stl` | 1 | Fundo na mesa |
| `tampa_caixa.stl` | 1 | Face externa plana na mesa; saia e soquete para cima |
| `portinha.stl` | 1 | Face externa plana na mesa; aba de encaixe para cima |
| `base_abrigo.stl` | 1 | Face plana central na mesa; tubo para cima |
| `aleta.stl` | 5 | Face plana na mesa; pinos para cima |
| `teto.stl` | 1 | Face externa plana na mesa; pinos para cima |

**Imprima primeiro as amostras** `teste_baioneta.stl`, `teste_tampa.stl` e `teste_aletas.stl`. Cada arquivo contém duas peças separadas. Use o material e o perfil previstos para o conjunto final.

- Na baioneta, vire o soquete para a posição de uso, alinhe os três pinos do tubo às entradas, pressione até o nível de giro, gire até o fim e deixe assentar. O tubo deve ficar retido e liberar depois de levantar e girar de volta. O colar da amostra não tem a concordância cônica da peça grande; as superfícies de encaixe são as mesmas.
- Na amostra da tampa, alinhe a lingueta por dentro da plaqueta que representa a parede: ela deve flexionar ao entrar e retornar quando o gancho alcançar a janela. Aperte o gancho pela janela para liberar.
- Nas aletas, comprima os pinos até as cabeças atravessarem os furos e os apoios encostarem. Confira a retenção e a liberação pelas janelas.

Confira no fatiador as pontes sobre a abertura lateral da caixa, as ranhuras internas do soquete, as pontes de aproximadamente 7 mm nas torres e as cabeças das linguetas. Avalie suportes nessas regiões sem preencher as folgas móveis. O colar do tubo tem uma concordância de 45° e os pinos da baioneta têm rampas para reduzir os avanços horizontais durante a impressão.

## Ajuste das folgas

Os valores são pontos de partida para prototipagem, sujeitos à precisão da impressora, ao material e à orientação das camadas.

| Parâmetro | Inicial | O que controla |
| --- | ---: | --- |
| `folga_tampa` | 0,30 mm por lado | Guia da tampa dentro da caixa |
| `espessura_lingueta` | 1,40 mm | Espessura das linguetas da tampa |
| `ressalto_tampa` | 0,90 mm | Engate dos ganchos além da face interna da caixa |
| `folga_tubo` | 0,30 mm radial | Tubo dentro do soquete |
| `folga_angular_baioneta` | 1° em cada borda | Passagem dos pinos pelos canais |
| `folga_axial_baioneta` | 0,30 mm | Altura extra do canal, em cada lado |
| `folga_encaixe` | 0,30 mm radial | Corpo dos pinos das aletas dentro dos furos |
| `ressalto_trava` | 0,50 mm | Retenção das cabeças bipartidas das aletas |
| `folga_portinha` | 0,30 mm por lado | Guia da portinha |
| `ressalto_portinha` | 0,15 mm | Interferência localizada dos ressaltos da portinha |

Se o tubo prender, aumente `folga_tubo` em pequenos passos e teste novamente. Se uma lingueta exigir força excessiva, reduza o ressalto correspondente e valide a retenção na amostra. Depois de qualquer alteração, exporte novamente **as duas peças de cada união afetada** e as respectivas amostras. Os STL desta pasta não são atualizados automaticamente pelo OpenSCAD.

## Montagem

1. Passe os fios pelo tubo e pelo furo de 20 mm da base. Posicione e fixe os sensores pelos rasgos da base, deixando suas aberturas expostas ao ar.
2. Com a tampa ainda fora da caixa, insira o tubo no soquete alinhando os três pinos às entradas. Gire 30° no sentido permitido pelos canais e deixe o conjunto descer ao assento final. O colar deve apoiar no topo da tampa. Pratique esse movimento na amostra.
3. Instale a eletrônica na caixa e conecte os fios, respeitando o espaço ocupado pelo soquete. Alinhe a saia da tampa e pressione perto das duas linguetas até os ganchos engatarem nas janelas.
4. Empilhe as cinco aletas na base. Pressione junto às três torres de cada nível até os apoios encostarem. Encaixe o teto por último.
5. Pressione a portinha na abertura lateral.

Para abrir a caixa, comprima os dois ganchos pelas janelas e levante a tampa. Para separar o abrigo, segure a tampa, levante o abrigo aproximadamente 1,2 mm, gire de volta e retire. Para desmontar a pilha, comece pelo teto e comprima as cabeças dos pinos pelas janelas; uma pinça pode ajudar. Não use as saias dos pratos como alavanca.

## Visualização e exportação no OpenSCAD

Altere `visualizacao` no início do arquivo ou no Customizador:

| Valor | Resultado |
| --- | --- |
| `"montado"` | Conjunto completo na posição de uso |
| `"explodido"` | Peças separadas para entender a montagem |
| `"corte"` | Meio conjunto, para inspecionar o interior |
| `"pecas"` | Uma unidade de cada tipo, distribuídas na mesa |
| `"caixa"`, `"tampa_caixa"`, `"portinha"` | Peça individual da caixa, pronta para exportar |
| `"base_abrigo"`, `"aleta"`, `"teto"` | Peça individual do abrigo, pronta para exportar |
| `"teste_baioneta"`, `"teste_tampa"`, `"teste_aletas"` | Pares de amostras |

Renderize a peça escolhida com **F6** e use **Arquivo → Exportar → Exportar como STL**. Exporte cada tipo separadamente; o modo montado contém contatos entre peças e não é a disposição para impressão. A distribuição de todas as peças excede mesas pequenas; imprima os STL individualmente.

Exemplo de exportação pela linha de comando:

```bash
openscad --export-format binstl -o base_abrigo.stl \
  -D 'visualizacao="base_abrigo"' estacao_integrada.scad
```

## Referência e conferência

As dimensões da caixa e da abertura lateral vêm de `../caixa_com_tampas.scad`. Os pratos, o passo e os encaixes axiais vêm de `Stevenson_geometrico/stevenson_geometrico.scad` (fonte local de referência, registrada em `referencia_modelo.json`). Foram acrescentados a tampa vazada com linguetas, o soquete, os canais em J, os pinos e o colar do tubo, a portinha por pressão e os rasgos de fixação dos sensores. Os arquivos anteriores foram preservados.

**Esta é uma versão para fabricar o conjunto integrado.** As janelas de trava da caixa e a baioneta do tubo não existem nos STL antigos; não se deve presumir que as peças já impressas tenham essas interfaces.

`validacao.json` registra a conferência pelo OpenSCAD 2021.01: seis tipos de peça com um sólido fechado cada, três amostras com dois sólidos cada, faces com orientação consistente e base de impressão em Z=0. As verificações de montagem confirmaram ausência de sobreposição volumétrica entre caixa e tampa, tampa e abrigo travado, caixa e abrigo e os pares de pratos. Foram verificadas as posições de entrada, meio e fim do giro da baioneta, além do bloqueio geométrico para retirar sem girar ou retornar sem levantar. Os testes de interferência e os STL fornecidos usam 96 segmentos. O conjunto de 32 verificações inclui os pares de amostras montados e mais posições do percurso da baioneta; resíduos de contato até 0,0001 mm³ são tolerados apenas como arredondamento numérico dos STL, sem relação com tolerância de fabricação.

A portinha tem interferência intencional de 0,15 mm nos ressaltos; as linguetas também precisam flexionar durante a montagem. A conferência é digital: força de encaixe, retenção, vida das travas, vedação e resposta dos sensores ainda dependem do protótipo físico. O beiral, o colar e o abrigo não estabelecem grau de proteção IP.

Para repetir a conferência: `python validar_modelo.py` (OpenSCAD e NumPy). Para regenerar as imagens das medidas iniciais: `python gerar_previas.py` (NumPy e Matplotlib). As prévias mostram as malhas efetivas dos STL, com escala separada nas vistas montada e explodida.

## Documentação no repositório

Veja o [guia de montagem completa](../../guias/montagem-integrada.md), o [esquema elétrico](../../circuito/README.md) e as [instruções da versão com circuito](CIRCUITO_MONTADO.md).

Os relatórios R2 preservam as medições de 04/11/2026, anteriores à alça do teto e ao ajuste de `folga_portinha` para 0,30 mm. Para a abertura de 30 × 20 mm, a aba atual mede 29,4 × 19,4 mm. O relatório específico da alça acompanha os arquivos atuais.
