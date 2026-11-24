# Asa ampliada para o túnel V7 — 19/11/2026

**Imprimir uma unidade de [21_asa_ampliada_190x114mm.stl](01_IMPRIMIR/21_asa_ampliada_190x114mm.stl), em escala 100%.** Substitui a asa A ou B. Reutiliza o suporte 16 e o eixo M3 × 35 existentes.

- [Prancha de dimensões e montagem — PDF](04_VISUALIZACAO/Asa_ampliada_dimensoes.pdf)
- [Imagem de comparação com a asa antiga](04_VISUALIZACAO/Asa_ampliada_dimensoes.png)
- [Fonte editável OpenSCAD](02_FONTE/asa_ampliada.scad)
- [Relatório de verificação](03_VERIFICACAO/relatorio.json)

## Dimensões escolhidas

| Medida | Asa original A/B | Asa ampliada |
|---|---:|---:|
| Corda, na direção do vento | 40 mm | **190 mm** |
| Envergadura, transversal ao vento | 90 mm | **114 mm** |
| Área em planta, corda × envergadura | 36 cm² | **216,6 cm²** |
| Relação de áreas | 1 | **6,02** |
| Largura do encaixe entre as orelhas | 15 mm | 15 mm, preservada |
| Furo do eixo | Ø3,4 mm | Ø3,4 mm, preservado |

O perfil é curvado, com arqueamento máximo de 3,8 mm a 40% da corda, espessura nominal de 8% da corda e bordo de fuga de 0,8 mm para fabricação. A distribuição polinomial deriva da família de quatro dígitos, mas usa espessura aplicada verticalmente e engrossamento do bordo: não é um perfil NACA exato nem possui coeficientes aerodinâmicos medidos. A altura total do corpo aerodinâmico é aproximadamente 15,94 mm; incluindo o encaixe, o envelope impresso é **190 × 37,41 × 114 mm**.

## Por que este tamanho

O CAD existente define câmara com 200 mm de comprimento, largura interna de 120 mm, piso em Z=62,4 mm e passagem nominal com 120 mm de altura. Para o teto foi adotado conservadoramente Z=180,8 mm, abaixo do teto corrigido. O eixo atual fica em X=300, Y=0, Z=104,4 mm, no meio do comprimento da câmara. A linha de corda da asa fica 18 mm acima do eixo.

Foi adotada folga mínima nominal de **3 mm**, para permitir montagem, pequenas variações de impressão e movimento sem contato. A envergadura resulta de 120 − 2 × 3 = 114 mm. A corda de 190 mm é a maior medida inteira que atende a essa folga **para este perfil, eixo central e giro completo de −20° a +20°**. O gerador verifica que 191 mm ultrapassa o envelope reservado. Em zero grau há 5 mm de sobra em cada extremidade; ao girar, a distância vertical entre o perfil e o eixo faz a extremidade avançar mais.

Isso maximiza o tamanho geométrico dentro dessas condições. Não representa uma otimização da sustentação ou um limite universal para outros perfis, suportes e tolerâncias.

| Folga calculada ao longo de todo o giro | Mínimo |
|---|---:|
| Cada lateral | 3,00 mm |
| Extremidade de entrada | 3,29 mm |
| Extremidade de saída | 3,23 mm |
| Piso | 25,19 mm |
| Teto conservador | 25,03 mm |
| Corpo aerodinâmico sobre o suporte — limite conservador vertical | 5,66 mm |
| Encaixe entre as orelhas — de cada lado | 0,50 mm |

## Impressão

1. Usar o STL da pasta `01_IMPRIMIR`. As malhas em `03_VERIFICACAO` e `04_VISUALIZACAO` são referências de montagem, não peças adicionais.
2. Manter a ponta plana na mesa, como no STL: altura de impressão 114 mm. Aplicar brim, conferindo que a área útil da mesa comporta a peça de 190 mm e o brim.
3. Usar o perfil de PLA já validado no laboratório. Como ponto de partida para reduzir o peso, usar camada de 0,20 mm, três paredes e 10% de preenchimento; conferir massa e continuidade das paredes no fatiador. Esses parâmetros não foram validados em impressão física.
4. Aplicar preenchimento local de 100% no disco de fixação e no pescoço. Não imprimir toda a asa maciça: isso acrescentaria peso desnecessário ao sensor.
5. Habilitar suporte localizado sob o ressalto central e conferir o início do disco na prévia de camadas. O furo Ø3,4 deve ficar livre depois da remoção dos suportes. Não alargar as faces de apoio nem escalar a asa para corrigir esse encaixe.
6. Retirar rebarbas, conferir a passagem do M3 e medir corda e envergadura. Não engrossar o bordo de fuga com excesso de acabamento.

## Instalação

