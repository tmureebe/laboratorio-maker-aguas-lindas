# Guia ilustrado de montagem do pedestal

[Abrir o manual em PDF](Guia_ilustrado_montagem_pedestal.pdf) · [Ver todas as páginas em miniatura](Visao_geral_do_manual.png)

Manual em português, 15 páginas A4 em orientação retrato, para as **46 peças da estrutura v2 mais o tampo inteiro de 500 × 380 mm**. As ilustrações das peças são vetoriais e derivadas dos contornos e das posições do modelo OpenSCAD existente. Detalhes de aplicação de cola e prensagem são esquemáticos. Os desenhos não são gabaritos nem arquivos de corte.

## Conteúdo

| Página | Conteúdo |
| --- | --- |
| 1 | Apresentação e orientação do pedestal |
| 2–3 | Inventário ilustrado das 47 peças |
| 4 | Preparação, aplicação da cola, prensagem e tempos do fabricante |
| 5 | Laminação da base B1/B2/B3 |
| 6 | Emendas das paredes e reforços R |
| 7 | Posição e colagem dos apoios A1/A2 |
| 8 | Ensaio completo do fechamento sem cola |
| 9 | Preparação e colocação do lastro |
| 10 | Inserção de H1/H2 e fechamento das paredes |
| 11 | Orientação e encaixe da grelha GX/GY |
| 12 | Colagem do tampo de 25 encaixes |
| 13 | Cura, acabamento e conferência |
| 14 | Preparação para a caixa eletrônica V4 |
| 15 | Solução de problemas e lista de conferência |

Imprima em A4, colorido ou preto e branco. Códigos, setas e textos também identificam as etapas sem depender da cor. Os arquivos `pagina_01.png` a `pagina_15.png` permitem consultar ou compartilhar páginas isoladas.

## Referências usadas

- [Instruções e dimensões do pedestal](../../LEIA_PRIMEIRO.md).
- [Inventário original](../Lista_de_pecas.csv) e [mapa de identificação nas chapas](../Mapa_das_15_chapas.pdf).
- [Modelo geométrico](../../04_MODELOS_3D/Pedestal_MDF.scad).
- [Instruções da adaptação V4](../../../caixa-eletronica-v4/LEIA_PRIMEIRO.md) e [manual próprio da caixa](../../../caixa-eletronica-v4/05_GUIA/Guia_de_montagem.pdf).

O guia distingue a referência estática de **19 kg de massa total com caixa V4** dos **17 kg da configuração anterior**, mantendo as hipóteses e limitações documentadas no projeto. Esses números não são cargas admissíveis no tampo. O material e a contenção do lastro devem ser definidos para a montagem real.

As orientações de colagem complementam a sequência existente; os tempos aberto, de prensagem e de cura devem ser os da cola escolhida. O manual não altera os arquivos de fabricação nem substitui a avaliação física das colagens e da estrutura.

## Regenerar

Na raiz do projeto:

```sh
python3 pedestal_pecas_v2/Pedestal_MDF_LASER_600x400/07_FONTE/gerar_manual_ilustrado.py
```

Dependências: NumPy e Matplotlib. PyMuPDF e Pillow geram as prévias e a conferência do PDF. [Fonte editável](../../07_FONTE/gerar_manual_ilustrado.py) · [Relatório de verificação](VERIFICACAO_manual.json).
