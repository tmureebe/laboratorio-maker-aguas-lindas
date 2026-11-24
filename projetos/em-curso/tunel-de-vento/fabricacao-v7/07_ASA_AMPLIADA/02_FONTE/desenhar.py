#!/usr/bin/python3
"""Prancha de montagem a partir dos STL e do relatório verificado."""
from pathlib import Path
import json
import sys
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parent
sys.path.insert(0, str(ROOT / '06_CAD_VALIDACAO'))
from malhas import read, rotation, transform

report = json.loads((OUT/'03_VERIFICACAO/relatorio.json').read_text())
assert report['resultado'] == 'PASSOU'
wing = read(OUT/'03_VERIFICACAO/asa_montada_REFERENCIA.stl')
old = read(ROOT/'06_CAD_VALIDACAO/montagem_REFERENCIA/asa_A.stl')
support = read(ROOT/'06_CAD_VALIDACAO/montagem_REFERENCIA/suporte_asa.stl')
v = wing.reshape(-1, 3)
tip = np.unique(v[np.isclose(v[:, 1], -57)][:, [0, 2]], axis=0)
center = tip.mean(0)
tip = tip[np.argsort(np.arctan2(tip[:, 1]-center[1], tip[:, 0]-center[0]))]

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False})
fig = plt.figure(figsize=(12, 8.3), facecolor='#f8fafb')
grid = fig.add_gridspec(2, 2, left=.065, right=.97, top=.86, bottom=.15,
                       hspace=.38, wspace=.23)
fig.suptitle('Asa ampliada • túnel de vento V7', x=.065, y=.97,
             ha='left', fontsize=22, weight='bold', color='#123d4a')
fig.text(.065, .915, '190 mm de corda × 114 mm de envergadura  |  216,6 cm²  |  6,02 × a área original',
         fontsize=12, color='#245c6a')

ax = fig.add_subplot(grid[0, 0])
ax.set_title('Vista superior • folga lateral de 3 mm', loc='left', weight='bold')
ax.add_patch(Rectangle((200,-60),200,120,fc='#e8eef0',ec='#677f87',lw=2))
ax.add_patch(Rectangle((205,-57),190,114,fc='#44a7b8',ec='#126275',alpha=.8))
ax.add_patch(Rectangle((288,-45),40,90,fc='#f3a453',ec='#9c590d',alpha=.9))
ax.text(308,0,'Asa\nantiga\n40 × 90',ha='center',va='center',fontsize=9)
ax.annotate('', xy=(205,69),xytext=(395,69),arrowprops=dict(arrowstyle='<->',color='#126275'))
ax.text(300,72,'190',ha='center',color='#126275')
ax.plot([300],[0],'ko',ms=4)
ax.annotate('Eixo existente',xy=(300,0),xytext=(220,-25),fontsize=9,
            arrowprops=dict(arrowstyle='->'))
ax.annotate('Ar',xy=(195,0),xytext=(174,0),va='center',arrowprops=dict(arrowstyle='->'))
ax.set(xlim=(173,415),ylim=(-70,85),aspect='equal',xlabel='X da montagem (mm)',ylabel='Y (mm)')

ax = fig.add_subplot(grid[0, 1])
ax.set_title('Vista lateral • giro de −20° a +20°',loc='left',weight='bold')
ax.add_patch(Rectangle((200,62.4),200,118.4,fc='#eef2f4',ec='#677f87',lw=2))
for angle, color in [(-20,'#c97330'),(20,'#7c69aa'),(0,'#15869c')]:
    points = np.column_stack([tip[:,0],np.zeros(len(tip)),tip[:,1]])
    points = transform(points-[300,0,104.4],rotation('y',angle),[300,0,104.4])
    ax.add_patch(Polygon(points[:,[0,2]],fc=color,ec=color,alpha=.5,label=f'{angle:+d}°'))
ax.plot(300,104.4,'ko',ms=4)
ax.annotate('Eixo M3',xy=(300,104.4),xytext=(305,72),fontsize=9,
            arrowprops=dict(arrowstyle='->'))
ax.legend(loc='upper left',ncol=3,fontsize=8,frameon=False)
ax.set(xlim=(195,405),ylim=(57,187),aspect='equal',xlabel='X da montagem (mm)',ylabel='Z (mm)')

ax = fig.add_subplot(grid[1, 0],projection='3d')
ax.set_title('Geometria real • asa e suporte existente',loc='left',weight='bold',pad=8)
ax.add_collection3d(Poly3DCollection(wing,facecolor='#2b9bab',edgecolor='none',alpha=1))
ax.add_collection3d(Poly3DCollection(support,facecolor='#b5bbc1',edgecolor='none',alpha=1))
ax.set(xlim=(200,400),ylim=(-60,60),zlim=(38,145))
ax.set_box_aspect((200,120,107))
ax.view_init(elev=24,azim=-57)
ax.set_axis_off()

ax = fig.add_subplot(grid[1, 1]); ax.axis('off')
ax.set_title('Impressão e instalação',loc='left',weight='bold')
f = report['folgas_minimas_mm']
lines = [
    'Imprimir 1 unidade do STL 21, em escala 100%.',
    'Ponta na mesa, como no arquivo; brim e suporte',
    'localizado sob o encaixe central. PLA do laboratório.',
    '',
    'Retirar acrílico E moldura para inserir a asa.',
    'Reutilizar suporte 16 e eixo M3 × 35.',
    'Bordo arredondado voltado para a entrada de ar.',
    '',
    f'Folgas no giro: laterais {f["lateral"]:.1f} mm;',
    f'extremidades ≥ {min(f["entrada"],f["saida"]):.2f} mm;',
    f'piso ≥ {f["piso"]:.2f} mm; teto ≥ {f["teto_conservador"]:.2f} mm.',
    '',
    'Começar em 0°, 5° e 10°; refazer tara e calibração.',
]
ax.text(0,.95,'\n'.join(lines),transform=ax.transAxes,va='top',linespacing=1.45,fontsize=10)
fig.text(.065,.075,'Conferência digital: malha fechada, um sólido; 54 interseções sem colisão. '
         'Cotas em mm; desenho fora de escala.',fontsize=9,color='#3a5660')
fig.text(.065,.045,'A área maior não garante seis vezes a força: o bloqueio do túnel e a velocidade do ar mudam. '
         'Montagem e medição ainda exigem ensaio.',fontsize=9,color='#3a5660')
for ext in ('png','pdf'):
    fig.savefig(OUT/f'04_VISUALIZACAO/Asa_ampliada_dimensoes.{ext}',dpi=180)
print('Prancha PNG/PDF criada a partir das malhas verificadas.')
