#!/usr/bin/env python3
"""Ilustra as coordenadas exatas da montagem geradas no SCAD, em PNG/PDF."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch, Polygon

root=Path(__file__).resolve().parents[1]
data={}
for line in (root/'04_MODELOS_3D'/'Pedestal_MDF.scad').read_text().splitlines():
    for key in ['nomes','contornos','matrizes','tipos']:
        if line.startswith(key+'='):
            data[key]=json.loads(line[len(key)+1:-1])

def project(points):
    p=np.array(points)
    return np.c_[.83*p[:,0]+.56*p[:,1],-.20*p[:,0]+.30*p[:,1]+.93*p[:,2]]

def world(ring,m):
    p=np.array(ring)
    h=np.c_[p,np.zeros(len(p)),np.ones(len(p))]
    return (h @ np.array(m).T)[:,:3]

def draw(ax,i,lift=0):
    verts,codes=[],[]
    for ring in data['contornos'][i]:
        q=world(ring,data['matrizes'][i])
        q[:,2]+=lift
        points=project(q).tolist()
        verts+=points+[points[0]]
        codes+=[MPath.MOVETO]+[MPath.LINETO]*(len(points)-1)+[MPath.CLOSEPOLY]
    colors={'F':'#e9b678','T':'#b98a65','E':'#77a9a9','D':'#95a8c6',
            'B':'#b7bf91','H':'#d6bf91','G':'#c390b1','R':'#c7b79a','A':'#99b191','P':'#ece3c8'}
    ax.add_patch(PathPatch(MPath(verts,codes),fc=colors[data['tipos'][i]],ec='#394954',lw=.55))

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
fig,axes=plt.subplots(1,2,figsize=(14,12))
order={'T':0,'E':1,'B':2,'R':3,'A':4,'H':5,'G':6,'F':7,'D':8,'P':9}
indices=sorted(range(len(data['nomes'])),key=lambda i:order[data['tipos'][i]])
for ax in axes:
    ax.set(xlim=(-50,750),ylim=(-110,1190),aspect='equal')
    ax.axis('off')
for i in indices:
    draw(axes[0],i)
    if data['tipos'][i] not in ['F','D','P'] and not data['nomes'][i].startswith(('RF','RD','A1F','A2F','A1D','A2D')):
        draw(axes[1],i)
# Illustrative ballast volume, not an extra MDF piece.
corners=[[80,50,9],[360,50,9],[360,270,9],[80,270,9],
         [80,50,119],[360,50,119],[360,270,119],[80,270,119]]
for face in [[4,5,6,7],[0,1,5,4],[1,2,6,5]]:
    axes[1].add_patch(Polygon(project([corners[j] for j in face]),fc='#6b7782',ec='#374651',lw=.6))
capindex=data['nomes'].index('TAMPO')
draw(axes[1],capindex,lift=115)
def label(ax,text,pos,target):
    q=project([target])[0]
    ax.annotate(text,xy=q,xytext=pos,fontsize=9,ha='left',va='center',
                arrowprops=dict(arrowstyle='-',color='#56626a',lw=.7),
                bbox=dict(boxstyle='round,pad=.2',fc='white',ec='none',alpha=.88))
label(axes[0],'Tampo 500 × 380 × 3 mm (laser)\nInclinação 9,09°',(-25,1120),(300,170,896))
label(axes[0],'Corpo 340 × 300 mm\nAltura central ≈ 90 cm',(-25,470),(50,20,460))
label(axes[0],'Base 440 × 340 mm\n3 camadas de MDF = 9 mm',(250,-75),(400,170,9))
label(axes[1],'25 dentes, rentes ao tampo\nFuros na posição real inclinada',(-30,1160),(260,170,1008))
label(axes[1],'Grelha: 3 GX + 2 GY\nNervuras com 70 mm de altura',(330,865),(220,170,884))
label(axes[1],'H2: divisória a 620 mm\nApoios A2 nas quatro bordas',(310,610),(290,190,629))
label(axes[1],'H1: divisória a 320 mm\nApoios A1 nas quatro bordas',(310,330),(290,190,329))
label(axes[1],'Lastro imobilizado e central\nMassa total do conjunto ≥ 17 kg',(100,-60),(220,150,95))
axes[0].set_title('Montagem completa',fontsize=15,pad=8)
axes[1].set_title('Interior: frente e direita ocultas; tampo levantado',fontsize=13,pad=8)
fig.suptitle('PEDESTAL REVISADO | MDF 3 mm | ESTRUTURA E TAMPO A LASER',fontsize=18,y=.98)
fig.text(.055,.035,'Base menor com lastro · As meias-madeiras e os dentes precisam de cola · Vista de identificação, não usar como arquivo de corte',fontsize=10)
fig.tight_layout(rect=(0,.055,1,.925))
fig.savefig(root/'05_GUIA'/'Pedestal_montagem.png',dpi=160)
fig.savefig(root/'05_GUIA'/'Pedestal_montagem.pdf')
plt.close(fig)
