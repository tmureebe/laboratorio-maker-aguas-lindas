# Fontes e verificação

Estes arquivos servem para editar ou conferir a geometria. Malhas de montagem e malhas MDF são referências, não arquivos para imprimir os dutos ou pés.

- `gerar_cortes.py`: gerador SVG/DXF e manifesto das chapas. Usa Python 3 e biblioteca padrão. Os valores do pacote são MDF 3/6 mm e folga total 0,4 mm.
- `conexoes.scad`: uniões U01/U02, ligação para parte 5 e cupom da luva MDF, em OpenSCAD.
- `moldura_corrigida.scad`: modifica a fonte da moldura, guardada em `referencias/`, para retirar o degrau interno de 1,6 mm.
- `regenerar_referencias.py`: regenera moldura, conexões e malhas de referência MDF dentro deste pacote, sem acessar V5/V6.
- `montar_conjunto.py`: reúne todas as peças nas coordenadas reais e exporta STL/OBJ completo.
- `verificar_conjunto.py`: analisa STL, chapas, quantidades, altura interna, apoio da câmara, hashes e colisões booleanas das interfaces modificadas. Requer NumPy e OpenSCAD.
- `visualizar.py`, `diagramas.py`: imagens e visualizador local da geometria real.
- `exportar_documentos.py`: PDFs do guia e listas. Requer ReportLab.
- `relatorio_verificacao.json`: resultados concretos desta revisão.

Execute com `/usr/bin/python3` neste ambiente. Exemplo de revisão padrão: gerar cortes → regenerar referências → montar conjunto → verificar → criar visualizações → exportar documentos. O pacote já contém todos os arquivos prontos.

O montador e os diagramas descrevem as medidas padrão 3/6 mm. Alterar parâmetros exige revisar também posicionamentos, dimensões dos modelos de referência e ferragens; não use uma regeneração parcial como lote aprovado.

`referencias/04_moldura_janela_removivel.stl` é a fonte histórica V5, apenas para produzir a moldura V7 corrigida. Não fatiar essa fonte como peça final.
