#!/usr/bin/env python3
"""Pedestal MDF: estrutura laser 600x400 e tampo laser 500x380, em milímetros.

Requer shapely>=1.8, numpy e matplotlib. Não aplica compensação de kerf.
Folga de encaixe é total; medir espessura e calibrar antes de fabricar.
"""
from pathlib import Path
import argparse
import csv
import json
import math
import shutil
import numpy as np
from shapely.geometry import Polygon, box, Point
from shapely.affinity import translate, rotate
from shapely.ops import unary_union
from shapely.geometry.polygon import orient
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as Patch, Rectangle, PathPatch
from matplotlib.path import Path as MPath


def cli():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--espessura', type=float, default=3)
    p.add_argument('--folga', type=float, default=.15)
    p.add_argument('--saida', type=Path, default=Path(__file__).resolve().parents[1])
    return p.parse_args()


def contours(g):
    g = orient(g, sign=1)
    return [list(g.exterior.coords)[:-1]] + [list(r.coords)[:-1] for r in g.interiors]


def svg(path, objects, w=600, h=400):
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.6f}mm" height="{h:.6f}mm" viewBox="0 0 {w:.6f} {h:.6f}">',
             '<title>Contornos finais, milimetros, 1:1, sem compensacao de ferramenta</title>',
             '<g fill="none" stroke="#000000" stroke-width="0.05">']
    for ident, g in objects:
        for i, ring in enumerate(contours(g)):
            d = 'M ' + ' L '.join(f'{x:.6f},{h-y:.6f}' for x, y in ring) + ' Z'
            lines.append(f'<path id="{ident}_{i}" d="{d}"/>')
    lines += ['</g>', '</svg>']
    path.write_text('\n'.join(lines), encoding='utf-8')


def dxf(path, objects):
    # AC1015 supports LWPOLYLINE and explicit mm units; all rings closed.
    lines = []
    def put(*values):
        lines.extend(str(v) for v in values)
    put(0,'SECTION',2,'HEADER',9,'$ACADVER',1,'AC1015',9,'$INSUNITS',70,4,
        9,'$MEASUREMENT',70,1,0,'ENDSEC',0,'SECTION',2,'TABLES',0,'TABLE',
        2,'LAYER',70,1,0,'LAYER',2,'CORTE',70,0,62,7,6,'CONTINUOUS',
        0,'ENDTAB',0,'ENDSEC',0,'SECTION',2,'ENTITIES')
    for ident, g in objects:
        for ring in contours(g):
            put(0,'LWPOLYLINE',100,'AcDbEntity',8,'CORTE',100,'AcDbPolyline',
                90,len(ring),70,1)
            for x, y in ring:
                put(10,f'{x:.6f}',20,f'{y:.6f}')
    put(0,'ENDSEC',0,'EOF')
    path.write_text('\n'.join(lines)+'\n', encoding='ascii')


def path_patch(g, color):
    verts, codes = [], []
    for ring in contours(g):
        verts += ring + [ring[0]]
        codes += [MPath.MOVETO] + [MPath.LINETO]*(len(ring)-1) + [MPath.CLOSEPOLY]
    return PathPatch(MPath(verts, codes), facecolor=color, edgecolor='#33434b', lw=.5)


