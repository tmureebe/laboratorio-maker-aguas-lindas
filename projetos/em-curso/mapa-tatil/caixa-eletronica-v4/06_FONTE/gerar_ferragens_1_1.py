"""Folha A4 vetorial; coordenadas em mm, sem recorte automático da página.

Fontes: Taco_impressao_3D.scad, Geometria_caixa.scad, integrar_caixa.py e
07_IMPRESSAO_3D/LEIA.md.
Cabeça, passo/perfil da rosca e furo da arruela são representações ilustrativas.
"""
from pathlib import Path
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/matplotlib-mapa-tatil')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, PathPatch, Polygon
from matplotlib.path import Path as MPath

BASE = Path(__file__).resolve().parents[1]
OUT = BASE / '05_GUIA' / 'Parafusos_e_arruelas_escala_1_1.pdf'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'pdf.fonttype': 42})
fig = plt.figure(figsize=(210 / 25.4, 297 / 25.4), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1], xlim=(0, 210), ylim=(297, 0))
ax.set_axis_off()

def text(x, y, s, size=9, weight='normal', ha='left', **kw):
    return ax.text(x, y, s, fontsize=size, weight=weight, ha=ha, va='top', **kw)

def line(x1, y1, x2, y2, lw=.65, **kw):
    ax.plot([x1, x2], [y1, y2], color='black', lw=lw, **kw)

def rect(x, y, w, h, fill='white', **kw):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor='black', lw=.65, **kw))

def hdim(x1, x2, y, objy, label):
    for x in (x1, x2):
        line(x, objy, x, y+1.5, .4)
        line(x-.8, y+1, x+.8, y-1, .5)
    line(x1, y, x2, y, .45)
    text((x1+x2)/2, y-4.5, label, 8, ha='center', bbox=dict(facecolor='white', edgecolor='none', pad=.3))

def vdim(y1, y2, x, objx, label):
    for y in (y1, y2):
        line(objx, y, x+1.5, y, .4)
        line(x-.8, y+1, x+.8, y-1, .5)
    line(x, y1, x, y2, .45)
    text(x+2, (y1+y2)/2-1.5, label, 8)

def screw(x, y, length):
    # x = face inferior da cabeça; comprimento sob a cabeça, envelope da rosca Ø3,5.
    top = [(x, y-1.05)]
    for i in range(length - 3):
        top += [(x+i+.25, y-1.05), (x+i+.55, y-1.75), (x+i+.95, y-1.05)]
    pts = top + [(x+length, y)] + [(a, 2*y-b) for a,b in reversed(top)]
    ax.add_patch(Polygon(pts, closed=True, facecolor='white', edgecolor='black', lw=.55, zorder=5))
    for i in range(length - 3):
        line(x+i+.55, y-1.75, x+i+.95, y+1.05, .35, zorder=6)
    # Cabeça panela simbólica, sem cotas comerciais inventadas.
    verts = [(x,y-3), (x-1,y-3), (x-2.1,y-2.1), (x-2.1,y),
             (x-2.1,y+2.1), (x-1,y+3), (x,y+3), (x,y-3)]
    codes = [MPath.MOVETO]+[MPath.CURVE4]*6+[MPath.CLOSEPOLY]
    ax.add_patch(PathPatch(MPath(verts,codes), facecolor='white', edgecolor='black', lw=.65, zorder=7))

text(16, 14, 'MAPA TÁTIL  /  CAIXA ELETRÔNICA', 8, 'bold')
text(16, 23, 'Parafusos dos tacos', 23, 'bold')
text(16, 36, 'Ferragens e encaixe • desenhos em escala 1:1 • medidas em mm', 9)
line(16, 45, 194, 45, 1)

text(19, 51, 'A', 16, 'bold')
text(31, 52, 'PARAFUSO PARA MADEIRA', 9, 'bold')
text(31, 59, 'Ø3,5 mm • cabeça panela', 9)
text(94, 51, '8×', 15, 'bold', ha='right')
text(116, 51, 'B', 16, 'bold')
text(128, 52, 'ARRUELA LISA', 9, 'bold')
text(128, 59, 'd₂ ≈ 7 mm • s = 0,8 mm*', 9)
text(191, 51, '8×', 15, 'bold', ha='right')
line(105, 51, 105, 114, .4)
for x, length in [(32, 12), (65, 20)]:
    screw(x, 83, length)
    hdim(x, x + length, 73, 81, f'L = {length}')
text(57, 96, 'Escolha um dos dois comprimentos.', 8, ha='center')
text(57, 104, 'Meça da face inferior da cabeça até a ponta.', 8, ha='center')
ax.add_patch(Circle((148,83), 3.5, facecolor='white', edgecolor='black', lw=.7))
ax.add_patch(Circle((148,83), 2, fill=False, edgecolor='black', lw=.5, linestyle='--'))
hdim(144.5,151.5,73,79.5,'Ø ≈ 7')
rect(174, 79.5, .8, 7)
text(175, 94, 's = 0,8*', 8, ha='center')
text(155, 101, 'd₂: Ø externo • s: espessura', 8, ha='center')
text(155, 108, 'Furo livre para parafuso Ø3,5', 7.5, ha='center')
line(16, 115, 194, 115, .6)

