# Revisão V4 — painéis obrigatoriamente 500 × 380 mm

**Esta é a versão atual. Substitui a proposta V3 de 500 × 500 mm.** Os dois painéis novos — fundo C0 e tampo removível C1 — têm **exatamente 500 × 380 mm**, são de MDF nominal de 3 mm e **não possuem nenhum furo**, inclusive de fixação. A caixa pronta mede **500 × 380 × 50 mm**.

Comece pelo [guia ilustrado de montagem](05_GUIA/Guia_de_montagem.pdf). Veja também a [prévia 3D](05_GUIA/Previa_3D.png) e a [planta interna](05_GUIA/Planta_interna.png).

## SVG e DXF conferidos e corrigidos

Os SVG anteriores usavam traço de 0,05 mm, quase invisível ao ajustar o desenho à janela. Agora cada contorno tem traço preto explícito de **0,35 mm**. Os dois painéis lisos contêm **somente um retângulo externo**, coincidente com a borda da página; não há detalhes internos por serem peças sem furos. Para ver as outras peças, abrir `02_CHAPA_600x400/PAREDES_E_REFORCOS.svg` ou os individuais de `03_PECAS`.

Os DXF anteriores tinham estrutura mínima que não era importada corretamente pelo Inkscape. Foram acrescentadas as seções e tabelas necessárias, camada `CORTE` visível, cor explícita e limites do desenho. **Os 12 pares SVG/DXF foram relidos, comparados e renderizados; as coordenadas e medidas originais foram preservadas.**

- [Prévia das nove peças](05_GUIA/Previa_dos_cortes.png): imagem para visualização, sem escala de fabricação.
- [Conferência visual SVG e DXF, lado a lado](05_GUIA/Conferencia_SVG_DXF.pdf): gerada dos arquivos reais; as prévias DXF vêm do importador independente do Inkscape.
- [Relatório da conferência dos 12 pares](05_GUIA/CONFERENCIA_SVG_DXF.json): contagem de contornos, equivalência, dimensões e hashes dos cortes.

A espessura do traço é apenas de exibição. Cortar pelo eixo vetorial; **não converter o traço em contorno**, não criar deslocamento a partir de sua espessura e não redimensionar pela caixa visual que inclui o traço. A peça é definida pelas coordenadas: os painéis continuam exatamente **500 × 380 mm**. No Inkscape, usar zoom para o desenho/seleção; no CAD, ajustar a vista para todos os objetos. Importar DXF em milímetros, sem ajuste automático para A4.

## Compatibilidade com as peças já cortadas

São reaproveitadas **todas as 46 peças da estrutura e o tampo existente de 500 × 380 com seus 25 encaixes**, sem cortar ou furar peças antigas. Após lixar os dentes rentes, o fundo novo C0 é colado sobre o tampo existente, alinhando as quatro bordas. A caixa mantém a inclinação de 9,09°; não há aumento do contorno nem abas novas.

O acesso à eletrônica é pelo painel superior removível. Como o fundo fica integralmente apoiado e colado ao tampo antigo, **a fixação passa para as paredes frontal e traseira**: quatro parafusos em cada uma, na horizontal, entram em tacos de madeira colados **somente à face inferior de C1**. Ao retirá-los, o painel sai com os tacos e três nervuras; as placas ficam no fundo. Não colar C1 às paredes, nem tacos ao fundo ou às paredes.

O guia original sugere manutenção inferior; nesta adaptação o acesso superior evita modificar a grelha e o corpo fechado já fabricados, mantendo os módulos e o microSD acessíveis.

## Cortes e materiais

