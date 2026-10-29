#!/usr/bin/env python3
"""Manual A4 vetorial, ilustrado a partir da geometria real do pedestal.

Executar com Python + numpy + matplotlib. PyMuPDF/Pillow geram as prévias
e fazem a conferência do PDF. Não modifica cortes, SCAD ou outros guias.
"""
from pathlib import Path
import csv
import hashlib
import json
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.path import Path as MP
from matplotlib.patches import PathPatch, Polygon, Rectangle, Circle, FancyArrowPatch
from matplotlib import colors

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / '05_GUIA' / 'Manual_ilustrado'
OUT.mkdir(exist_ok=True)
MODEL = ROOT / '04_MODELOS_3D' / 'Pedestal_MDF.scad'
DATA = {}
for line in MODEL.read_text().splitlines():
    for key in ('nomes', 'contornos', 'matrizes', 'tipos'):
        if line.startswith(key + '='):
            DATA[key] = json.loads(line[len(key) + 1:-1])
NAMES = DATA['nomes']
assert len(NAMES) == 47 and len(DATA['contornos'][NAMES.index('TAMPO')]) == 26
with (ROOT / '05_GUIA' / 'Lista_de_pecas.csv').open(encoding='utf-8-sig') as f:
    INVENTORY = list(csv.DictReader(f, delimiter=';'))
assert {row['Peça'] for row in INVENTORY} == set(NAMES)-{'TAMPO'}
assert all(row['Quantidade']=='1' for row in INVENTORY)
INK = '#23333b'
MUTED = '#56666c'
TEAL = '#006b70'
ACTIVE = '#d8edef'
LIGHT = '#f0f2f1'
GLUE = '#bd5e1a'
WARM = '#fff1e3'
W, H = 595.276, 841.89
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'pdf.fonttype': 42, 'svg.fonttype': 'none'})
TOTAL = 15
PAGES = []
TEXTS = []


def txt(ax, x, y, s, size=10.5, color=INK, weight='normal', ha='left', va='top', **kw):
    obj = ax.text(x, y, s, fontsize=size, color=color, weight=weight,
                  ha=ha, va=va, linespacing=1.4, **kw)
    TEXTS.append(obj)
    return obj


def wrap(s, n):
    return '\n'.join(textwrap.wrap(s, n, break_long_words=False, break_on_hyphens=False))


def page(kicker, title, sub, step=None):
    fig = plt.figure(figsize=(W/72, H/72), facecolor='white')
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set(xlim=(0, W), ylim=(0, H)); ax.axis('off')
    n = len(PAGES)+1
    txt(ax, 35, 809, 'LABORATÓRIO MAKER  /  MAPA TÁTIL', 8.2, TEAL, 'bold')
    txt(ax, 560, 809, kicker.upper(), 8.2, MUTED, ha='right')
    xx = 35
    if step:
        ax.add_patch(Circle((55, 759), 20, color=TEAL))
        txt(ax, 55, 759, step, 19, 'white', 'bold', 'center', 'center')
        xx = 88
    txt(ax, xx, 778, title, 22 if len(title) < 35 else 19.5, weight='bold')
    txt(ax, xx, 741, sub, 10, MUTED)
    ax.plot([35, 560], [713, 713], color=INK, lw=.8)
    ax.plot([35, 560], [40, 40], color='#b9c3c5', lw=.6)
    txt(ax, 35, 28, 'PEDESTAL v2 • TAMPO 500 × 380 • MDF 3 mm • 21/10/2026', 7.5, MUTED)
    txt(ax, 560, 28, f'{n:02d} / {TOTAL:02d}', 8.5, INK, 'bold', 'right')
    PAGES.append((fig, ax, title))
    return fig, ax


def boxnote(ax, y, title, body, tone='normal', height=76):
    fc = WARM if tone == 'glue' else LIGHT
    cc = GLUE if tone == 'glue' else TEAL
    ax.add_patch(Rectangle((35, y-height), 525, height, facecolor=fc, edgecolor='none'))
    ax.add_patch(Rectangle((35, y-height), 3, height, facecolor=cc, edgecolor='none'))
    txt(ax, 48, y-10, title, 10.5, cc, 'bold')
    txt(ax, 48, y-29, wrap(body, 85), 10)


def bullets(ax, items, y=282):
    for title, body in items:
        txt(ax, 35, y, title, 11, TEAL, 'bold')
        body = wrap(body, 86)
        txt(ax, 35, y-21, body, 10.2)
        y -= 29 + (body.count('\n')+1)*14.5 + 10
    return y


def diagram(fig, bounds=(.059, .378, .882, .438)):
    ax = fig.add_axes(bounds)
    ax.set_aspect('equal'); ax.axis('off')
    return ax


def proj(p):
    p = np.asarray(p)
    return np.c_[.86*p[:, 0]+.50*p[:, 1], -.25*p[:, 0]+.43*p[:, 1]+.866*p[:, 2]]


def world(name, ring, offset=(0,0,0), thick=0):
    m = np.asarray(DATA['matrizes'][NAMES.index(name)])
    p = np.asarray(ring)
    pts = np.c_[p, np.full(len(p), thick), np.ones(len(p))]
    return (pts @ m.T)[:, :3] + np.asarray(offset)


def path(ax, rings, fc='white', ec=INK, lw=.7, alpha=1, hatch=None, zorder=None):
    verts, codes = [], []
    for r in rings:
        r = np.asarray(r).tolist()
        verts += r + [r[0]]
        codes += [MP.MOVETO]+[MP.LINETO]*(len(r)-1)+[MP.CLOSEPOLY]
    p = PathPatch(MP(verts,codes), facecolor=fc, edgecolor=ec, lw=lw,
                  alpha=alpha, hatch=hatch, zorder=zorder)
    ax.add_patch(p)