def main():
    a = cli()
    T, C = a.espessura, a.folga
    if not 2.5 <= T <= 3.5 or not 0 <= C <= .4:
        raise ValueError('Projeto para MDF próximo de 3 mm; folga total entre 0 e 0,4 mm.')
    root = a.saida.resolve()
    folders = ['01_CHAPAS_DXF','02_CHAPAS_SVG','03_PECAS_INDIVIDUAIS',
               '04_MODELOS_3D','05_GUIA','06_TESTE_ENCAIXE','07_FONTE',
               '08_TAMPO_LASER_500x380']
    for f in folders:
        (root/f).mkdir(parents=True, exist_ok=True)
    W, D, BW, BD = 340., 300., 440., 340.
    TW, TD = 500., 380.
    HF, S = 860., .16
    HT = HF + S*D
    COS = 1/math.sqrt(1+S*S)
    SIN = S*COS
    ANGLE = math.degrees(math.atan(S))
    CAPX, CAPY = (W-TW)/2, D/2-TD*COS/2
    BASEZ = 3*T
    BX, BY = (BW-W)/2, (BD-D)/2
    LEVELS = [HT*i/4 for i in range(1,4)]
    AMP = 4.
    parts, by_id, boards = [], {}, []
    palette = {'F':'#e9b678','T':'#b98a65','E':'#77a9a9','D':'#95a8c6',
               'B':'#b7bf91','H':'#cfbb93','G':'#c390b1','R':'#d5c7ad','A':'#9ab691'}

    def clean(g):
        if g.geom_type == 'GeometryCollection':
            g=unary_union([p for p in g.geoms if p.geom_type in ['Polygon','MultiPolygon']])
        g = g.simplify(1e-8, preserve_topology=True)
        if not g.is_valid or g.geom_type != 'Polygon' or g.area <= 0:
            raise ValueError(f'Contorno inválido: {g.geom_type}')
        return g

    def add(ident, g, kind, matrix, note=''):
        g = clean(g)
        x0,y0,x1,y1 = g.bounds
        flat = translate(g,-x0,-y0)
        part = dict(id=ident,g=g,flat=flat,kind=kind,matrix=matrix,
                    dims=[x1-x0,y1-y0],note=note)
        parts.append(part)
        by_id[ident] = part
        return part

    def matwall(k):
        if k=='F': return [[1,0,0,BX],[0,0,1,BY],[0,1,0,BASEZ],[0,0,0,1]]
        if k=='T': return [[1,0,0,BX],[0,0,1,BY+D-T],[0,1,0,BASEZ],[0,0,0,1]]
        if k=='E': return [[0,0,1,BX],[1,0,0,BY],[0,1,0,BASEZ],[0,0,0,1]]
        return [[0,0,1,BX+W-T],[1,0,0,BY],[0,1,0,BASEZ],[0,0,0,1]]

    def flatmat(x,y,z):
        return [[1,0,0,x],[0,1,0,y],[0,0,1,z],[0,0,0,1]]

    def comb(height):
        anchors = [0]+[z for z in LEVELS if z < height]+[height]
        rows = []
        for low,high in zip(anchors,anchors[1:]):
            n = math.ceil((high-low)/28)
            if n%2==0: n+=1
            rows += [(low+i*(high-low)/n,low+(i+1)*(high-low)/n,i%2==0)
                     for i in range(n)]
        return rows

    def seam(length,z):
        pts=[(0,z),(T,z)]
        n=14
        for i in range(n):
            x0=T+i*(length-2*T)/n
            x1=T+(i+1)*(length-2*T)/n
            y=z+(AMP if i%2==0 else -AMP)
            pts += [(x0,y),(x1,y)]
        return Polygon([(0,-100),(length,-100)]+list(reversed(pts+[(length-T,z),(length,z)])))

    # Three transverse ribs and two longitudinal ribs. Positions in the actual
    # inclined top coordinate system, not its horizontal projection.
    # Trim 10 mm at each depth edge; preserve all existing lattice/world positions.
    XS = [90.,190.,290.]
    YS = [125.,375.]
    RIB_Y = [CAPY+s*COS for s in XS]
    RIB_X = [CAPX+s for s in YS]
    tab_wall = {'F':[90.,170.,250.], 'T':[90.,170.,250.],
                'E':[100.,200.], 'D':[100.,200.]}
    bottom_tabs = {'F':[60.,170.,280.], 'T':[60.,170.,280.],
                   'E':[60.,150.,240.], 'D':[60.,150.,240.]}
    fullwalls = {}
    for k in 'FTED':
        length = W if k in 'FT' else D
        h0,h1 = (HF,HF) if k=='F' else (HT-S*T,HT-S*T) if k=='T' else (HF,HT)
        if k in 'ED':
            # Remove the tiny rear triangle that would only touch the side at
            # one point above the rear corner finger; it is not a usable part.
            g = Polygon([(0,0),(length,0),(length,HT-S*T),
                         (length-T,HT-S*T),(0,h0)])
        else:
            g = Polygon([(0,0),(length,0),(length,h1),(0,h0)])
        removals=[]
        for edge,H in enumerate((h0,h1)):
            lo,hi = (0,T) if edge==0 else (length-T,length)
            # Rear side corners stop at the rear panel's low edge; the final
            # 0.48 mm remains below the inclined cap.
            Hcorner = HF if (k=='F' or k in 'ED' and edge==0) else HT-S*T
            for z0,z1,front_owner in comb(Hcorner):
                if (not front_owner) if k in 'FT' else front_owner:
                    removals.append(box(lo,z0-C/2,hi,z1+C/2))
        # Cross lap with the upper support lattice: walls receive the upper slot.
        locations = RIB_X if k in 'FT' else RIB_Y
        def top(u):
            return h0 if k in 'FT' else HF+S*u
        for u in locations:
            z=top(u)
            removals.append(box(u-C/2,z-35-S*(T+C),u+T+C/2,z+15))
        g=g.difference(unary_union(removals))
        additions=[]
        for u in tab_wall[k]:
            lo,hi=u-10,u+10
            z0,z1=top(lo),top(hi)
            # Teeth go through 3 mm of the inclined plate, ending flush after sanding.
            extra=S*T if k in 'FT' else 0
            additions.append(Polygon([(lo,z0-1),(hi,z1-1),
                                       (hi,z1+extra+T/COS),(lo,z0+extra+T/COS)]))
        for u in bottom_tabs[k]:
            additions.append(box(u-10,-T,u+10,1))
        g=clean(unary_union([g]+additions))
        fullwalls[k]=g
        for i in range(4):
            piece=g
            if i<3: piece=piece.intersection(seam(length,LEVELS[i]))
            if i: piece=piece.difference(seam(length,LEVELS[i-1]))
            add(f'{k}{i+1}',piece,k,matwall(k),f'{k}: faixa {i+1}, de baixo para cima')

    # Three layers of one-piece floor; only the upper one has wall mortises.
    floor_holes=[]
    for k in 'FTED':
        for u in bottom_tabs[k]:
            if k in 'FT':
                y=BY+(0 if k=='F' else D-T)
                hole=box(BX+u-10-C/2,y-C/2,BX+u+10+C/2,y+T+C/2)
            else:
                x=BX+(0 if k=='E' else W-T)
                hole=box(x-C/2,BY+u-10-C/2,x+T+C/2,BY+u+10+C/2)
            floor_holes.append(hole)
    for i in range(3):
        g=box(0,0,BW,BD)
        if i==2: g=g.difference(unary_union(floor_holes))
        add(f'B{i+1}',g,'B',flatmat(0,0,i*T),'Camada da base laminada, de baixo para cima')

    # Closed horizontal diaphragms resist racking and halve the free wall height.
    for i,z in enumerate([320.,620.],1):
        add(f'H{i}',box(0,0,W-2*T-C,D-2*T-C),'H',
            flatmat(BX+T+C/2,BY+T+C/2,BASEZ+z-T),'Divisória horizontal interna')
        for k in 'FTED':
            length=(W if k in 'FT' else D)-60
            if k=='F': m=flatmat(BX+30,BY+T,BASEZ+z-T)
            elif k=='T': m=flatmat(BX+30,BY+D-2*T,BASEZ+z-T)
            elif k=='E': m=[[0,0,1,BX+T],[1,0,0,BY+30],[0,1,0,BASEZ+z-20],[0,0,0,1]]
            else: m=[[0,0,1,BX+W-2*T],[1,0,0,BY+30],[0,1,0,BASEZ+z-20],[0,0,0,1]]
            # Cleats are vertical strips, 20 mm high. Diaphragm underside rests
            # on their top edge at z-T, independently of splice reinforcements.
            if k in 'FT':
                m=matwall(k)
                m[1][3]=BY+T if k=='F' else BY+D-2*T
                m[0][3]=BX+30
                m[2][3]=BASEZ+z-T-20
            else:
                m[2][3]=BASEZ+z-T-20
            add(f'A{i}{k}',box(0,0,length,20),'A',m,'Apoio colado sob a divisória H'+str(i))

    # Internal splice plates: 30 mm glued across each wall seam.
    for k in 'FTED':
        for i,z in enumerate(LEVELS,1):
            length=(W if k in 'FT' else D)-60
            m=matwall(k)
            if k in 'FT':
                m[0][3]+=30
                m[1][3]=BY+T if k=='F' else BY+D-2*T
            else:
                m[1][3]+=30
                m[0][3]=BX+T if k=='E' else BX+W-2*T
            m[2][3]=BASEZ+z-15
            add(f'R{k}{i}',box(0,0,length,30),'R',m,'Reforço colado na emenda '+k+str(i))

    top_holes=[]
    def add_top_rect(x0,s0,x1,s1):
        top_holes.append(box(x0-C/2,s0-C/2,x1+C/2,s1+C/2))
    # Exact projection of a vertical tab through the inclined top thickness.
    # A slot in the transverse direction also includes T*tan(angle).
    for k in 'FTED':
        for u in tab_wall[k]:
            if k in 'FT':
                y=0 if k=='F' else D-T
                add_top_rect(u-10-CAPX,(y-CAPY)/COS,
                             u+10-CAPX,(y+T-CAPY)/COS+T*S)
            else:
                x=0 if k=='E' else W-T
                add_top_rect(x-CAPX,(u-10-CAPY)/COS,
                             x+T-CAPX,(u+10-CAPY)/COS+T*S)

    # Gx: horizontal transverse ribs, underside slots at walls, top slots at Gy.
    rib_length=TW-36
    for i,(s,y) in enumerate(zip(XS,RIB_Y),1):
        topz=HF+S*y
        g=box(0,-70,rib_length,0)
        for bodyx in [0,W-T]:
            q=bodyx-(CAPX+18)
            g=g.difference(box(q-C/2,-71,q+T+C/2,-35+S*(T+C)))
        for bodyx in RIB_X:
            q=bodyx-(CAPX+18)
            g=g.difference(box(q-C/2,-35,q+T+C/2,1))
        for xt in [30.,250.,470.]:
            q=xt-18
            g=g.union(box(q-10,-1,q+10,T/COS+S*T))
            add_top_rect(xt-10,s,xt+10,s+T/COS+T*S)
        m=[[1,0,0,BX+CAPX+18],[0,0,1,BY+y],[0,1,0,BASEZ+topz],[0,0,0,1]]
        add(f'GX{i}',g,'G',m,'Travessa superior X, posição s='+str(s))

    # Gy: inclined longitudinal ribs, bottom slots at both walls and Gx.
    qlen=(TD-16)*COS
    ystart=CAPY+8*COS
    for i,x in enumerate(RIB_X,1):
        g=Polygon([(0,-70),(qlen,S*qlen-70),(qlen,S*qlen),(0,0)])
        for y in [0,D-T]+RIB_Y:
            q=y-ystart
            lo,hi=q-C/2,q+T+C/2
            cut=Polygon([(lo,S*lo-71),(hi,S*hi-71),
                         (hi,S*hi-35+S*(T+C)),(lo,S*lo-35+S*(T+C))])
            g=g.difference(cut)
        for st in [20.,TD/2,TD-20]:
            lo,hi=(st-10-8)*COS,(st+10-8)*COS
            g=g.union(Polygon([(lo,S*lo-1),(hi,S*hi-1),
                               (hi,S*hi+T/COS),(lo,S*lo+T/COS)]))
            add_top_rect(x-CAPX,st-10,x+T-CAPX,st+10+T*S)
        m=[[0,0,1,BX+x],[1,0,0,BY+ystart],
           [0,1,0,BASEZ+HF+S*ystart],[0,0,0,1]]
        add(f'GY{i}',g,'G',m,'Longarina superior Y, posição x='+str(YS[i-1]))

    cap=clean(box(0,0,TW,TD).difference(unary_union(top_holes)))
    capmat=[[1,0,0,BX+CAPX],[0,COS,-SIN,BY+CAPY],
            [0,SIN,COS,BASEZ+HF+S*CAPY],[0,0,0,1]]
    capdata=dict(id='TAMPO',g=cap,flat=cap,kind='P',matrix=capmat,dims=[TW,TD])

    def put_board(name, ids, positions):
        objects=[]
        for ident,(x,y,ang) in zip(ids,positions):
            p=by_id[ident]
            g=rotate(p['flat'],ang,origin=(0,0))
            x0,y0,_,_=g.bounds
            g=translate(g,x-x0,y-y0)
            objects.append((ident,g))
        boards.append(dict(name=name,objects=objects))

    # Two major wall panels rotated 90 degrees on each of eight sheets.
    for k in 'FTED':
        for j in [0,2]:
            ids=[f'{k}{j+1}',f'{k}{j+2}']
            w0=by_id[ids[0]]['dims'][1]
            put_board(f'{len(boards)+1:02d}_{ids[0]}_{ids[1]}',ids,[(20,20,90),(20+w0+8,20,90)])
    for ident in ['B1','B2','B3','H1','H2']:
        put_board(f'{len(boards)+1:02d}_{ident}',[ident],[(20,20,0)])
    put_board('14_GX1_GX2_GY1',['GY1','GX1','GX2'],
              [(20,20,0),(20,20+by_id['GY1']['dims'][1]+8,0),
               (20,20+by_id['GY1']['dims'][1]+8+by_id['GX1']['dims'][1]+8,0)])
    put_board('15_GX3_GY2',['GY2','GX3'],
              [(20,20,0),(20,20+by_id['GY2']['dims'][1]+8,0)])

    # Pack splice plates and cleats in the free rectangular strips. Candidate
    # positions follow existing rectangle edges, with an 8 mm clearance.
    small=[p for p in parts if p['kind'] in 'RA']
    small.sort(key=lambda p:p['g'].area,reverse=True)
    usable=box(20,20,580,380)
    for p in small:
        found=False
        for b in boards:
            occupied=[g.bounds for _,g in b['objects']]
            for ang in [90,0]:
                candidate=rotate(p['flat'],ang,origin=(0,0))
                x0,y0,x1,y1=candidate.bounds
                candidate=translate(candidate,-x0,-y0)
                w,h=x1-x0,y1-y0
                xvalues=sorted({20.}|{q[2]+8 for q in occupied})
                yvalues=sorted({20.}|{q[3]+8 for q in occupied})
                for x in xvalues:
                    if x+w > 580+1e-7: continue
                    for y in yvalues:
                        if y+h > 380+1e-7: continue
                        if all(x>=qx1+8-1e-7 or x+w<=qx0-8+1e-7 or
                               y>=qy1+8-1e-7 or y+h<=qy0-8+1e-7
                               for qx0,qy0,qx1,qy1 in occupied):
                            g=translate(candidate,float(x),float(y))
                            b['objects'].append((p['id'],g))
                            found=True
                            break
                    if found: break
                if found: break
            if found: break
        if not found:
            raise ValueError('Falta espaço para '+p['id'])

    # Fabrication safeguards, part of generation (not a physical load test).
    inventory=[]
    min_gap=1e9
    for b in boards:
        for ident,g in b['objects']:
            if not usable.buffer(1e-7).covers(g):
                raise ValueError(f'Peça fora da área útil: {ident} {g.bounds}')
            inventory.append(ident)
            by_id[ident]['sheet']=b['name']
        for i,(_,g) in enumerate(b['objects']):
            for _,h in b['objects'][i+1:]:
                dist=g.distance(h)
                min_gap=min(min_gap,dist)
                if dist<7.999999:
                    raise ValueError('Distância entre peças menor que 8 mm.')
    if sorted(inventory)!=sorted(by_id):
        raise ValueError('Inventário de corte incompleto ou duplicado.')
    for k,g in fullwalls.items():
        reconstruction=unary_union([by_id[f'{k}{i}']['g'] for i in range(1,5)])
        if reconstruction.symmetric_difference(g).area>1e-5:
            raise ValueError('As faixas não reconstroem a parede '+k)
    if len(cap.interiors)!=len(top_holes):
        raise ValueError('Furos do tampo coincidem ou se sobrepõem.')

    for b in boards:
        dxf(root/'01_CHAPAS_DXF'/f'{b["name"]}.dxf',b['objects'])
        svg(root/'02_CHAPAS_SVG'/f'{b["name"]}.svg',b['objects'])
    for p in parts:
        dxf(root/'03_PECAS_INDIVIDUAIS'/f'{p["id"]}.dxf',[(p['id'],p['flat'])])
        svg(root/'03_PECAS_INDIVIDUAIS'/f'{p["id"]}.svg',[(p['id'],p['flat'])],*p['dims'])
    dxf(root/'08_TAMPO_LASER_500x380'/'TAMPO_INTEIRO_500x380.dxf',[('TAMPO',cap)])
    svg(root/'08_TAMPO_LASER_500x380'/'TAMPO_INTEIRO_500x380.svg',[('TAMPO',cap)],TW,TD)
    # Laser top is one intact sheet on the user's CNC laser; no halves or indexing jobs.

    # Small kerf and thickness coupon, 180x200 usable envelope.
    coupon=[]
    for i,delta in enumerate([-.10,0,.10,.15,.20,.25,.30]):
        y=20+i*22
        hole=box(28,y+5,48,y+5+T+delta)
        coupon.append((f'RANHURA_{delta:+.2f}',box(20,y,58,y+18).difference(hole)))
        # Finger width gauge checks in-plane laser compensation as well.
        coupon.append((f'DENTE_{i}',box(70,y,105,y+18).union(box(105,y+5,125,y+5+T))))
    coupon.append(('REGUA_100mm',box(20,185,120,195)))
    svg(root/'06_TESTE_ENCAIXE'/'00_CALIBRAR_MDF_3mm.svg',coupon)
    dxf(root/'06_TESTE_ENCAIXE'/'00_CALIBRAR_MDF_3mm.dxf',coupon)

    # SCAD uses exact 2D polygons and world transforms, includes all reinforcements.
    all3d=parts+[capdata]
    scad='''/* Estrutura e tampo a laser, mm. Gerado por 07_FONTE/gerar_pedestal.py.
Contornos sem compensação de kerf. Tampo verdadeiro 500x380; tampo inteiro para CNC a laser, inclinação 9,09 graus.
Regenerar para outra espessura/folga. STL serve para visualização, DXF/SVG para corte.
*/
modo="montado"; // [montado,explodido,peca2d,peca3d,chapa2d,chapas]
numero_peca=1;
numero_chapa=1;
mostrar_tampo=true;
mostrar_paredes=true;
mostrar_lastro=false;
'''
    arrays={
        'esp':T,'nomes':[p['id'] for p in all3d],
        'contornos':[contours(p['g']) for p in all3d],
        'planos':[contours(p['flat']) for p in all3d],
        'matrizes':[p['matrix'] for p in all3d],
        'tipos':[p['kind'] for p in all3d],
        'chapas':[[contours(g) for _,g in b['objects']] for b in boards]
    }
    for key,value in arrays.items():
        scad+=key+'='+json.dumps(value,separators=(',',':'))+';\n'
    scad+='''
module perfil(rings) {
    difference() {
        polygon(rings[0]);
        if(len(rings)>1) for(j=[1:len(rings)-1]) polygon(rings[j]);
    }
}
module montagem(explodida=false) {
    for(i=[0:len(nomes)-1]) {
        parede=tipos[i]=="F" || tipos[i]=="T" || tipos[i]=="E" || tipos[i]=="D";
        if((mostrar_paredes || !parede) && (mostrar_tampo || nomes[i]!="TAMPO"))
            color(nomes[i]=="TAMPO"?[.83,.78,.62]:tipos[i]=="G"?[.73,.50,.62]:
                  tipos[i]=="H"?[.71,.78,.60]:[.76,.60,.40])
            translate([0,0,explodida && nomes[i]=="TAMPO"?100:0])
            multmatrix(matrizes[i]) linear_extrude(esp) perfil(contornos[i]);
    }
    if(mostrar_lastro) color([.25,.3,.32,.6]) translate([80,50,9]) cube([280,220,110]);
}
module chapa(i) { for(r=chapas[i]) perfil(r); }
if(modo=="montado") montagem();
else if(modo=="explodido") montagem(true);
else if(modo=="peca2d") perfil(planos[numero_peca-1]);
else if(modo=="peca3d") linear_extrude(esp) perfil(planos[numero_peca-1]);
else if(modo=="chapa2d") chapa(numero_chapa-1);
else if(modo=="chapas") for(i=[0:len(chapas)-1])
    translate([(i%3)*620,floor(i/3)*420]) linear_extrude(esp) chapa(i);
else assert(false,"Modo desconhecido");
'''
    (root/'04_MODELOS_3D'/'Pedestal_MDF.scad').write_text(scad,encoding='utf-8')

    # Sheet identification map and inclined top locating drawing.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9})
    fig,axes=plt.subplots(5,3,figsize=(15,17))
    fig.suptitle('PEDESTAL MDF 3 mm | 15 chapas de 600 × 400 mm',fontsize=19)
    for ax,b in zip(axes.flat,boards):
        ax.add_patch(Rectangle((0,0),600,400,fc='white',ec='#667780',lw=.7))
        ax.add_patch(Rectangle((20,20),560,360,fill=False,ec='#b5b5b5',ls='--',lw=.7))
        for ident,g in b['objects']:
            ax.add_patch(path_patch(g,palette[by_id[ident]['kind']]))
            p=g.representative_point()
            ax.text(p.x,p.y,ident,ha='center',va='center',fontsize=8,fontweight='bold')
        ax.set(xlim=(-2,602),ylim=(-2,402),aspect='equal',title=b['name'])
        ax.axis('off')
    fig.text(.06,.015,'Área útil 560 × 360 mm · margem 20 mm por lado · intervalo mínimo 8 mm · tampo em pasta própria',fontsize=10)
    fig.tight_layout(rect=(0,.035,1,.97))
    fig.savefig(root/'05_GUIA'/'Mapa_das_15_chapas.png',dpi=140)
    fig.savefig(root/'05_GUIA'/'Mapa_das_15_chapas.pdf')
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(12,10))
    ax.add_patch(path_patch(cap,'#eee6d2'))
    ax.add_patch(Rectangle((-CAPX,-CAPY/COS),W,D/COS,fill=False,ec='#71999e',ls='--'))
    for s in XS: ax.plot([18,TW-18],[s,s],color='#b481a8',alpha=.45)
    for x in YS: ax.plot([x,x],[8,TD-8],color='#b481a8',alpha=.45)
    for i,g in enumerate(top_holes,1):
        p=g.centroid
        ax.text(p.x,p.y+6,str(i),fontsize=8,ha='center')
    ax.set(xlim=(-25,525),ylim=(-25,TD+25),aspect='equal',xlabel='x (mm)',ylabel='s, medido na chapa inclinada (mm)')
    ax.set_title('Tampo 500 × 380 mm | posições reais dos 25 encaixes',fontsize=16)
    ax.text(8,-18,'Azul: corpo 340 × 300 mm projetado no tampo. Roxo: grelha inferior. Frente baixa: s = 0.',fontsize=9)
    fig.tight_layout()
    fig.savefig(root/'05_GUIA'/'Tampo_encaixes.png',dpi=150)
    fig.savefig(root/'05_GUIA'/'Tampo_encaixes.pdf')
    plt.close(fig)

    rows=[]
    for p in parts:
        rows.append([p['id'],1,p['sheet'],round(p['dims'][0],3),round(p['dims'][1],3),p['note']])
    with (root/'05_GUIA'/'Lista_de_pecas.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f,delimiter=';')
        w.writerow(['Peça','Quantidade','Chapa','Largura_mm','Altura_mm','Montagem'])
        w.writerows(rows)
    hole_rows=[]
    for i,g in enumerate(top_holes,1):
        x0,s0,x1,s1=g.bounds
        hole_rows.append(dict(furo=i,x0=x0,s0=s0,x1=x1,s1=s1))
    (root/'08_TAMPO_LASER_500x380'/'Coordenadas_dos_encaixes.json').write_text(json.dumps(hole_rows,indent=2),encoding='utf-8')
    with (root/'08_TAMPO_LASER_500x380'/'Coordenadas_dos_encaixes.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=['furo','x0','s0','x1','s1'],delimiter=';')
        w.writeheader()
        w.writerows(hole_rows)
    params=dict(espessura=T,folga_total=C,base=[BW,BD],corpo=[W,D],tampo=[TW,TD],
                altura_frente=HF,altura_tras=HT,angulo_graus=ANGLE,
                maquina=[600,400],margem_por_lado=20,intervalo_pecas=8)
    (root/'07_FONTE'/'parametros.json').write_text(json.dumps(params,indent=2),encoding='utf-8')
    force,height,factor,lever=20.,.93,1.5,BD/2000
    required=factor*force*height/(9.81*lever)
    mdf_area=sum(p['g'].area for p in parts)+cap.area
    mass=mdf_area*1e-6*(T/1000)*700
    report=dict(**params,chapas_pedestal=len(boards),chapas_tampo_laser=1,
                tampo_inteiro=True,processo_tampo='laser',
                pecas_pedestal=len(parts),furos_tampo=len(top_holes),
                distancia_minima_entre_pecas=round(min_gap,5),
                contornos_validos=True,inventario_completo_sem_duplicatas=True,
                paredes_reconstruidas=True,kerf_compensado=False,
                massa_estimada_MDF_kg=round(mass,2),densidade_assumida_kg_m3=700,
                massa_total_minima_kg=round(required,2),forca_horizontal_assumida_N=force,
                altura_forca_m=height,fator_estatico=factor,
                prototipo_fisico_ensaiado=False)
    (root/'05_GUIA'/'DIMENSIONAMENTO.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    manual=f'''# Pedestal revisado — estrutura e tampo 500 × 380 mm a laser

Use esta pasta para fabricar a revisão. A pasta `Pedestal_MDF_17_pecas` contém a versão antiga.

## Medidas e material

- Tampo: **500 × 380 mm**, uma camada de MDF {T:g} mm, inclinação {ANGLE:.2f}°.
- Corpo: **340 × 300 mm**. Frente {HF:g} mm / traseira {HT:g} mm acima da base laminada.
- Base no chão: **440 × 340 mm**, três camadas coladas de MDF, total {3*T:g} mm.
- Altura no centro do tampo: {(BASEZ+HF+S*D/2+T*COS)/10:.1f} cm. Borda baixa/alta aproximadamente {(BASEZ+HF+S*CAPY+T*COS)/10:.1f}/{(BASEZ+HF+S*(CAPY+TD*COS)+T*COS)/10:.1f} cm.
- 15 chapas de 600 × 400 mm para o pedestal: 46 peças, incluindo reforços e apoios. O tampo é adicional.
- Área útil **560 × 360 mm**: 40 mm de folga total em cada dimensão, 20 mm por borda. Intervalo mínimo de 8 mm entre peças.
- Todas as peças são do mesmo MDF; as três bases viram uma única peça laminada de 9 mm. Divisórias H e grelha G também são de 3 mm.

## Arquivos para o laser

`01_CHAPAS_DXF` e `02_CHAPAS_SVG` são alternativas do mesmo corte. Cada arquivo numerado é uma chapa; as peças pequenas já estão incluídas. Os oito primeiros arquivos levam **duas peças grandes de parede em cada chapa**. Corte uma vez cada arquivo de 01 a 15.

Vetores em milímetros, escala 1:1, contornos fechados; furos e perímetros separados. Não há molduras nem textos de gravação nos arquivos de corte. A página SVG mede 600 × 400; a origem e o eixo Y no DXF são os usuais de CAD (o SVG tem Y invertido para representar a mesma disposição). Nomes e posição das peças aparecem em `05_GUIA/Mapa_das_15_chapas.pdf` e `.png`. `Lista_de_pecas.csv` informa todas as peças e chapas.

Os arquivos não têm compensação da largura do feixe. A folga total nominal é {C:g} mm nas ranhuras e nos cantos. Faça a compensação **uma vez no CAM**, exterior dos perímetros e interior dos furos. Use espessura medida, não redimensione o desenho. `06_TESTE_ENCAIXE` é um cupom de fabricação; as ranhuras, de baixo para cima, têm larguras {T-.1:g}, {T:g}, {T+.1:g}, {T+.15:g}, {T+.2:g}, {T+.25:g}, {T+.3:g} mm. Ajuste a espessura/folga no gerador se necessário. As emendas coplanares das paredes têm dentes nominais complementares, sem folga incorporada: dependem da compensação do feixe.

## Tampo inteiro para CNC a laser

Use `08_TAMPO_LASER_500x380/TAMPO_INTEIRO_500x380.dxf` ou o SVG equivalente, em milímetros e escala 1:1. Incluem um perímetro de **500 × 380 mm** e 25 ranhuras passantes. Corte o tampo inteiro na CNC a laser indicada para esta peça, com área útil que comporte o contorno. A estrutura usa as 15 chapas existentes. A medida do tampo supera a antiga área útil de 560 × 360 mm na profundidade; os arquivos do tampo usam página própria de 500 × 380 mm.

A redução retira 10 mm da frente e 10 mm de trás do tampo original, mantendo o centro e a inclinação. Todas as peças do pedestal, incluindo GX e GY, são compatíveis com as anteriores; não é necessário recortá-las. As coordenadas s dos furos diminuem 10 mm. A grelha fica a 18 mm das bordas laterais e 8 mm das bordas dianteira/traseira.

Os vetores representam a peça acabada, **sem compensação da largura do feixe**. No software da sua CNC a laser, corte os encaixes antes do perímetro e aplique compensação uma vez: interna nos furos, externa no contorno. Ajuste potência, velocidade e passes para o MDF medido e o laser utilizado. Os cantos retangulares são adequados ao processo a laser. Confira primeiro um encaixe em retalho do mesmo MDF, usando `06_TESTE_ENCAIXE`. Não escale o desenho para corrigir espessura. Não é necessário dividir o tampo ou reposicionar a chapa durante o corte.

Os **25 encaixes** incluem dentes nas quatro paredes superiores e nas cinco nervuras da grelha. A inclinação foi considerada na projeção dos furos: um dente vertical atravessa um tampo inclinado e precisa de ranhura mais larga que a espessura nominal. `Coordenadas_dos_encaixes.csv` usa x e s medidos **na chapa**, a partir do canto dianteiro esquerdo, olhando a face superior. Não transferir diretamente as coordenadas horizontais do corpo. Os dentes sobem aproximadamente 3 mm, sem deixar espigas altas sobre o mapa; nivelar com lixa após colagem.

## Montagem

1. Identifique com lápis todas as peças conforme o mapa de chapas. F = frente baixa, T = traseira, E/D = laterais. As faixas 1…4 sobem da base ao topo. Antes da cola, confira o encaixe a seco com o MDF real.
2. Cole B1+B2+B3 em superfície plana. B1 é inferior, B2 intermediária, B3 superior com 12 ranhuras. Alinhe as bordas; não deixe cola obstruir as ranhuras. A base deve apoiar **toda a face inferior no chão**, sem pés altos ou pequenos.
3. Una as quatro faixas de cada parede em plano. Cole RF1…RF3 / RT1…RT3 / RE1…RE3 / RD1…RD3 na face interna das respectivas emendas. Tiras de 30 mm centralizadas na linha nominal da emenda; ficam 30 mm afastadas das extremidades.
4. Cole A1F/T/E/D abaixo de H1 e A2F/T/E/D abaixo de H2. H1 e H2 têm face superior a 320 e 620 mm acima da base superior. Portanto, a **borda superior de cada apoio A** fica a 317 / 617 mm (para MDF 3 mm). Apoios com 20 mm de altura: borda inferior a 297 / 597 mm. Cole as faces internas das paredes contra as faces largas dos apoios; a divisória pousa na borda superior de 3 mm de cada apoio. Estas divisórias travam o corpo e reduzem o vão livre das paredes.
5. Monte paredes e base B3 juntas, mantendo cantos soltos até inserir os dentes inferiores. Os dentes entram somente nos 3 mm de B3; B1/B2 ficam inteiros. Insira H1 e H2 **antes de fechar a última parede** e cole suas quatro bordas. Confira diagonais e esquadro.
6. **Antes de fechar H1**, coloque e imobilize o lastro no compartimento inferior, diretamente sobre B3, centralizado e distribuído. Não ponha peso nas divisórias H ou no tampo. Consulte o dimensionamento abaixo. Para uso fixado ao piso, instalar a fixação mecânica adequada antes de fechar o compartimento.
7. Encaixe a grelha: GX1/GX2/GX3 são as travessas em s=90/190/290 mm; GY1/GY2 as longarinas em x=125/375 mm do tampo. Nas interseções entre nervuras, GX tem ranhuras superiores e GY inferiores. Na passagem pelas paredes, todas as nervuras têm ranhuras inferiores e as paredes superiores. Faça um encaixe simultâneo a seco; os dentes de cada nervura ficam para cima. Cole as meias-madeiras e os contatos com as paredes. Os encaixes apenas posicionam, precisam de cola.
8. Passe cola nas bordas superiores das paredes e de todas as nervuras; assente o tampo com os 25 dentes alinhados às respectivas ranhuras. Mantenha pressão distribuída durante a cura conforme a cola. A grelha se estende até 18 mm das bordas laterais e 8 mm da frente/traseira do tampo, sustentando as partes em balanço.
9. As faces horizontais da frente/traseira encontram uma chapa inclinada: pode haver até {S*T:.2f} mm de diferença ao longo da espessura. Ajuste a borda por lixa ao ângulo de {ANGLE:.2f}° ou preencha a diferença com adesivo apropriado, sem levantar o tampo. Lixe pontas dos dentes até ficarem rentes ao tampo. Só depois da cura, cole o mapa.

## Estabilidade da base reduzida

A base 440 × 340 economiza 40% da área da antiga 500 × 500. A estrutura possui paredes formando uma caixa fechada, 12 reforços de emenda, duas divisórias horizontais, base laminada e grelha superior de cinco nervuras de 70 mm. Isso organiza um caminho de apoio para o tampo fino; o lastro resolve a estabilidade ao tombamento de um pedestal alto.

Dimensionamento estático adotado para orientar o lastro: força horizontal **20 N** (aproximadamente 2 kgf), aplicada a **0,93 m** de altura; fator 1,5 sobre o momento; centro de massa centrado; chão plano. O caso crítico usa metade da profundidade da base, 0,17 m:

`massa total mínima = 1,5 × 20 × 0,93 / (9,81 × 0,17) = {required:.2f} kg`.

Adote **pelo menos 17 kg de massa total do conjunto** (pedestal + tampo + mapa + lastro), com lastro imobilizado na parte inferior. O MDF foi estimado em {mass:.2f} kg usando densidade 700 kg/m³; a densidade real e a massa do mapa variam. **Pese o conjunto** e complete com lastro até 17 kg. Exemplo: se pedestal+tampo+mapa pesarem 5 kg, usar no mínimo 12 kg de lastro. O compartimento inferior tem aproximadamente 334 × 294 × 317 mm; distribua o peso dentro do corpo, sobre a base apoiada no chão.

Sem lastro ou fixação ao piso, essa base reduzida não atende ao caso estático assumido. O cálculo não é ensaio de carga, não estabelece carga máxima no tampo e não cobre uma pessoa apoiando o peso do corpo. Para interação pública que possa incluir esse apoio, use fixação mecânica ao piso e dimensione a estrutura para as cargas reais. O protótipo de MDF de 3 mm ainda exige avaliação física das colagens e da flexão para o mapa utilizado. Não há certificação estrutural nesta entrega.

## Visualizar e regenerar

Abra `04_MODELOS_3D/Pedestal_MDF.scad` no OpenSCAD. Modo inicial `montado`; para ver as divisórias, desmarque `mostrar_paredes` e `mostrar_tampo`. Modos `explodido`, `peca2d`, `peca3d`, `chapa2d`, `chapas`. Peças 1…47 (a 47ª é o tampo); chapas 1…15. Em modo explodido o tampo é levantado 100 mm. O SCAD contém a montagem exata com todos os reforços; não apenas as peças planas.

Dependências em `07_FONTE/requirements.txt`. Gerar os cortes e o modelo: `python 07_FONTE/gerar_pedestal.py --espessura 3 --folga 0.15`. Gerar as vistas de montagem: `python 07_FONTE/gerar_vistas.py`. Gerar os 47 STL individuais: `python 07_FONTE/exportar_stl.py` (requer OpenSCAD). Os STL são peças planas para visualização; a montagem completa está no SCAD. Espessura altera os encaixes, não a escala geral. Regere em pasta vazia ao mudar os parâmetros. `DIMENSIONAMENTO.json` registra as medidas e as verificações de geração: contornos válidos, inventário, faixas reconstruídas, limites úteis e distâncias entre peças. Não registra ensaios físicos.

Fontes para propriedades de painéis e união por cola: [USDA Wood Handbook](https://research.fs.usda.gov/download/treesearch/37440.pdf). Propriedades do MDF dependem do produto; a estimativa de massa e a equação de tombamento acima são hipóteses deste projeto, sem adoção de resistência tabelada como capacidade de carga.
'''
    (root/'LEIA_PRIMEIRO.md').write_text(manual,encoding='utf-8')
    (root/'07_FONTE'/'requirements.txt').write_text('shapely>=1.8\nnumpy>=1.21\nmatplotlib>=3.5\n',encoding='utf-8')
    source=Path(__file__).resolve()
    target=root/'07_FONTE'/'gerar_pedestal.py'
    if source!=target.resolve():
        shutil.copy2(source,target)
    print(json.dumps(report,indent=2,ensure_ascii=False))


if __name__=='__main__':
    main()
