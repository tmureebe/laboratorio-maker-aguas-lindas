# Verificação do modelo · V7

Resultado: **PASSOU**. Conferência digital, sem ensaio físico.

| Conferência | Resultado |
|---|---|
| STL de fabricação, incluindo alternativas/testes | 30 malhas fechadas, sem triângulos degenerados, volume positivo |
| Chapas MDF | 7 chapas; limites 600 × 400; margens e quantidades conferidas |
| Novo apoio da câmara M23 | X=350, patamar 60, furos compatíveis com B01 |
| Moldura corrigida | Altura livre de 120 em X=210 e 390, na região fechada sobre o canal |
| Interfaces alteradas versus vizinhos | 90 interseções booleanas; nenhuma acima de 0,01 mm³ |
| Asas A e B | Envelopes nos cinco ângulos e 40 interseções contra câmara, moldura, suporte e acrílico |
| Cinco partes recebidas | Hashes originais preservados |

## Alterações feitas após a revisão

1. O teto da moldura V5 ficava em Z=180,8, acima do piso interno Z=62,4: a altura local era 118,4. O rebaixo V7 eleva o teto interno a Z=182,4 sem alterar furos ou apoios externos. O canal nominal passa a ter 120 mm também nos trechos cobertos da janela.
2. A câmara passou a ter seu próprio apoio M23, em X=350, evitando sustentar seu peso somente pelas luvas. O patamar é 60 mm; os apoios dos dutos têm 59,4 mm. O painel e os mapas incluem os dois furos adicionais.
3. Os parafusos do painel foram revistos de M4 × 16 para M4 × 20 para acomodar pilha nominal de 12 mm, porca e arruelas. Conferir ferragens reais.
4. A montagem foi reconstruída com todas as peças finais e referências comerciais, em uma pasta independente. As peças substituídas V5 não estão na pasta de impressão padrão.

## Alcance da verificação

Os testes booleanos examinam pares com sobreposição de envelopes nas interfaces alteradas: MDF, novas conexões, moldura e componentes vizinhos. Contatos coplanares de apoio não são tratados como colisões. Foram acrescentadas 40 interseções das duas asas nos cinco ângulos contra câmara, moldura, suporte e acrílico: total de 130 testes booleanos. Ventoinha/célula são referências simplificadas; ferragens não foram modeladas.

Ainda dependem de teste físico: tolerâncias de corte/impressão, acabamento, encaixe após selagem, rigidez da base de 6 mm, vedação, vibração e medição. Não houve CFD nem cálculo estrutural.

O relatório detalhado, com nomes dos pares, volumes, dimensões e hashes, está em 06_CAD_VALIDACAO/relatorio_verificacao.json.