| Peça/material | Quantidade | Arquivo ou medida |
|---|---:|---|
| C0_BASE — MDF 3, sem furos | 1 | **500 × 380**: [DXF](01_CORTE_PAINEIS/C0_BASE_500x380.dxf) / [SVG](01_CORTE_PAINEIS/C0_BASE_500x380.svg) |
| C1_TAMPO_LISO — MDF 3, sem furos | 1 | **500 × 380**: [DXF](01_CORTE_PAINEIS/C1_TAMPO_LISO_500x380.dxf) / [SVG](01_CORTE_PAINEIS/C1_TAMPO_LISO_500x380.svg) |
| Paredes e três nervuras — MDF 3 | 1 chapa 600 × 400 | Sete peças: [DXF](02_CHAPA_600x400/PAREDES_E_REFORCOS.dxf) / [SVG](02_CHAPA_600x400/PAREDES_E_REFORCOS.svg) |
| Tacos de madeira maciça | 8 | 20 × 20 × **44**; 44 é a altura entre fundo e painel |
| Parafusos de madeira, cabeça panela | 8 | **3 × 16**, com oito arruelas de diâmetro externo aproximado 7 |
| Abraçadeira de nylon | 1 | Tira compatível com os rasgos 3 × 8 da parede traseira |
| Cola e suportes isolantes/removíveis | Conforme montagem | Conferir placas e falante reais |

Frente e traseira: **494 × 44**, entre as laterais de **380 × 44**. Nervuras NX1/NX2: **494 × 30**; NY: **374 × 30**. Os arquivos de `03_PECAS` repetem as peças já incluídas nos painéis e na chapa; são alternativas para reposição, não unidades adicionais.

Vetores em **mm, escala 1:1, sem compensação de feixe**. Aplicar compensação uma vez no CAM. As meias-madeiras têm ranhuras 3,15 para MDF 3; testar com retalho e ajustar por lixa se necessário. Não alterar a escala para corrigir espessura.

A chapa das paredes mantém área útil **560 × 360**, margens de 20 e intervalos de 8. Os painéis 500 × 380 usam arquivos próprios e o processo do tampo inteiro v2, em máquina cuja área útil comporte seu contorno ou serra com guia. **A profundidade 380 não cabe na área útil 360 reservada à chapa das paredes.** Nenhum painel deve ser dividido ou ampliado.

## Fechamento e eletrônica

- Tacos nos centros `x=30, 150, 400, 470`, com `s=13` e `s=367`. Coordenadas desde o canto dianteiro esquerdo, sobre o plano inclinado. [CSV de montagem](05_GUIA/Coordenadas_montagem.csv).
- Parafusos horizontais a **35 mm sobre a face inferior de C0**, equivalentes a **32 mm acima da borda inferior de cada parede**. Furos Ø3,5 somente nas paredes, sem escareamento. Transferir os centros a seco para os tacos; pré-furar Ø2, cerca de 13 de profundidade, conferindo a madeira real. Apertar sem esmagar o MDF.
- Vão interno **44**; sob as nervuras há **14** para fios. Nervuras em `s=110`, `s=240` e `x=250`, solidárias ao painel removível.
- Grade de som na frente. Entalhe USB **24 × 14** na traseira e dois rasgos **3 × 8** na mesma parede para alívio de tração. Essas passagens continuam acessíveis após colar o fundo ao tampo antigo.
- Os volumes verdes da planta são **reservas a confirmar com os componentes reais**: ESP32/protoboard 200 × 95 × 32; DFPlayer 100 × 95 × 32; falante 72 × 35 × 38. Conferir suportes, jumpers e conectores. Usar fixação isolante para placas e suporte próprio para o falante; não usar a grade como suporte.
- A caixa impressa antiga de altura 80 foi preservada como histórico, mas **não cabe no vão interno de 44 e não faz parte desta montagem**.

## Mapa e futuros botões

**O gabarito anterior do mapa tem 500 × 500 mm e não é compatível diretamente com o painel de 500 × 380.** Rever sua implantação antes de colar; recortar as margens ou reduzir indiscriminadamente a escala pode afetar a distribuição, o espaço tátil e o Braille. Esta revisão entrega a caixa e os painéis lisos; não altera as peças nem o gabarito existentes da maquete.

O [plano de 500 × 380 em escala 1:1](05_GUIA/Planejar_botoes_500x380_1_1.pdf) serve para anotar a futura distribuição; **não é arquivo de corte**. Informar depois centro `(x,s)`, diâmetro/contorno de instalação, profundidade, curso e tampa de cada botão. Reservar inicialmente 15 de cada lado dos eixos das nervuras e 30 nas bordas, conferindo todo o corpo e seus fios. As nervuras novas podem ser revistas sem alterar o pedestal antigo. Nenhuma correspondência entre os 18 marcadores da maquete e os 10 botões do guia foi presumida.

