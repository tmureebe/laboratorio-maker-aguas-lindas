# Modelos táteis de feridas

**Situação em novembro de 2026:** em curso, com modelos digitais e protótipos impressos.

Estamos desenvolvendo modelos 3D para o ensino da morfologia de feridas. As versões táteis destacam diferenças de relevo entre a pele, a borda e o leito da lesão para exploração das peças impressas.

| Modelo | Material disponível |
| --- | --- |
| Úlcera venosa | [Prévia](imagens/ulcera-venosa.jpg) · [Gerador](scripts/gerar_modelo.py) · [Parâmetros](configuracao/modelo.json) |
| Lesão por pressão no calcâneo | [Prévia](imagens/lesao-por-pressao.jpg) · [Gerador](pressao/gerar.py) · [Parâmetros](pressao/parametros.json) |
| Lesão cronificada | [Prévia](imagens/lesao-cronificada.jpg) · [Gerador](cronificada/gerar.py) · [Parâmetros](cronificada/parametros.json) |
| Úlcera neuropática no dorso do pé | [Prévia do relevo](imagens/ulcera-neuropatica.jpg) |

A geometria da úlcera neuropática foi desenvolvida a partir da malha humana hm08 do MakeHuman, distribuída sob CC0. [Fonte da malha](https://github.com/makehumancommunity/makehuman/blob/master/makehuman/data/3dobjs/base.obj)

## Gerar arquivos de impressão

Execute na pasta do projeto com Blender e NumPy disponíveis. Cada gerador exporta seu STL para a pasta de saída correspondente.

```sh
blender --background --factory-startup --python scripts/gerar_modelo.py
blender --background --factory-startup --python pressao/gerar.py
blender --background --factory-startup --python cronificada/gerar.py
```

[Voltar ao índice geral](../../../README.md)
