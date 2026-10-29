#!/usr/bin/env python3
"""Gera cortes nominais em mm, sem compensação de kerf. Python 3, só stdlib.
Exemplo: python3 gerar_mdf_v6.py --parede 3 --apoio 6 --folga 0.4
Regenerar também STL com OpenSCAD após mudar qualquer parâmetro.
"""
from pathlib import Path
import argparse, json, math, html

ROOT = Path(__file__).resolve().parents[1]
p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--parede', type=float, default=3)
p.add_argument('--apoio', type=float, default=6)
p.add_argument('--folga', type=float, default=.4, help='folga total nominal das luvas')
a = p.parse_args()
t, b, f = a.parede, a.apoio, a.folga
assert 2 <= t <= 4 and 4 <= b <= 8 and .2 <= f <= 1
E = 120 + 2*t
altura = 62.4-t
parts = []

def rect(x,y,w,h):
    return [(x,y),(x+w,y),(x+w,y+h),(x,y+h)]

def part(id, title, material, qty, outer, holes=None, note=''):
    parts.append(dict(id=id,titulo=title,espessura_mm=material,quantidade=qty,
                      contorno=outer,furos=holes or [],nota=note))

# Duas faces largas cobrem as bordas das duas laterais: interior 120 x 120.
part('M01','Teto/piso do módulo de entrada 200 mm',t,2,rect(0,0,200,E))
part('M02','Lateral da entrada 200 mm',t,2,rect(0,0,200,120))
part('M03','Teto/piso do módulo de saída 200 mm',t,2,rect(0,0,200,E))
part('M04','Lateral da saída 200 mm',t,2,rect(0,0,200,120))

def foot(width,saddle,z,cradle):
    # Perfil YZ. Patamar superior em z; aba sobe 4 mm; pernas 14 mm.
    g=cradle/2; s=saddle/2; w=width/2
    outer=[(-w,0),(w,0),(w,b),(s-6,b),(s-6,z-b),
           (s,z-b),(s,z+4),(g,z+4),(g,z),(-g,z),
           (-g,z+4),(-s,z+4),(-s,z-b),(-s+6,z-b),(-s+6,b),(-w,b)]
    # Abertura deixa a travessa de b mm e duas pernas de 14 mm.
    hole=rect(-s+20,b,saddle-40,z-2*b)
    return [(x+w,y) for x,y in outer], [[(x+w,y) for x,y in hole]]

o,h=foot(160,140,altura,E+.4)
part('M13','Lâmina do pé dos dutos (4 pés, 4 lâminas/pé)',b,16,o,h,
     'Colar quatro lâminas; espessura final 4*apoio. Furar verticalmente Ø4,5 em Y=±73, X=0 após colagem.')
o,h=foot(180,158,47.4,150.4)
part('M19','Lâmina do pé da ventoinha (4 lâminas)',b,4,o,h,
     'Colar quatro lâminas. Furar verticalmente Ø4,5 em Y=±83, X=0 após colagem.')

o,h=foot(160,140,60,125.2)
part('M23','Lâmina do apoio próprio da câmara (4 lâminas)',b,4,o,h,'Patamar 60 mm; centro X=350; furar como M13.')

# Base opcional bipartida: junta x=375 e duas talas por baixo.
holes=[(25,110-73,2.25),(25,110+73,2.25),(150,110-73,2.25),(150,110+73,2.25)]
holes += [(x,110+y,2.25) for x in (220,261) for y in (-22,22)]
holes += [(325,110+y,2.25) for y in (-80,80)]
holes += [(350,110+y,2.25) for y in (-73,73)]
part('B01','Base opcional: metade da entrada',b,1,rect(0,0,375,220),holes)
holes=[(x-375,110+y,2.25) for x in (450,550) for y in (-73,73)]
holes += [(695-375,110+y,2.25) for y in (-83,83)]
holes += [(425-375,110+y,2.25) for y in (-80,80)]
part('B02','Base opcional: metade da saída',b,1,rect(0,0,375,220),holes)
part('B03','Tala inferior da base opcional',b,2,rect(0,0,200,40),[(50,20,2.25),(150,20,2.25)])
part('G13','Gabarito para furar verticalmente os pés dos dutos',t,1,rect(0,0,4*b,160),[(2*b,7,2.25),(2*b,153,2.25)])
part('G19','Gabarito para furar verticalmente o pé da ventoinha',t,1,rect(0,0,4*b,180),[(2*b,7,2.25),(2*b,173,2.25)])
part('T01','Cupom: piso/teto para montar tubo curto',t,2,rect(0,0,20,E))
part('T02','Cupom: lateral para montar tubo curto',t,2,rect(0,0,20,120))
part('T03','Cupom para medir kerf e testar furo M4',t,1,rect(0,0,50,30),
     [rect(5,5,10,10),(30,15,2.25)],'Guardar quadrado interno de 10 mm. Kerf aproximado=(abertura-quadrado)/2.')

def bounds(pt):
    return max(x for x,y in pt['contorno']),max(y for x,y in pt['contorno'])

def inside(x,y,poly):
    flag=False
    for (ax,ay),(bx,by) in zip(poly,poly[1:]+poly[:1]):
        if (ay>y)!=(by>y) and x < (bx-ax)*(y-ay)/(by-ay)+ax:
            flag=not flag
    return flag

def area(poly):
    return abs(sum(x*v-u*y for (x,y),(u,v) in zip(poly,poly[1:]+poly[:1])))/2

def coords(seq):
    return ' '.join(f'{x:.4f},{y:.4f}' for x,y in seq)