## Altura e lastro

O painel novo fica 53 mm acima do antigo na direção perpendicular à chapa, cerca de **52 mm na vertical**. Face superior, antes do relevo: frente **91,5 cm**, centro **94,5 cm**, traseira **97,5 cm**. Conferir alcance e rigidez no protótipo.

Mantidas as hipóteses estáticas do v2 — força horizontal 20 N, fator 1,5, base com semiprofundidade 0,17 m, piso plano e massa centrada — adota-se esforço a **1,02 m**, incluindo margem para o relevo: `m = 1,5 × 20 × 1,02 / (9,81 × 0,17) = 18,35 kg`. A referência passa a **pelo menos 19 kg de massa total**, substituindo os 17 kg do pedestal anterior. Pesar o conjunto e completar com lastro imobilizado, centrado sobre B3, antes de fechar H1; não carregar H1/H2 ou a caixa. Se não houver acesso ao lastro, avaliar a fixação ao piso prevista no manual v2.

O cálculo não define carga máxima no painel nem cobre apoio do peso do corpo. Nesse caso permanece a orientação original de fixação ao piso e avaliação estrutural. Alterações nas hipóteses ou na altura exigem novo cálculo. Conferir fisicamente colagens, encaixes, flexão e funcionamento.

## Modelos e verificações

[Caixa com o sistema eletrônico montado](04_MODELO_3D/Caixa_com_sistema_eletronico.scad): abrir no OpenSCAD e pressionar **F5**. Contém ESP32 sobre protoboard, DFPlayer com microSD, resistor de 1 kΩ, alto-falante, cabo USB, fios e **dez botões com posições apenas ilustrativas**. A vista inicial tem tampa e paredes transparentes. O parâmetro `vista` permite `inspecao`, `fechada`, `aberta`, `sem_tampa` e `eletronica`; `mostrar_pedestal=true` inclui o pedestal. `posicoes_botoes` permite mover os botões no plano de 500 × 380.

Os componentes têm dimensões aproximadas e a fiação mostra funções do guia, sem reproduzir a pinagem física de uma placa comercial. Essa cena serve para visualizar a montagem, não para orientar ligações ou fabricar componentes. Os furos de passagem dos botões existem **somente na representação visual desse SCAD**; os SVG/DXF e os dois painéis de fabricação permanecem lisos. Para ocultá-los também na cena, usar `furos_apenas_visuais=false`.

[Modelo OpenSCAD](04_MODELO_3D/Pedestal_com_caixa.scad): modos `conjunto`, `caixa`, `explodido`, `peca2d` e `peca3d`. `mostrar_tampa=false` revela o interior e `mostrar_reservas=true` exibe volumes indicativos. O modelo inclui uma cópia geométrica do pedestal original.

Na pasta original do projeto:

```sh
python3 adaptacao_caixa_eletronica_v4/06_FONTE/gerar_caixa.py
python3 adaptacao_caixa_eletronica_v4/06_FONTE/validar_e_visualizar.py
python3 adaptacao_caixa_eletronica_v4/06_FONTE/conferir_cortes.py
```

Requer Python, NumPy e Matplotlib; a validação também usa OpenSCAD. A conferência visual usa Pillow e Inkscape, com seu importador DXF Python em `/usr/share/inkscape/extensions/dxf_input.py` e Python do sistema; foi executada com Inkscape 1.1.2. [Requisitos](06_FONTE/requirements.txt), [geometria e parâmetros](06_FONTE/parametros_e_geometria.json), [verificação dos cortes](05_GUIA/VERIFICACAO.json), [validação 3D](05_GUIA/VALIDACAO_3D.json) e [hashes dos originais preservados](05_GUIA/ORIGINAIS_PRESERVADOS_SHA256.json) acompanham os arquivos. O [gabarito das paredes](05_GUIA/Gabarito_paredes_494x44_1_1.pdf) permite conferir a posição dos furos em 100%; cada parede mede 494 × 44. Verificações digitais não substituem testes físicos.