def draw_parts(ax, names, active=(), offsets=None, tint=None, fit=True, pad=20):
    """Projeção de contornos reais. Espessura 3 mm e ordenação por profundidade."""
    offsets = offsets or {}
    tint = tint or {}
    records, points = [], []
    eye = np.array([.433, -.745, .495])
    for name in names:
        rings = DATA['contornos'][NAMES.index(name)]
        off = offsets.get(name, (0,0,0))
        fc = tint.get(name, ACTIVE if name in active else '#f7f7f4')
        wr = [world(name,r,off,3) for r in rings]
        w0 = [world(name,r,off,0) for r in rings]
        # Arestas laterais e face externa; os furos permanecem vazados.
        for r0,r3 in zip(w0,wr):
            for i in range(len(r0)):
                j = (i+1)%len(r0)
                q = np.array([r0[i],r0[j],r3[j],r3[i]])
                shade = tuple(np.asarray(colors.to_rgb(fc))*.88)
                records.append((q.mean(axis=0)@eye, [proj(q)], shade, .35))
        for ww in [w0,wr]:
            records.append((ww[0].mean(axis=0)@eye, [proj(r) for r in ww], fc, .65))
        points.extend(proj(wr[0]))
    for _, rr, fc, lw in sorted(records, key=lambda x:x[0]):
        path(ax,rr,fc,lw=lw)
    if fit and points:
        points=np.asarray(points); lo=points.min(axis=0)-pad; hi=points.max(axis=0)+pad
        ax.set(xlim=(lo[0],hi[0]),ylim=(lo[1],hi[1]))


def arrow(ax, a, b, color=TEAL, lw=1.7, dashed=False):
    ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=13,
                               color=color,lw=lw,linestyle='--' if dashed else '-'))


def arrow3(ax,a,b,**kw):
    p=proj([a,b]); arrow(ax,p[0],p[1],**kw)


def label(ax, s, target, pos, size=9.5, ha='left', color=INK):
    obj=ax.annotate(s,xy=target,xytext=pos,fontsize=size,color=color,ha=ha,va='center',
                   arrowprops=dict(arrowstyle='-',color=MUTED,lw=.7),
                   bbox=dict(boxstyle='round,pad=.24',fc='white',ec='none',alpha=.96))
    TEXTS.append(obj)


def label3(ax,s,target,pos,**kw):
    label(ax,s,proj([target])[0],pos,**kw)


def dim(ax,a,b,s,offset=(0,0),size=9):
    a,b=np.asarray(a),np.asarray(b); off=np.asarray(offset)
    ax.plot([a[0],a[0]+off[0]],[a[1],a[1]+off[1]],color=MUTED,lw=.6)
    ax.plot([b[0],b[0]+off[0]],[b[1],b[1]+off[1]],color=MUTED,lw=.6)
    ax.add_patch(FancyArrowPatch(a+off,b+off,arrowstyle='<->',mutation_scale=9,color=MUTED,lw=.8))
    p=(a+b)/2+off
    txt(ax,p[0],p[1],s,size,MUTED,ha='center',va='center',bbox=dict(fc='white',ec='none',pad=1.8))


def flat(ax,name,position=(0,0),scale=1,fc='white',normalize=True):
    rr=[np.asarray(r) for r in DATA['contornos'][NAMES.index(name)]]
    origin=rr[0].min(axis=0) if normalize else np.zeros(2)
    rr=[(r-origin)*scale+position for r in rr]
    path(ax,rr,fc)
    return rr[0]


def wall_names(k): return [f'{k}{i}' for i in range(1,5)]
def related(k): return wall_names(k)+[f'R{k}{i}' for i in range(1,4)]+[f'A{i}{k}' for i in [1,2]]
BASE=['B1','B2','B3']
GRID=['GX1','GX2','GX3','GY1','GY2']
BODY=[n for n in NAMES if n not in GRID+['TAMPO']]


def ballast(ax):
    # Volume apenas ilustrativo, sem especificar material, massa ou recipiente.
    p=np.array([[85,55,9],[355,55,9],[355,285,9],[85,285,9],
                [85,55,115],[355,55,115],[355,285,115],[85,285,115]])
    for face in [[0,1,5,4],[1,2,6,5],[4,5,6,7]]:
        ax.add_patch(Polygon(proj(p[face]),fc='#c5cbd0',ec=INK,lw=.8,hatch='///'))


def save(pdf,fig):
    pdf.savefig(fig)