def svg(items,w,h,labels=False):
    out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}">',
         '<title>Corte MDF V7: mm, escala 1:1, contornos nominais</title>']
    if labels: out += [f'<rect width="{w}" height="{h}" fill="#f7f2e6"/>']
    for pt,x,y in items:
        out += [f'<g id="{pt["id"]}" transform="translate({x} {y})" fill="none" stroke="#ff0000" stroke-width="0.1">',
                f'<polygon points="{coords(pt["contorno"])}"/>']
        for h in pt['furos']:
            if isinstance(h,tuple): out += [f'<circle cx="{h[0]}" cy="{h[1]}" r="{h[2]}"/>']
            else: out += [f'<polygon points="{coords(h)}"/>']
        out += ['</g>']
        if labels:
            out += [f'<text x="{x+5}" y="{y+12}" font-family="sans-serif" font-size="5" fill="#334155">{pt["id"]}</text>']
    return '\n'.join(out+['</svg>'])

def dxf(items):
    out=['0','SECTION','2','HEADER','9','$INSUNITS','70','4','0','ENDSEC','0','SECTION','2','ENTITIES']
    def poly(points,x,y):
        out.extend(['0','POLYLINE','8','CORTE','66','1','70','1'])
        for u,v in points: out.extend(['0','VERTEX','8','CORTE','10',str(u+x),'20',str(v+y),'30','0'])
        out.extend(['0','SEQEND'])
    for pt,x,y in items:
        poly(pt['contorno'],x,y)
        for h in pt['furos']:
            if isinstance(h,tuple):
                out.extend(['0','CIRCLE','8','CORTE','10',str(h[0]+x),'20',str(h[1]+y),'30','0','40',str(h[2])])
            else: poly(h,x,y)
    return '\n'.join(out+['0','ENDSEC','0','EOF'])+'\n'

for pt in parts:
    w,h=bounds(pt)
    assert 0<w<=590 and 0<h<=390
    assert area(pt['contorno'])>0
    for hole in pt['furos']:
        samples=([(hole[0]+hole[2]*math.cos(i*math.pi/36),hole[1]+hole[2]*math.sin(i*math.pi/36)) for i in range(72)]
                 if isinstance(hole,tuple) else hole)
        assert all(inside(x,y,pt['contorno']) for x,y in samples),pt['id']
    pt['dimensoes_mm']=[w,h]
    path=ROOT/'02_CORTE_LASER'/'pecas_individuais'/f'MDF_{pt["espessura_mm"]:g}mm'
    path.mkdir(parents=True,exist_ok=True)
    (path/f'{pt["id"]}.svg').write_text(svg([(pt,0,0)],w,h))
    (path/f'{pt["id"]}.dxf').write_text(dxf([(pt,0,0)]))

layouts=[]
# Cupons separados do lote. Base opcional também separada para reaproveitar base existente.
groups=[('dutos',t,[q for q in parts if q['id'] in ('M01','M02','M03','M04','G13','G19')]),
        ('pes',b,[q for q in parts if q['id'] in ('M13','M19','M23')]),
        ('base_opcional',b,[q for q in parts if q['id'].startswith('B')]),
        ('cupons',t,[q for q in parts if q['id'].startswith('T')])]
for group,thick,pts in groups:
    copies=[pt for pt in pts for _ in range(pt['quantidade'])]
    copies.sort(key=lambda pt: (-bounds(pt)[1],-bounds(pt)[0]))
    sheets=[]; sheet=[]; x=y=5.; row=0.
    for pt in copies:
        w,h=bounds(pt)
        if x+w>595: x=5.; y+=row+5; row=0.
        if y+h>395:
            sheets.append(sheet); sheet=[]; x=y=5.; row=0.
        sheet.append((pt,x,y)); x+=w+5; row=max(row,h)
    if sheet: sheets.append(sheet)
    for i,items in enumerate(sheets,1):
        name=f'{group}_{thick:g}mm_chapa_{i:02d}'
        for pt,x,y in items:
            w,h=bounds(pt)
            assert 5<=x and 5<=y and x+w<=595 and y+h<=395
        for j,(pt,x,y) in enumerate(items):
            w,h=bounds(pt)
            for qt,u,v in items[j+1:]:
                ww,hh=bounds(qt)
                assert x+w<=u or u+ww<=x or y+h<=v or v+hh<=y
        dest=ROOT/'02_CORTE_LASER'/f'MDF_{thick:g}mm'/group
        dest.mkdir(parents=True,exist_ok=True)
        (dest/f'{name}.svg').write_text(svg(items,600,400))
        (dest/f'{name}.dxf').write_text(dxf(items))
        (ROOT/'05_VISUALIZACAO'/'mapas_chapas').mkdir(parents=True,exist_ok=True)
        (ROOT/'05_VISUALIZACAO'/'mapas_chapas'/f'{name}_MAPA_NAO_CORTAR.svg').write_text(svg(items,600,400,True))
        layouts.append(dict(caminho=str((dest/name).relative_to(ROOT)),arquivo=name,grupo=group,espessura_mm=thick,
                            pecas=[dict(id=q['id'],x=x,y=y) for q,x,y in items]))


manifest=dict(revisao='V7',parede_mm=t,apoio_mm=b,folga_mm=f,pecas=parts,chapas=layouts,mesa_mm=[600,400],margem_mm=5,kerf_compensado=False)
(ROOT/'06_CAD_VALIDACAO'/'cortes.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
print('Cortes:',len(parts),'tipos;',len(layouts),'chapas incluindo cupons e base opcional')