text(16, 121, 'MONTAGEM EM CORTE', 11, 'bold')
text(16, 129, 'Taco impresso • 1 parafuso + 1 arruela por taco • 4 na frente + 4 atrás', 8.5)
# Seção lateral real: parede 3, taco 20 × 44, tampa e fundo 3.
# Eixo 12 abaixo do topo, ou 35 acima da face inferior do fundo.
wall, front, top, axis = 43, 46, 148, 160
rect(wall, top, 3, 44, '#ededed', hatch='////')
rect(front, top, 20, 44, '#f5f5f5', hatch='..')
rect(wall, top-3, 27, 3, '#ededed', hatch='////')
rect(wall, top+44, 27, 3, '#ededed', hatch='////')
# Remover seções dos furos (passante na parede e cego no taco).
rect(wall, axis-2, 3, 4)
rect(front, axis-1.4, 18, 2.8)
# Arruela em corte, abertura central representativa.
rect(wall-.8, axis-3.5, .8, 1.5, '#cccccc')
rect(wall-.8, axis+2, .8, 1.5, '#cccccc')
screw(wall-.8, axis, 20)
line(37, axis, 70, axis, .35, linestyle='-.', zorder=8)
hdim(front, front+20, 205, 192, '20')
vdim(top,top+44,79,66,'44')
vdim(top,axis,72,66,'12')
text(18, 145, 'Tampa', 8)
line(33,147,43,147,.4)
text(18, 173, 'MDF e = 3', 7)
line(33,174,44.5,176,.4)
text(18, 189, 'Fundo', 8)
line(33,192,43,193,.4)
text(56, 179, 'Taco', 8, ha='center', bbox=dict(facecolor='white', edgecolor='none', pad=1))

text(101, 145, 'CONFERÊNCIA DO COMPRIMENTO', 9, 'bold')
text(101, 154, 'MDF de 3 mm e arruela de 0,8 mm*', 9)
text(101, 165, 'Parafuso', 8, 'bold')
text(130, 165, 'Entrada', 8, 'bold')
text(158, 165, 'Folga à ponta', 8, 'bold')
for row, length in enumerate((12, 20)):
    y = 173 + 8 * row
    entry = length - 3 - .8
    gap = 18 - entry
    text(101, y, f'{length} mm', 9)
    text(130, y, f'{entry:.1f} mm'.replace('.', ','), 9)
    text(158, y, f'{gap:.1f} mm'.replace('.', ','), 9)
text(101, 195, 'Corte ilustrado com o parafuso de 20 mm.', 8.5)
text(101, 202, 'Taco com furo cego de Ø2,8 × 18 mm.', 8.5)

line(16, 216, 194, 216, .6)
text(16, 221, '* O cálculo considera arruela de 0,8 mm. Confira a espessura da peça usada.', 8)
text(16, 227, 'Cálculo nominal, com o taco encostado na parede e sem compressão do MDF.', 8)
text(16, 233, 'Cabeça, rosca e furo interno da arruela são ilustrativos: faltam medidas no projeto.', 8)
text(16, 239, 'O corte no MDF tem Ø3,5 mm. Se a rosca prender, alargue só o MDF para Ø4 mm, como ilustrado.', 8)

text(16, 251, 'IMPRIMIR EM A4 • TAMANHO REAL / 100%', 10, 'bold')
text(16, 258, 'Desative “ajustar à página”. Confira os 100 mm abaixo com uma régua.', 8)
line(16,269,116,269,.8)
for mm in range(101):
    length = 3 if mm%10 == 0 else (2 if mm%5 == 0 else 1)
    line(16+mm,269,16+mm,269-length,.45)
    if mm%10 == 0:
        text(16+mm,271,str(mm),6.5,ha='center')
text(122, 268, '100 mm', 9, 'bold')
line(16,281,194,281,.4)
text(16, 284, 'Caixa do mapa tátil • revisão de 18/11/2026', 7)
text(194, 284, '1 / 1', 7, ha='right')

# Verifica transformação física: escala física preservada no desenho.
fig.canvas.draw()
for mm in (3.5, 7, 12, 18, 20, 44, 100):
    p0 = ax.transData.transform((0, 0))
    p1 = ax.transData.transform((mm, 0))
    assert abs((p1[0]-p0[0])/fig.dpi*25.4-mm) < 1e-9
fig.savefig(OUT, format='pdf', metadata={'Title':'Parafusos dos tacos — escala 1:1', 'Author':'Laboratório MAKER — mapa tátil'}, bbox_inches=None)
fig.savefig('/tmp/Parafusos_e_arruelas_escala_1_1.png', dpi=150, bbox_inches=None)
print(OUT)
