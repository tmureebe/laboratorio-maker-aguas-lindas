# Túnel híbrido V7 — pacote completo

Esta é a pasta única de fabricação e montagem. Não é necessário consultar as pastas V5 ou V6.

Comece pelo **04_DOCUMENTOS/01_GUIA_MONTAGEM.pdf** e pela **04_DOCUMENTOS/02_LISTA_FABRICACAO.pdf**. Para examinar o conjunto, abra **05_VISUALIZACAO/ABRIR_VISUALIZADOR_3D.html** no navegador.

| Pasta | Destino dos arquivos |
|---|---|
| 01_IMPRESSAO_3D | Impressora 3D: peças finais, alternativas e cupons em subpastas separadas |
| 02_CORTE_LASER | Laser: MDF de 3 mm, MDF de 6 mm e acrílico de 3 mm, separados por material |
| 03_COMPRADOS_NAO_FABRICAR | Comprar/reaproveitar: ventoinha, célula, ferragens e consumíveis; modelos comerciais apenas ilustrativos |
| 04_DOCUMENTOS | Guia ilustrado, quantidades, compras e resumo de verificação |
| 05_VISUALIZACAO | Vistas completas/explodidas, modelo 3D e mapas identificados; não fabricar esses arquivos |
| 06_CAD_VALIDACAO | Fontes editáveis, medidas, hashes e resultado das verificações |

## O que foi revisado

- Entrada de 50 mm e trecho de 150 mm permanecem unidos em um duto MDF de 200 mm; saída também em MDF de 3 mm.
- A moldura da janela foi corrigida: removeu-se o degrau interno de 1,6 mm, conservando fixações e tampa. Use **04_moldura_V7_passagem_120mm.stl**.
- A câmara ganhou apoio MDF próprio M23 em X=350. São **seis apoios**, feitos com **24 lâminas de MDF de 6 mm**.
- Parafusos da base foram revistos para M4 × 20, considerando a pilha de 12 mm mais porca e arruelas.
- A visualização contém o conjunto completo, sensor, asa, ventoinha, regulador e acrílico, com materiais separados.

## Fabricar sem duplicidade

Os 19 STL padrão representam 29 peças físicas, incluindo cinco peças recebidas que podem ser reaproveitadas. Imprima na quantidade indicada, individualmente, em escala 100%.

As alternativas não são peças adicionais: escolha apenas uma asa e uma ligação para a parte 5. Testes e gabaritos ficam fora da montagem final.

Cada chapa de corte já contém suas quantidades. Use os arquivos de chapas **ou** os desenhos individuais, e importe **SVG ou DXF**, nunca os dois para o mesmo corte. A base MDF bipartida é opcional. A tampa de acrílico pode ser reaproveitada.

Todos os cortes estão em mm, escala 1:1, sem compensação de kerf. Chapas MDF têm 600 × 400 mm com 5 mm de margem. Meça a espessura real e faça os cupons antes do lote.

Os arquivos de conjunto STL/OBJ, modelos comerciais e malhas MDF em CAD são para visualizar/conferir. As malhas MDF não substituem os SVG/DXF do laser. STL não conserva as cores; prefira o HTML ou o OBJ acompanhado de `materiais.mtl`.

## Estado da verificação

Passaram as verificações de 30 STL de fabricação, distribuição e quantidades das sete chapas MDF, altura do canal na moldura corrigida, novo apoio e 90 interseções nas interfaces alteradas, mais 40 das asas A/B nos cinco ângulos. Os cinco STL recebidos mantêm os hashes originais.

O modelo foi conferido digitalmente. Encaixes, acabamento, rigidez, vedação, ventoinha real e medição ainda precisam de validação física. O guia descreve os testes necessários antes de operar o conjunto.
