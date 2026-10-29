# Visualização — não fabricar

`ABRIR_VISUALIZADOR_3D.html`: modelo completo interativo, abre localmente no navegador. Permite giro, zoom, ocultar materiais, abrir dutos/tampa e explodir o conjunto. Não precisa de internet; requer WebGL no navegador.

`Conjunto_COMPLETO_APENAS_VISUALIZAR.stl`: conjunto completo nas coordenadas de montagem. STL não armazena cores ou nomes. Não reduzir para caber na mesa, fatiar ou imprimir inteiro.

`Conjunto_COMPLETO.obj` e `materiais.mtl`: modelo completo com nomes de componentes e cores. Mantenha ambos na mesma pasta ao importar em um visualizador que suporte OBJ/MTL.

Imagens PNG mostram conjunto, peças explodidas, medição, janela, painéis, apoios e regulador. Vistas explodidas deslocam as peças para explicar a ordem; não fornecem posições reais de montagem. Nas vistas internas, algumas paredes/tampa são omitidas para facilitar a inspeção.

`mapas_chapas`: identifica IDs nos cortes; contém texto ilustrativo e não deve ser usado como arquivo de laser.

Ventoinha e célula são referências comerciais simplificadas. Ferragens, fios e vedação não estão modelados. As lâminas MDF aparecem antes da furação vertical dos pés: o guia especifica essa operação posterior.