1. Desligar a ventoinha. Retirar presilhas, acrílico **e a moldura superior**. A abertura apenas do acrílico é menor que a asa; a câmara sem moldura permite entrada por cima.
2. Retirar a asa anterior. Conferir na montagem real se o eixo está centralizado transversalmente e a **100 mm de cada extremidade da câmara**. As folgas calculadas dependem dessa centralização.
3. Colocar o encaixe entre as orelhas do suporte 16. Reutilizar M3 × 35, arruelas e porca previstos no projeto. Não ampliar a fixação: ela foi copiada sem escala da asa B original.
4. Orientar o bordo arredondado para a entrada/colmeia e o bordo fino para a saída/ventoinha. No CAD, a entrada está em X=200 e a saída em X=400. A face mais arqueada fica para cima.
5. Ajustar 0° pela linha que liga bordo de ataque a bordo de fuga, não pela tangente à face curva. Travar suavemente e verificar manualmente todo o intervalo −20° a +20°. Não forçar o suporte para conseguir passagem.
6. Recolocar moldura, acrílico e presilhas. Conferir novamente folgas e liberdade da célula, hastes e fios.
7. Refazer tara sem vento e calibração com massas conhecidas após a troca. Começar as medições em 0°, 5° e 10°, com a mesma condição da ventoinha, registrando também o ruído e a leitura com o suporte sem asa.

A célula real registrada em [dimensões da célula de carga e da ventoinha](../../guias-e-ferragens/dimensoes_celula_de_carga_e_ventoinha.txt) mede 75,2 × 12,76 × 12,76 mm; o conjunto CAD antigo usa uma referência de 85 × 15 × 15 mm. Esta revisão conserva a interface da asa com o suporte existente. A posição física do suporte deve ser conferida na etapa 2; a referência antiga não valida a localização da célula real.

## O que esperar da medição

A força perpendicular ao escoamento é a **sustentação**. A área passou de 36 para 216,6 cm², mas não é possível afirmar que a força aumentará 6,02 vezes. A relação é `L = ½ ρ V² S CL`: a troca também altera o escoamento e o coeficiente de sustentação, e a velocidade real com a asa instalada ainda não foi medida. [Equação de sustentação — NASA](https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/lift-equation/).

Por ser a opção de maior tamanho, há interferência importante das paredes. A tabela abaixo calcula somente a projeção frontal do corpo da asa, dividida pela seção de 120 × 120 mm; não inclui suporte, esteira nem correção aerodinâmica de bloqueio.

| Ângulo positivo | Projeção frontal / seção do túnel |
|---|---:|
| 0° | 12,6% |
| 5° | 18,8% |
| 10° | 29,8% |
| 15° | 41,4% |
| 20° | 53,3% |

Por isso, ±20° é uma capacidade geométrica de ajuste, não uma recomendação para obter a maior força. Priorizar inicialmente ângulos baixos e observar a resposta. O bloqueio em túneis de baixa velocidade envolve volume, separação e esteira; esta peça não recebeu essas correções. [Referência técnica NASA-CR-152241](https://ntrs.nasa.gov/citations/19790024048).

Não foram informadas capacidade, resolução, calibração nem ruído da balança, nem a velocidade do ar. A geometria maior está pronta para fabricar; conseguir uma leitura útil precisa ser confirmado no ensaio. O dispositivo continua medindo uma componente de força, conforme o guia V7.

## Verificação e reprodução

- STL fechado, um único componente, orientação consistente, volume positivo e ausência de triângulos degenerados.
- Envelopes contínuos calculados pelos extremos analíticos das trajetórias dos vértices entre −20° e +20°, incluindo extremos entre ângulos amostrados.
- 54 interseções booleanas: nove ângulos contra câmara, moldura, suporte, acrílico, U01 e U02, sem volume de colisão.
- Folga entre corpo e suporte verificada em todo o intervalo com passos de 0,05° e margem adicional que limita o deslocamento entre amostras; o encaixe mantém 0,5 mm lateral até as orelhas.
- Preservados o furo Ø3,4 e a largura de 15 mm do encaixe original. Ferragens reais não foram modeladas.
- Sem ensaio físico, CFD, cálculo estrutural ou validação de impressão.

Na raiz do projeto:

```bash
/usr/bin/python3 fabricacao-v7/07_ASA_AMPLIADA/02_FONTE/gerar_e_verificar.py
PYTHONNOUSERSITE=1 MPLCONFIGDIR=/tmp/tunel-matplotlib /usr/bin/python3 fabricacao-v7/07_ASA_AMPLIADA/02_FONTE/desenhar.py
```

Dependências: OpenSCAD, NumPy e Matplotlib. A fonte usa o STL original B dentro do pacote V7; manter a estrutura de pastas. Equações de referência: [PDAS — distribuição de espessura](https://www.pdas.com/naca456thick4.html). Aqui o coeficiente final foi ajustado para fechamento e somado um termo linear para o bordo de fuga de 0,8 mm.

O visualizador completo e os PDFs anteriores da V7 continuam representando a montagem com a asa pequena. Para esta substituição, usar esta pasta e a prancha específica da asa ampliada.
