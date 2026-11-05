# Revisão dimensional R2 — 04/11/2026

A revisão compara as cotas do SCAD com os STL exportados e com a posição montada das amostras. A medição de diâmetros é feita por cortes nas malhas, sem depender apenas dos valores declarados no código. Unidades: milímetros.

## Correções aplicadas

1. **Canal da baioneta:** antes, o pino girava apoiado no piso do canal e sobravam 0,6 mm apenas acima dele. O piso foi deslocado para garantir **0,3 mm abaixo e 0,3 mm acima**, na posição de giro. No assento final, o colar apoia na tampa e sobra 0,3 mm sob o pino; o pino não precisa tocar o fundo ao mesmo tempo que o colar. O giro permanece em 30° e o levantamento nominal para liberar permanece em 1,2 mm.
2. **Amostra da tampa:** mantida a plaqueta corrigida de 16 mm de altura. Acrescentada uma **guia externa** que encosta na face externa da plaqueta e posiciona a lingueta com a mesma folga de 0,3 mm da peça final. Antes, essa posição dependia de quem segurava a amostra. A guia pertence somente à amostra.

Foram atualizados `estacao_integrada.scad`, `STL/tampa_caixa.stl`, `STL/teste_baioneta.stl`, `STL/teste_tampa.stl`, as ilustrações e o manual. A geometria das demais peças foi preservada. Use esses arquivos da R2; se já imprimiu os testes anteriores de tampa e baioneta, reimprima os pares. Se a tampa final já estiver impressa, ela também corresponde ao canal anterior.

## Cotas conferidas

| Região | Cota / folga conferida |
| --- | --- |
| Corpo da caixa, sem a cobertura lateral | 120 × 80 × 50 |
| Vão interno da caixa | 114 × 74 |
| Saia de encaixe da tampa | 113,4 × 73,4 |
| Folga tampa–caixa | 0,3 por lado; 0,6 total em cada eixo |
| Lingueta da tampa | 12 de largura; 1,4 de espessura; 16 de comprimento |
| Janela da trava | 13 de largura; 4,2 de altura |
| Folga entre gancho e janela | 0,5 de cada lado; 0,3 abaixo e 0,4 acima |
| Gancho da tampa | 0,9 de engate além da parede interna; precisa recuar geometricamente 1,2 para entrar |
| Soquete da baioneta, diâmetro livre medido no STL | 42,60000 a 42,62282 |
| Tubo, diâmetro externo medido no STL | 41,97751 a 42,00000 |
| Folga radial garantida entre tubo e soquete | Pelo menos 0,3 |
| Tubo, diâmetro interno medido no STL | 37,97965 a 38,00000 |
| Canal da baioneta / altura do pino | 4,2 / 3,6 |
| Parede externa preservada atrás do canal | 1,7 nominal |
| Baioneta | 30° de giro; 1,2 de levantamento nominal |
| Pino / furo das aletas | Corpo nominal 6,4; furo livre medido 7,00000 a 7,00375 |
| Cabeça das aletas / fenda | 8 de largura máxima; fenda de 1,6 |
| Passagem da cabeça comprimida | Recuo de 0,5 por metade resulta em raio máximo 3,5 e fenda restante de 0,6 |
| Portinha: abertura / aba de encaixe | 30 × 20 / 29,6 × 19,6; folga de 0,2 por lado |
| Portinha: dimensão entre ressaltos opostos | 30,3 × 20,3; interferência de 0,15 por lado apenas nos ressaltos |
| Passo / sobreposição vertical das saias | 18 / 4,4 |
| Altura total, com cinco aletas | 195,4 |

As pequenas faixas de diâmetro decorrem das facetas do STL, não de uma variação na peça impressa. Os furos de encaixe são compensados no SCAD para preservar o vão mínimo entre facetas. O interior de 38 mm do tubo é nominal e não foi compensado; a passagem central de cabos de 20 mm possui compensação própria.

## Medidas para identificar as amostras na mesa

| Arquivo | Peça receptora | Peça de encaixe |
| --- | --- | --- |
| `teste_baioneta.stl` | Ø 60 × 18 de altura total | Ø 56 × 21 de altura total |
| `teste_tampa.stl` | 20 × 3 × 16 | 20 × 10 × 19, incluindo a aba e a guia |
| `teste_aletas.stl` | 20 × 20 × 18 | 20 × 20 × 22,2 |

As alturas são das peças separadas na orientação de impressão. A plaqueta da tampa mede 16 mm; a altura máxima do arquivo com as duas peças é 19 mm, devido à peça da lingueta. Não confundir essas duas medidas.

## O que foi verificado

- Exportação de nove STL: seis peças com um sólido fechado cada e três pares de amostras com dois sólidos cada; faces consistentes e Z mínimo igual a zero.
- Contatos e movimentos calculados com **96 segmentos, a mesma resolução dos STL**.
- Baioneta: entrada em diferentes alturas; giro em 0°, 5°, 10°, 15°, 20°, 25° e 30°; levantamento em 0,3, 0,6, 0,9 e 1,2 mm no final do giro; retenção contra retorno sem levantar e retirada sem girar.
- Portinha montada: interferência restrita aos quatro ressaltos previstos, sem sobreposição volumétrica fora deles.
- Amostras reais dos STL montadas digitalmente: baioneta, tampa com guia e aletas.
- Contorno da cabeça das aletas comprimida para confirmar passagem pelo diâmetro livre do furo. Essa verificação trata o deslocamento geométrico das metades e não simula a deformação ou a resistência do material.

Os registros detalhados estão em `validacao.json` e `auditoria_medidas.json`. A tolerância numérica de volume nas operações com STL é 0,0001 mm³, para acomodar arredondamento float32 em superfícies que se tocam. Não é uma tolerância de fabricação.

Os testes de bancada do manual continuam necessários para confirmar força de encaixe, recuperação das linguetas, retenção e influência do material e do perfil de impressão. As amostras não validam a carga suportada, a vedação nem a precisão meteorológica.
