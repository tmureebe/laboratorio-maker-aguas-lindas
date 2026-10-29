# Manual de medições complementares — V7

**MM-V7 · Revisão 03 · 13/10/2026 · Unidades em mm**

[Manual ilustrado de cinco páginas](Guia_Ilustrado_Medicoes_Parafusos_V7.pdf), com ficha de levantamento na página 5.

## 1. Finalidade e preparação

Levantar apenas os dados que faltam para definir a compra das ferragens. Parafusos, porcas e arruelas ainda não foram comprados.

Separe paquímetro de 200 mm, célula de carga, ventoinha e identificação/documentação desses componentes. Se a documentação confirmar uma informação, registre a fonte e dispense a medição correspondente. A ventoinha deve estar desconectada.

Este procedimento considera peças conforme a V7. Se houve alteração de painel, vedação, peça ou montagem, identifique apenas a alteração na ficha.

## 2. Cotas já conhecidas: usar os dados digitais

As cotas abaixo foram extraídas das malhas montadas da V7. Não repetir essas medições no levantamento de pré-compra.

| Local | Cota nominal, sem ferragens |
|---|---|
| Fixação inferior da célula pela base 14 | 17 mm antes da entrada na célula |
| Fixação superior da célula por espaçador 15 + suporte 16 | 3 + 5 = 8 mm |
| Janela: orelha da câmara + moldura no furo + espaçador + presilha | 10 + 4 + 3,5 + 3 = 20,5 mm |
| Parte 1 + grade 09 + espaçador 20 + parte 2 | 12 + 3,2 + 8 + 8 = 31,2 mm |

Na janela, o acrílico fica ao lado do parafuso e não integra a pilha atravessada. Não furar a tampa. O fornecedor deve somar à pilha de 20,5 mm as arruelas, a porca e a sobra necessária para definir o comprimento comercial. M3 × 25 é a referência inicial, a comparar com a ferragem oferecida.

Os modelos de célula e ventoinha são referências comerciais simplificadas. Suas roscas e características reais não são confirmadas pelos STL; por isso entram nos procedimentos seguintes.

## 3. Procedimento 01 — célula de carga

1. Identifique os quatro furos em uma foto: F1/F2 na extremidade fixa à base 14; M1/M2 na extremidade móvel que recebe as peças 15 e 16.
2. Consulte marca/modelo e manual para identificar rosca e passo de cada furo. Sem identificação, leve a célula à loja para avaliação com calibres adequados. Não é necessário comprar parafusos alternativos para descobrir a rosca.
3. Observe se o furo tem fundo ou atravessa a célula. Em furo cego, apoie a extremidade do paquímetro na entrada e meça a profundidade com a haste, sem pressionar. Se a haste não alcançar corretamente, registre a limitação.
4. Confirme a entrada mínima e máxima permitidas pelo fabricante ou por avaliação apropriada. A profundidade física, isoladamente, não informa quanto do furo tem rosca utilizável. Em furo passante, registre eventuais restrições à saída da ponta.
5. Preencha a ficha do manual. Dado desconhecido: escreva “pendente”. Não é preciso medir novamente os 17 mm e 8 mm das peças impressas.

Para selecionar o parafuso, use: pilha CAD de 17 mm no lado fixo ou 8 mm no móvel, mais a arruela escolhida, mais uma entrada na célula dentro dos limites confirmados. O fornecedor pode selecionar o comprimento com esses dados. Os dois lados podem usar roscas ou comprimentos diferentes.

## 4. Procedimento 02 — ventoinha

Se a documentação confirmar espessura de 30 mm nos pontos de fixação e furação de 105 × 105 mm, registre a fonte e encerre esta etapa. Caso contrário:

1. Meça a espessura entre as faces de apoio nos quatro cantos, identificados como C1 a C4. Use os bicos externos do paquímetro, como na figura 3 do manual.
2. Registre a distância entre centros na horizontal e na vertical. Para furos iguais: distância externa entre os dois furos menos o diâmetro de um furo.
3. Compare com o passo de 105 × 105 mm das peças digitais. Furação diferente exige compatibilizar as peças; trocar o comprimento do parafuso não corrige o alinhamento.

A espessura real é usada para conferir a referência M4 × 55. Não medir novamente as peças impressas da grade ou do regulador para este levantamento.

## 5. Referências de compra

| Uso | Quantidade | Referência V7 |
|---|---|---|
| Célula fixa | 2 | Rosca e comprimento definidos com os dados da célula; pilha CAD de 17 mm |
| Célula móvel | 2 | Rosca e comprimento definidos com os dados da célula; pilha CAD de 8 mm |
| Janela | 6 | M3; comprimento a fechar com a pilha CAD de 20,5 mm e as ferragens oferecidas |
| Pés e base do sensor | 16 | M4 × 20, painel conforme V7 |
| Ventoinha | 4 | M4 × 55; confirmar componente real |
| Grade e espaçador | 4 | M3 × 40 |
| Eixo da asa | 1 | M3 × 35 |
| Eixo do regulador | 1 | M4 × 20; arruela de retenção com externo próximo de 12 mm |
| Disco e alavanca | 2 | M3 escareado × 12; definir retenção por porca ou rosca receptora |
| Talas da base bipartida | 4 opcionais | M4 escareado × 20 |

Total nominal: **38 parafusos; 42 com as talas opcionais**. A opção de retenção da alavanca precisa ser definida, mas não exige repetir as dimensões do disco.

Leve a ficha da página 5 e a tabela ao fornecedor. Registre as porcas e arruelas usadas na escolha dos comprimentos; separe qualquer reserva da quantidade nominal. O comprimento da célula fica pendente enquanto sua rosca ou os limites de entrada não forem confirmados.

Após receber as ferragens, faça a conferência normal da montagem conforme o guia V7: assentamento, engate e liberdade de partes móveis. Essa validação não é uma medição prévia para a compra.

## Rastreabilidade

Fontes: `Tunel_Hibrido_V7_COMPLETO/06_CAD_VALIDACAO/montagem.json`, malhas de `montagem_REFERENCIA`, guia de montagem e lista de itens comprados V7. Memória das cotas extraídas em `manual_medicoes_v7/cotas_confirmadas.json`; procedimento de extração em `manual_medicoes_v7/conferir_cotas_cad.py`. As cotas são nominais do modelo, não medições físicas já realizadas.