def main():
    pdfpath=OUT/'Guia_ilustrado_montagem_pedestal.pdf'
    with PdfPages(pdfpath,metadata={'Title':'Pedestal — Guia ilustrado de montagem',
         'Author':'Laboratório Maker • Mapa tátil','Subject':'Montagem das 47 peças e técnicas de colagem; compatível com caixa V4'}) as pdf:
        # 01 — Capa
        fig,ax=page('Manual de montagem','Monte o pedestal','Guia visual • peças identificadas • encaixes • colagem por etapas')
        dax=diagram(fig,(.15,.30,.70,.53))
        draw_parts(dax,NAMES,active=['TAMPO']+BASE,pad=55)
        label3(dax,'TAMPO\n500 × 380 mm',(470,170,898),(480,830))
        label3(dax,'FRENTE\nlado mais baixo',(160,20,600),(-100,590))
        label3(dax,'BASE\n440 × 340 mm',(280,80,9),(410,30))
        dax.set(xlim=(-135,665),ylim=(-65,1080))
        txt(ax,35,230,'47 peças',25,TEAL,'bold')
        txt(ax,215,230,'MDF 3 mm',25,TEAL,'bold')
        txt(ax,420,230,'A4',25,TEAL,'bold')
        txt(ax,35,193,'46 da estrutura\n+ 1 tampo inteiro',10,MUTED)
        txt(ax,215,193,'Base laminada de 9 mm\nTampo inclinado a 9,09°',10,MUTED)
        txt(ax,420,193,'Impressão colorida\nou em preto e branco',10,MUTED)
        boxnote(ax,133,'COMECE PELO ENSAIO SEM COLA',
                'Separe as peças, marque a face interna e simule o fechamento completo. '+
                'As setas mostram o movimento; azul-claro destaca a peça da etapa. '+
                'Ilustrações sem escala de fabricação.',height=76)
        save(pdf,fig)

        # 02 — Inventário paredes
        fig,ax=page('Conferência 1/2','Separe as quatro paredes','16 peças • uma unidade de cada código • numeração sobe da base ao topo')
        for col,(k,title) in enumerate([('F','FRENTE'),('T','TRASEIRA'),('E','ESQUERDA'),('D','DIREITA')]):
            x=42+col*134
            txt(ax,x+55,684,title,10,TEAL,'bold','center')
            txt(ax,x+55,665,'baixa' if k=='F' else 'alta' if k=='T' else 'topo inclinado',9,MUTED,ha='center')
            for row in range(4):
                n=f'{k}{4-row}'; y=550-row*118
                rr=flat(ax,n,(x,y),.30,ACTIVE)
                txt(ax,x+55,y-10,n,12,INK,'bold','center')
            arrow(ax,(x+117,228),(x+117,620),lw=.8)
        boxnote(ax,177,'COMO IDENTIFICAR AS PEÇAS JÁ CORTADAS',
                'Use o Mapa_das_15_chapas.pdf da pasta 05_GUIA para relacionar cada '+
                'posição da chapa ao código. Escreva a lápis na face que ficará por dentro. '+
                'F1/T1/E1/D1 têm dentes inferiores; as faixas 4 recebem a grelha.',height=90)
        txt(ax,35,65,'Oriente E e D com a borda mais alta junto à traseira T.',10,TEAL,'bold')
        save(pdf,fig)

        # 03 — Inventário restante
        fig,ax=page('Conferência 2/2','Base, apoios e tampo','31 peças • somadas às 16 paredes = 47 • todos os códigos são do projeto')
        for j,n in enumerate(BASE):
            x=42+j*174
            flat(ax,n,(x,571),.31,ACTIVE)
            txt(ax,x+68,557,n+'  ×1',11,weight='bold',ha='center')
        txt(ax,35,532,'B1 e B2: lisas. B3: 12 ranhuras. Cada base mede 440 × 340 mm.',9.5,MUTED)
        for j,n in enumerate(['H1','H2']):
            x=42+j*165
            flat(ax,n,(x,414),.32,LIGHT)
            txt(ax,x+54,404,n+'  ×1',10,weight='bold',ha='center')
        flat(ax,'TAMPO',(382,414),.32,ACTIVE)
        txt(ax,462,404,'TAMPO ×1',10,weight='bold',ha='center')
        txt(ax,35,382,'H1/H2: 333,85 × 293,85 mm. Tampo: 500 × 380 mm, 25 ranhuras.',9.5,MUTED)
        for j,n in enumerate(['GX1','GX2','GX3']):
            flat(ax,n,(42,337-j*30),.39,ACTIVE)
            txt(ax,235,347-j*30,n+' ×1',9.5,va='center')
        for j,n in enumerate(['GY1','GY2']):
            flat(ax,n,(330,327-j*64),.42,ACTIVE)
            txt(ax,495,345-j*64,n+' ×1',9.5,va='center')
        txt(ax,35,249,'12 REFORÇOS DE EMENDA  /  altura 30 mm',10,TEAL,'bold')
        flat(ax,'RF1',(42,213),.36,LIGHT)
        txt(ax,156,224,'RF1–RF3 + RT1–RT3: 6 tiras de 280 × 30',9.5,va='center')
        flat(ax,'RE1',(42,189),.36,LIGHT)
        txt(ax,156,200,'RE1–RE3 + RD1–RD3: 6 tiras de 240 × 30',9.5,va='center')
        txt(ax,35,161,'8 APOIOS DAS DIVISÓRIAS  /  altura 20 mm',10,TEAL,'bold')
        flat(ax,'A1F',(42,127),.36,ACTIVE)
        txt(ax,156,136,'A1F/A1T/A2F/A2T: 4 tiras de 280 × 20',9.5,va='center')
        flat(ax,'A1E',(42,103),.36,ACTIVE)
        txt(ax,156,112,'A1E/A1D/A2E/A2D: 4 tiras de 240 × 20',9.5,va='center')
        txt(ax,35,68,'Não confunda: R reforça emendas; A sustenta H; G sustenta o tampo.',10,TEAL,'bold')
        save(pdf,fig)

        # 04 — Cola, visão prática
        fig,ax=page('Antes de começar','Como colar sem deformar','Separe tudo antes de abrir a cola • bancada plana • ajuda no fechamento')
        # Ilustrações esquemáticas de ferramentas e prensagem.
        for x,title in [(45,'COLA'),(219,'APLICAÇÃO'),(393,'PRENSAGEM')]:
            txt(ax,x+72,687,title,10,TEAL,'bold','center')
        ax.add_patch(Rectangle((91,578),53,73,fc=ACTIVE,ec=INK,lw=1))
        ax.add_patch(Polygon([(104,651),(130,651),(124,666),(111,666)],fc='white',ec=INK))
        txt(ax,117,622,'PVA',14,TEAL,'bold','center','center')
        txt(ax,117,597,'MDF',9,INK,ha='center')
        ax.add_patch(Rectangle((225,591),130,13,fc='#dadbd7',ec=INK))
        ax.plot([232,349],[607,607],color=GLUE,lw=2)
        ax.add_patch(Polygon([(271,612),(291,631),(305,626),(280,607)],fc=ACTIVE,ec=INK))
        ax.plot([298,316],[629,652],color=INK,lw=5)
        txt(ax,291,574,'película fina e contínua',9,MUTED,ha='center')
        for y,col in [(590,LIGHT),(609,ACTIVE),(625,LIGHT)]:
            ax.add_patch(Rectangle((395,y),150,11,fc=col,ec=INK))
        for x in [416,524]:
            ax.plot([x,x],[575,654],color=INK,lw=2)
            ax.plot([x-12,x+12],[648,648],color=INK,lw=3)
            arrow(ax,(x,674),(x,638),color=GLUE)
        txt(ax,470,563,'calços largos e planos',9,MUTED,ha='center')
        bullets(ax,[
            ('1  Prepare as superfícies',
             'Escolha cola para madeira/MDF compatível com as superfícies, como PVA. '+
             'Remova fuligem solta das bordas a laser com lixa fina em taco; tire o pó com pincel seco. '+
             'Preserve os dentes e teste a aderência em retalho do mesmo MDF.'),
            ('2  Dose e distribua',
             'Use pincel pequeno nas bordas e espátula nas faces largas. Espalhe uma película '+
             'contínua conforme o rótulo, sem poças. Evite encher ranhuras. Retire o excesso '+
             'com espátula e pano apenas levemente umedecido, sem encharcar o MDF.'),
            ('3  Prenda com pressão leve e distribuída',
             'Use placas planas, calços largos, fita de baixa aderência testada em retalho '+
             'e sargentos leves. Proteja a bancada e os calços com filme antiaderente. '+
             'Aperte só até fechar a junta; se o MDF curvar, reduza a pressão.'),
        ],y=528)
        boxnote(ax,211,'TRÊS TEMPOS DIFERENTES — CONSULTE O RÓTULO',
                'Tempo aberto: limite para espalhar cola e unir as peças. Tempo de prensagem: '+
                'quanto manter o conjunto preso. Cura total: quando liberar esforço e carga. '+
                'A cola parecer seca por fora não comprova cura. Temperatura e umidade influem.',tone='glue',height=92)
        txt(ax,35,98,'Tenha à mão: lápis, régua/trena, esquadro, lixa fina, pincel, espátula,',9.5)
        txt(ax,35,80,'fita, sargentos, calços, filme antiaderente e balança para o lastro.',9.5)
        save(pdf,fig)

        # 05 — Base
        fig,ax=page('Montagem','Lamine a base','Peças: B1 + B2 + B3 • três camadas de 3 mm',step='01')
        dax=diagram(fig)
        offsets={'B2':(0,0,100),'B3':(0,0,200)}
        draw_parts(dax,BASE,active=['B3'],offsets=offsets,pad=30)
        for y,z,name in [(340,6,'B1 · inferior lisa'),(340,109,'B2 · intermediária lisa'),(340,212,'B3 · 12 ranhuras')]:
            label3(dax,name,(70,y,z),(-20,proj([[70,y,z]])[0,1]+30),size=10)
        for x in [70,365]:
            arrow3(dax,(x,90,175),(x,90,130))
            arrow3(dax,(x,90,80),(x,90,30))
        dax.set(xlim=(-25,600),ylim=(-130,440))
        txt(ax,35,308,'↓  Alinhe as quatro bordas. As ranhuras ficam na camada de cima.',10,TEAL,'bold')
        bullets(ax,[
            ('Prepare e confira',
             'Empilhe a seco e marque a orientação. Espalhe cola entre B1/B2 e B2/B3. '+
             'Na segunda união, mantenha livres as 12 ranhuras de B3.'),
            ('Prense entre duas placas planas',
             'Proteja as placas contra cola e distribua os sargentos. Confira se as camadas '+
             'deslizaram ao apertar e corrija imediatamente. Não use peso concentrado no meio.'),
        ],y=279)
        boxnote(ax,128,'COLAGEM • ESPERE A CURA ANTES DE ERGUER AS PAREDES',
                'A base pronta tem 9 mm. Confira as ranhuras ainda durante o tempo aberto. '+
                'Os dentes das paredes entram só em B3; B1 e B2 permanecem inteiras. '+
                'A face inferior deverá apoiar por inteiro no piso.',tone='glue',height=77)
        save(pdf,fig)

        # 06 — Emendas
        fig,ax=page('Montagem','Una e reforce as paredes','Peças: F1–F4 + RF1–RF3 • repita para T, E e D',step='02')
        dax=diagram(fig,(.059,.365,.882,.46))
        for i in range(1,5):
            flat(dax,f'F{i}',(0,(i-1)*55),1,LIGHT,normalize=False)
            txt(dax,170,(i-1)*227+(i-1)*55+100,f'F{i}',12,ha='center',va='center',weight='bold')
        for i,z in enumerate([227,454,681],1):
            arrow(dax,(170,z+(i-1)*55+43),(170,z+(i-1)*55+8))
        txt(dax,170,1090,'UNIR EM PLANO',10,TEAL,'bold','center')
        for n in wall_names('F'): flat(dax,n,(520,0),1,LIGHT,normalize=False)
        for i,z in enumerate([227,454,681],1):
            dax.add_patch(Rectangle((550,z-15),280,30,fc=ACTIVE,ec=INK,lw=.7))
            label(dax,f'RF{i}',(770,z),(900,z),size=10)
        txt(dax,690,990,'FACE INTERNA',10,TEAL,'bold','center')
        label(dax,'30 mm\nde altura',(650,681),(530,790),size=9)
        dim(dax,(520,0),(550,0),'30',(0,-55))
        label(dax,'reforço centralizado\nna linha da emenda',(695,454),(520,560),size=9)
        dax.set(xlim=(-40,1050),ylim=(-90,1140))
        bullets(ax,[
            ('Monte cada parede deitada',
             'Sobre bancada plana protegida, una as faixas 1 → 2 → 3 → 4. Aplique cola nas '+
             'superfícies dos dentes em contato. Alinhe as faixas sem forçar nem criar degrau.'),
            ('Reforce a face interna',
             'Cole cada tira R por toda a face larga, cobrindo a emenda. Centralize a altura '+
             'de 30 mm na linha nominal da união: 15 mm de cada lado. Deixe 30 mm livres nas extremidades.'),
        ],y=286)
        boxnote(ax,130,'COLAGEM • FAÇA UMA PAREDE POR VEZ',
                'Use fita para manter as faixas alinhadas e calços planos sobre as tiras R. '+
                'Prense sem empenar. Aguarde a cura antes de levantar. Repita com RT na traseira, '+
                'RE na esquerda e RD na direita; todos por dentro.',tone='glue',height=78)
        save(pdf,fig)

        # 07 — Apoios
        fig,ax=page('Montagem','Cole os apoios de H1 e H2','Peças: A1F/T/E/D e A2F/T/E/D • oito tiras de 20 mm',step='03')
        dax=diagram(fig,(.059,.375,.882,.45))
        for n in wall_names('F'):flat(dax,n,(0,0),1,LIGHT,normalize=False)
        for z in [227,454,681]:dax.add_patch(Rectangle((30,z-15),280,30,fc='#dededb',ec=MUTED,lw=.5))
        for i,z in [(1,297),(2,597)]:
            dax.add_patch(Rectangle((30,z),280,20,fc=ACTIVE,ec=TEAL,lw=1))
            label(dax,f'A{i}F',(150,z+10),(390,z+35),size=10)
        dax.plot([-30,360],[0,0],color=INK,lw=1)
        dim(dax,(0,0),(0,317),'317',(-75,0),size=10)
        dim(dax,(0,0),(0,617),'617',(-150,0),size=10)
        txt(dax,170,-45,'0 = face superior de B3\n(borda reta inferior da parede)',9,MUTED,ha='center')
        # Corte ampliado: parede, apoio vertical e divisória horizontal.
        dax.add_patch(Rectangle((580,300),15,290,fc=LIGHT,ec=INK))
        dax.add_patch(Rectangle((595,360),15,100,fc=ACTIVE,ec=INK))
        dax.add_patch(Rectangle((595,460),155,15,fc='white',ec=INK))
        dax.plot([595,595],[363,457],color=GLUE,lw=2)
        label(dax,'H: 3 mm',(675,468),(675,555),size=10,ha='center')
        label(dax,'A: altura 20 mm',(610,400),(690,330),size=9,ha='center')
        label(dax,'cola na face larga',(595,415),(650,235),size=9,ha='center')
        txt(dax,665,735,'CORTE AMPLIADO',10,TEAL,'bold','center')
        txt(dax,665,680,'H pousa na borda\nde 3 mm do apoio.',9,ha='center')
        dax.set(xlim=(-190,830),ylim=(-100,920))
        bullets(ax,[
            ('Meça a partir da referência correta',
             'Marque a borda superior dos apoios A1 a 317 mm e dos A2 a 617 mm acima da face '+
             'superior de B3. Na parede deitada, use a borda inferior reta; não a ponta dos dentes.'),
            ('Cole as tiras na face interna',
             'As bordas inferiores ficam em 297 e 597 mm. Centralize as tiras, deixando '+
             '30 mm livres em cada extremidade da parede. Repita nas quatro paredes.'),
        ],y=279)
        boxnote(ax,128,'COLAGEM • A TIRA FICA EM PÉ, ENCOSTADA NA PAREDE',
                'Espalhe cola na face de 20 mm de altura do apoio e prense com um calço largo. '+
                'Aguarde a cura. Não cole a tira deitada como uma prateleira. Depois, H1/H2 '+
                'terão faces superiores a 320/620 mm acima de B3.',tone='glue',height=77)
        save(pdf,fig)

        # 08 — Ensaio do corpo
        fig,ax=page('Montagem','Ensaie o fechamento completo','Base + quatro paredes preparadas + H1/H2 • ainda SEM cola',step='04')
        dax=diagram(fig)
        names=BASE+sum([wall_names(k) for k in 'TEDF'],[])
        offsets={}
        for k,off in [('F',(0,-150,45)),('T',(0,70,45)),('E',(-80,0,45)),('D',(100,0,45))]:
            for n in wall_names(k):offsets[n]=off
        draw_parts(dax,names,active=wall_names('F'),offsets=offsets,pad=60)
        arrow3(dax,(220,-125,490),(220,15,460))
        arrow3(dax,(490,180,430),(390,180,410))
        label3(dax,'T · traseira alta',(200,390,920),(305,1100))
        label3(dax,'F · última parede',(150,-130,460),(-160,450))
        label3(dax,'D',(490,170,700),(610,700))
        label3(dax,'E',(-30,120,650),(-160,740))
        label3(dax,'12 dentes na base',(340,20,6),(370,-85))
        dax.set(xlim=(-190,680),ylim=(-120,1140))
        bullets(ax,[
            ('Simule toda a sequência, com ajuda',
             'Teste paredes, base, lastro, H1/H2 e frente F. Mantenha os cantos com folga '+
             'para introduzir os dentes inferiores em B3. Encaixe a última parede com pequenos '+
             'movimentos conjuntos das paredes, sem torcer os dentes.'),
            ('Prepare a sessão de colagem',
             'Separe fita, calços, sargentos e pano ao alcance. Marque a orientação. '+
             'Ajuste somente pontos de atrito com lixa em taco. Se precisa bater, o ajuste ainda não está pronto.'),
        ],y=285)
        boxnote(ax,128,'ATENÇÃO • NÃO CURE UM CORPO EM “U” ANTES DE FECHAR',
                'As etapas 05 e 06 são preparadas agora e executadas na mesma sessão de '+
                'fechamento. Os cantos precisam continuar ajustáveis. Ensaie até caber no tempo '+
                'aberto da cola; escolha produto com tempo suficiente e trabalhe a duas pessoas.',tone='glue',height=77)
        save(pdf,fig)

        # 09 — Lastro
        fig,ax=page('Montagem','Prepare e coloque o lastro','Antes de H1 e do fechamento definitivo • base curada e apoiada no piso',step='05')
        dax=diagram(fig)
        draw_parts(dax,BASE+related('T')+related('E'),pad=60)
        ballast(dax)
        label3(dax,'H1 ficará aqui\nface superior: 320 mm',(200,150,329),(400,430))
        q=proj([[53,23,329],[387,23,329],[387,317,329],[53,317,329],[53,23,329]])
        dax.plot(q[:,0],q[:,1],'--',color=TEAL,lw=1)
        label3(dax,'peso sobre B3\ncentrado e imobilizado',(220,150,70),(420,120))
        txt(dax,200,970,'F e D omitidas para mostrar o interior.',8.7,MUTED,ha='center')
        dax.set(xlim=(-20,700),ylim=(-100,1010))
        bullets(ax,[
            ('Pese as peças e os componentes previstos',
             'Para o conjunto atual COM caixa eletrônica V4, a referência do projeto é '+
             '19 kg de massa total. Lastro = 19 kg menos a massa das demais partes. '+
             'Exemplo: 6 kg de peças + mapa + eletrônica pedem pelo menos 13 kg de lastro.'),
            ('Deixe o compartimento pronto para fechar',
             'Distribua e imobilize o lastro centralizado diretamente sobre B3, dentro do corpo. '+
             'Use contenção compatível com o material escolhido; não deixe peso solto. '+
             'Não apoie lastro em H1/H2. O volume desenhado é apenas ilustrativo.'),
        ],y=285)
        boxnote(ax,128,'REFERÊNCIA DO PROJETO, NÃO CAPACIDADE DE CARGA',
                'Os 19 kg usam 20 N a 1,02 m, fator 1,5, piso plano e massa centrada; '+
                'sem a caixa V4, o guia v2 usa 17 kg. Isso não cobre apoio do peso do corpo. '+
                'Nesse uso, o projeto prevê fixação ao piso e avaliação estrutural.',height=77)
        save(pdf,fig)

        # 10 — Fechamento H + frente
        fig,ax=page('Montagem','Insira H1/H2 e feche a frente','Sessão de fechamento • mantenha os cantos ajustáveis até assentar tudo',step='06')
        dax=diagram(fig)
        names=BASE+related('T')+related('E')+['H1','H2']+wall_names('F')
        offsets={'H1':(0,-90,30),'H2':(0,-90,30)}
        offsets.update({n:(0,-210,20) for n in wall_names('F')})
        draw_parts(dax,names,active=['H1','H2']+wall_names('F'),offsets=offsets,pad=30)
        for z in [326,626]:arrow3(dax,(220,-80,z+40),(220,100,z+5))
        arrow3(dax,(340,-205,460),(340,15,440))
        label3(dax,'H2',(300,0,656),(470,720))
        label3(dax,'H1',(300,0,356),(470,440))
        label3(dax,'F: encaixar cantos\ne dentes da base',(120,-190,400),(-180,210))
        txt(dax,340,1010,'D oculta apenas para visualização.',8.7,MUTED,ha='center')
        dax.set(xlim=(-195,660),ylim=(-190,1050))
        bullets(ax,[
            ('Cole e monte na ordem ensaiada',
             'Aplique cola nas superfícies de contato dos cantos, dentes da base, bordas de H '+
             'e topos dos apoios A. Posicione T/E/D com cantos soltos; coloque o lastro preparado; '+
             'insira H1 e H2 e feche com F antes de a cola perder o tempo aberto.'),
            ('Acerte a geometria antes de apertar',
             'H1/H2 pousam nos apoios e têm as quatro bordas coladas às paredes. '+
             'Confira dentes da base assentados, base plana, cantos a 90° e diagonais iguais '+
             'na seção retangular do corpo. A inclinação prevista fica só no topo.'),
        ],y=286)
        boxnote(ax,129,'COLAGEM • PRENDA PERTO DOS APOIOS INTERNOS',
                'Use calços largos junto à base e aos níveis de H1/H2. Fita ou cinta com '+
                'proteções de canto ajuda a manter a posição, sem esmagar o corpo. Reconfira '+
                'as diagonais após prender e aguarde a cura antes de instalar a grelha.',tone='glue',height=78)
        save(pdf,fig)

        # 11 — Grelha
        fig,ax=page('Montagem','Encaixe a grelha superior','Peças: GX1/GX2/GX3 + GY1/GY2 • todos os dentes para cima',step='07')
        dax=diagram(fig,(.059,.43,.882,.395))
        # Topo isolado, sem o restante do corpo, para ampliar os encaixes.
        upper=[f'{k}4' for k in 'FTED']
        offsets={n:(0,0,145 if n.startswith('GY') else 70) for n in GRID}
        draw_parts(dax,upper+GRID,active=GRID,offsets=offsets,pad=20)
        for x,y in [(95,80),(345,180)]:arrow3(dax,(x,y,1000),(x,y,930))
        label3(dax,'GY1',(95,155,1040),(-10,1110))
        label3(dax,'GY2',(345,155,1040),(530,1090))
        for n,y in [('GX1',71.26),('GX2',170),('GX3',268.74)]:
            label3(dax,n,(-12,y,860+.16*y+70),(-150,proj([[-12,y,860+.16*y+70]])[0,1]),size=9)
        dax.set(xlim=(-190,640),ylim=(500,1170))
        txt(ax,35,347,'Nos cruzamentos G × G:',10,TEAL,'bold')
        txt(ax,282,347,'Nos encontros G × parede:',10,TEAL,'bold')
        txt(ax,35,326,'GX: rasgo para cima. GY: para baixo.',9.5)
        txt(ax,282,326,'G: rasgo para baixo. Parede: para cima.',9.5)
        bullets(ax,[
            ('Monte a seco e confira o sentido',
             'GX1 fica à frente, GX2 no meio e GX3 atrás. GY1 fica à esquerda e GY2 à direita. '+
             'A extremidade mais alta das GY aponta para a traseira. Faça a grelha e as '+
             'paredes entrarem em conjunto, aos poucos, sem martelar.'),
            ('Posições de referência no tampo',
             'GX: s = 90 / 190 / 290 mm. GY: x = 125 / 375 mm. As medidas partem do canto '+
             'dianteiro esquerdo, na superfície inclinada do tampo. Use os encaixes existentes para posicionar.'),
        ],y=289)
        boxnote(ax,129,'COLAGEM • NÃO CURE A GRELHA SEPARADA ANTES DO TESTE',
                'Após ensaiar o encaixe simultâneo, aplique cola nas faces das meias-madeiras '+
                'e contatos com as paredes. Retire excessos e confira o alinhamento usando o '+
                'tampo a seco, sem deixá-lo aderir por acidente. Os encaixes precisam de cola.',tone='glue',height=78)
        save(pdf,fig)

        # 12 — Tampo
        fig,ax=page('Montagem','Assente o tampo inteiro','Peça: TAMPO 500 × 380 • alinhe os 25 dentes antes de pressionar',step='08')
        dax=diagram(fig,(.059,.39,.882,.435))
        names=[f'{k}4' for k in 'FTED']+GRID+['TAMPO']
        draw_parts(dax,names,active=['TAMPO'],offsets={'TAMPO':(0,0,160)},pad=25)
        for x,y in [(70,40),(400,270)]:arrow3(dax,(x,y,1015),(x,y,935))
        label3(dax,'25 ranhuras',(250,150,1060),(-40,1210))
        label3(dax,'cola em todas as bordas\nque tocam o tampo',(220,90,895),(600,860),size=9.5,ha='right')
        dax.set(xlim=(-80,625),ylim=(510,1250))
        bullets(ax,[
            ('Primeiro, confira todos os encaixes sem cola',
             'O tampo deve descer por igual, sem ficar suspenso por um dente. Se travar, '+
             'levante, localize o contato e ajuste levemente. A frente é a borda baixa. '+
             'Não use sargentos para obrigar um encaixe que não entrou a seco.'),
            ('Cole paredes, grelha e tampo',
             'Passe película de cola nas bordas superiores das quatro paredes, nas cinco '+
             'nervuras e nos contatos dos dentes. Alinhe as 25 ranhuras e assente progressivamente, '+
             'com outra pessoa ajudando a manter o alinhamento.'),
        ],y=293)
        boxnote(ax,133,'COLAGEM • PRESSÃO SOBRE AS LINHAS DE APOIO',
                'Use calços planos protegidos e pressão leve, distribuída sobre paredes e '+
                'nervuras. Evite carga pontual no centro ou nas bordas em balanço. Se houver '+
                'desnível na frente/traseira, ajuste por lixa ao ângulo de 9,09° antes da cola.',tone='glue',height=82)
        save(pdf,fig)

        # 13 — Cura e acabamento
        fig,ax=page('Montagem','Espere a cura e dê acabamento','Cura completa da cola antes de movimentar ou carregar o conjunto',step='09')
        dax=diagram(fig,(.059,.48,.882,.34))
        # Corte esquemático ampliado (sem escala).
        dax.add_patch(Rectangle((80,50),300,18,fc=ACTIVE,ec=INK))
        dax.add_patch(Rectangle((160,-30),18,80,fc=LIGHT,ec=INK))
        dax.add_patch(Rectangle((160,50),18,24,fc=LIGHT,ec=INK))
        dax.add_patch(Rectangle((120,95),110,30,fc='white',ec=INK))
        dax.plot([120,230],[92,92],color=GLUE,lw=2)
        arrow(dax,(125,142),(225,142));arrow(dax,(225,157),(125,157))
        label(dax,'lixa fina em taco plano',(170,110),(305,152),size=10)
        label(dax,'dente deve ficar rente',(169,74),(315,95),size=10)
        txt(dax,220,-54,'DETALHE AMPLIADO • não lixar o tampo para “sumir” o dente',9,MUTED,ha='center')
        dax.set(xlim=(45,465),ylim=(-70,185))
        bullets(ax,[
            ('Depois da cura total',
             'Retire as proteções e lixe apenas as pontas salientes até ficarem rentes. '+
             'Use taco plano e confira com régua; não afine a chapa de 3 mm. Tire o pó '+
             'antes de qualquer colagem seguinte.'),
            ('Confira o conjunto em piso plano',
             'A base deve apoiar por inteiro. Examine emendas e cantos: não devem abrir. '+
             'Confira H1/H2 na montagem, dentes assentados, tampo sem folgas e lastro imóvel. '+
             'Se algo se move, corrija a junta antes de acrescentar a caixa ou o mapa.'),
            ('Movimente pelo corpo e pela base',
             'Com lastro, o conjunto fica pesado. Planeje a montagem perto do local de uso. '+
             'Quando precisar mover, use ajuda e sustente a base; não levante pelo tampo em balanço.'),
        ],y=384)
        boxnote(ax,128,'ANTES DO ACABAMENTO SUPERFICIAL',
                'Se for receber a caixa V4, mantenha a área de colagem do tampo limpa e '+
                'sem pintura, cera ou verniz incompatível com a cola escolhida. Confira '+
                'a aderência em retalho quando houver qualquer revestimento.',tone='glue',height=77)
        save(pdf,fig)

        # 14 — V4
        fig,ax=page('Montagem','Prepare a caixa eletrônica V4','O pedestal termina no tampo com 25 encaixes • a caixa é um conjunto adicional',step='10')
        dax=diagram(fig,(.059,.47,.882,.345))
        # Detalhe de interface, mantida a inclinação real de 9,09 graus.
        for z,col in [(0,LIGHT),(20,ACTIVE),(125,'white')]:
            p=np.array([[0,0],[500,0],[500,3],[0,3]],dtype=float)
            p[:,1]+=.16*p[:,0]+z
            dax.add_patch(Polygon(p,fc=col,ec=INK,lw=1))
        arrow(dax,(240,94),(240,65))
        label(dax,'C1: painel removível da caixa',(200,160),(20,242),size=10)
        label(dax,'C0: fundo liso novo',(350,78),(330,161),size=10)
        label(dax,'tampo do pedestal\ndentes já lixados',(400,65),(330,-42),size=10)
        txt(dax,70,105,'COLAR\nC0 ao tampo',10,GLUE,'bold',ha='center')
        dax.set(xlim=(-20,545),ylim=(-80,270))
        txt(ax,35,393,'Esquema da união: paredes e reforços da caixa omitidos.',9,MUTED)
        bullets(ax,[
            ('Siga o guia próprio da caixa',
             'Cole C0 sobre o tampo existente, alinhando as quatro bordas de 500 × 380. '+
             'Prepare a montagem da caixa e seu painel removível conforme o guia V4; '+
             'as peças adicionais não fazem parte das 47 peças deste manual.'),
            ('Preserve a abertura para manutenção',
             'C1 sai com os tacos e as nervuras da caixa após retirar os parafusos laterais '+
             'da frente e de trás. Não cole C1 às paredes nem os tacos ao fundo. '+
             'O mapa será fixado ao painel removível, após revisar sua implantação.'),
            ('Confira dimensões e lastro antes de finalizar',
             'O gabarito antigo do mapa, de 500 × 500, precisa ser revisto para 500 × 380. '+
             'Com V4, a altura central antes do relevo fica em cerca de 94,5 cm e a referência '+
             'estática de massa total passa a 19 kg, conforme a página 9.'),
        ],y=367)
        boxnote(ax,117,'GUIA COMPLEMENTAR JÁ EXISTENTE NO PROJETO',
                'adaptacao_caixa_eletronica_v4/05_GUIA/Guia_de_montagem.pdf — '+
                'consulte para montar paredes, tampa removível, tacos, parafusos e eletrônica.',height=65)
        save(pdf,fig)

        # 15 — Problemas e checklist
        fig,ax=page('Consulta rápida','Se a montagem emperrar','Pare, localize a causa e corrija enquanto as peças ainda podem ser ajustadas')
        rows=[
            ('O dente não entra',
             'Retire e veja onde há atrito. Remova só rebarba/fuligem e teste de novo. '+
             'Não martele nem use a cola como lubrificante para forçar.'),
            ('A cola começou a formar pele',
             'Não feche a junta assim. Reabra, retire a cola conforme o fabricante '+
             'e prepare as faces antes de reaplicar. Não acrescente água para recuperar o tempo aberto.'),
            ('A peça escorrega ao prensar',
             'Reduza a pressão, alinhe e segure com fita testada. Reaperte gradualmente '+
             'com calços largos. Confira a posição outra vez antes de deixar curar.'),
            ('Há fresta ou a tira descolou',
             'Não conte com um cordão externo de PVA para preencher a falha. Abra a união '+
             'quando possível, limpe, recupere o contato e recoloque; troque peça danificada.'),
            ('O tampo arqueia ou fica alto',
             'Pare a pressão. Confira dentes, ranhuras e grelha. Ajuste antes de colar; '+
             'pressão excessiva não corrige geometria errada e pode romper o MDF.'),
        ]
        y=687
        for i,(title,body) in enumerate(rows):
            ax.add_patch(Rectangle((35,y-79),525,79,fc=LIGHT if i%2==0 else 'white',ec='none'))
            txt(ax,47,y-9,title,11,TEAL,'bold')
            txt(ax,47,y-30,wrap(body,83),9.7)
            y-=85
        txt(ax,35,246,'CONFERÊNCIA FINAL',11,TEAL,'bold')
        checklist=[
            'Base plana, cantos alinhados e todas as colagens curadas.',
            'Lastro centrado e imobilizado; massa conferida para a configuração.',
            'H1/H2 e grelha coladas; tampo assentado e dentes rentes.',
            'Sem folgas ou juntas abertas; interface V4 preparada, se usada.',
        ]
        for i,s in enumerate(checklist):
            y=217-i*25
            ax.add_patch(Rectangle((36,y-10),9,9,fill=False,ec=INK,lw=.8))
            txt(ax,54,y,s,9.8)
        txt(ax,35,105,'BASE DOCUMENTAL',8.5,MUTED,'bold')
        txt(ax,35,90,'Geometria: Pedestal_MDF.scad • Inventário: Lista_de_pecas.csv\n'+
            'Montagem: LEIA_PRIMEIRO.md do pedestal e da caixa V4.\n'+
            'As conferências digitais não substituem a avaliação física do protótipo.',8.4,MUTED)
        save(pdf,fig)

    assert len(PAGES)==TOTAL
    # Conferência de margens de texto na página, sem depender apenas da extração PDF.
    overflow=[]
    for num,(fig,ax,title) in enumerate(PAGES,1):
        fig.canvas.draw(); renderer=fig.canvas.get_renderer()
        for artist in fig.findobj(match=matplotlib.text.Text):
            if not artist.get_visible() or not artist.get_text():continue
            bb=artist.get_window_extent(renderer)
            # Ticks invisíveis dos eixos não integram o documento.
            if artist.axes is not None and not artist.axes.axison and artist not in artist.axes.texts:continue
            fbb=fig.bbox
            if bb.x0 < -1 or bb.y0 < -1 or bb.x1>fbb.width+1 or bb.y1>fbb.height+1:
                overflow.append({'pagina':num,'texto':artist.get_text()})
    report={'paginas':len(PAGES),'formato':'A4 retrato','pecas_modelo':len(NAMES),
            'ranhuras_tampo':25,'inventario_conferido_com_csv':True,
            'modelo_sha256':hashlib.sha256(MODEL.read_bytes()).hexdigest(),
            'textos_fora_da_pagina':overflow,'ilustracoes':'Contornos e matrizes reais do SCAD; detalhes de cola esquemáticos',
            'escopo':'Manual; não altera geometria de fabricação nem certifica resistência'}
    (OUT/'VERIFICACAO_manual.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    for fig,_,_ in PAGES:plt.close(fig)
    try:
        import fitz
        from PIL import Image,ImageOps,ImageDraw
        doc=fitz.open(pdfpath)
        thumbs=[]
        for i,p in enumerate(doc):
            pix=p.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False)
            pix.save(OUT/f'pagina_{i+1:02d}.png')
            im=Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
            im.thumbnail((238,337))
            card=Image.new('RGB',(258,367),'#dce1e2');card.paste(im,((258-im.width)//2,8))
            ImageDraw.Draw(card).text((12,347),f'{i+1:02d}',fill='#23333b')
            thumbs.append(card)
        contact=Image.new('RGB',(258*3,367*5),'white')
        for i,im in enumerate(thumbs):contact.paste(im,((i%3)*258,(i//3)*367))
        contact.save(OUT/'Visao_geral_do_manual.png')
        report['texto_extraido_por_pagina']=[len(p.get_text()) for p in doc]
        report['dimensoes_pdf_pt']=[list(p.rect)[2:] for p in doc]
        overlaps=[]
        for i,p in enumerate(doc):
            words=p.get_text('words')
            for j,a in enumerate(words):
                r=fitz.Rect(a[:4])
                for b in words[j+1:]:
                    q=fitz.Rect(b[:4]); intersection=r & q
                    if intersection.is_empty:continue
                    if (intersection.width>min(r.width,q.width)*.3 and
                        intersection.height>min(r.height,q.height)*.5):
                        overlaps.append({'pagina':i+1,'palavras':[a[4],b[4]]})
        report['sobreposicoes_de_texto_pdf']=overlaps
        assert not overlaps,overlaps
        assert all(len(p.get_text())>500 for p in doc)
        (OUT/'VERIFICACAO_manual.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
    except ImportError:
        pass
    print(json.dumps({'pdf':str(pdfpath),'paginas':len(PAGES),'textos_fora_da_pagina':overflow},ensure_ascii=False))


if __name__=='__main__':
    main()
