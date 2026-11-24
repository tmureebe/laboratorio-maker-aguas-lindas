"""Exportadores de contornos fechados em mm, compartilhados pela revisão integrada."""
import json


def rect(x,y,w,h):
    return [[x,y],[x+w,y],[x+w,y+h],[x,y+h]]


def circle(x,y,r):
    return dict(centro=[x,y], raio=r)


def rings(part):
    return [part['contorno']] + part['furos']


def cut_svg(path, objects, w, h):
    # Aparência explícita em cada entidade: leitores CAM simples nem sempre
    # herdam a aparência do grupo. O traço é visual; os eixos de corte não mudam.
    appearance = 'fill="none" stroke="#000000" stroke-width="0.35" stroke-linejoin="round"'
    out = ['<?xml version="1.0" encoding="UTF-8"?>',
           f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{w:g}mm" height="{h:g}mm" viewBox="0 0 {w:g} {h:g}" overflow="visible">',
           '<title>Corte em mm, escala 1:1; sem compensação de feixe</title>',
           '<desc>Contornos pretos de 0,35 mm para visualização. Cortar pelos eixos vetoriais, sem converter o traço em contorno. Contornos internos são cortes passantes; marcações são fornecidas em PDF separado.</desc>',
           '<g id="CORTE">']
    for part,dx,dy in objects:
        for i,ring in enumerate(rings(part)):
            if isinstance(ring,dict):
                x,y = ring['centro']
                out.append(f'<circle id="{part["id"]}_{i}" cx="{x+dx:.6f}" cy="{h-y-dy:.6f}" r="{ring["raio"]:.6f}" {appearance}/>')
            else:
                d = 'M ' + ' L '.join(f'{x+dx:.6f},{h-y-dy:.6f}' for x,y in ring) + ' Z'
                out.append(f'<path id="{part["id"]}_{i}" d="{d}" {appearance}/>')
    path.write_text('\n'.join(out+['</g>','</svg>']),encoding='utf-8')


def cut_dxf(path, objects):
    out=[]
    def put(*v):
        out.extend(map(str,v))
    bounds=[]
    for part,dx,dy in objects:
        bounds.extend((x+dx,y+dy) for x,y in part['contorno'])
    xs,ys=zip(*bounds)
    put(0,'SECTION',2,'HEADER',9,'$ACADVER',1,'AC1015',9,'$INSUNITS',70,4,
        9,'$MEASUREMENT',70,1,9,'$LWDISPLAY',290,1,
        9,'$EXTMIN',10,min(xs),20,min(ys),30,0,
        9,'$EXTMAX',10,max(xs),20,max(ys),30,0,
        9,'$LIMMIN',10,min(xs),20,min(ys),
        9,'$LIMMAX',10,max(xs),20,max(ys),0,'ENDSEC',
        0,'SECTION',2,'TABLES',0,'TABLE',2,'LTYPE',70,1,
        0,'LTYPE',100,'AcDbSymbolTableRecord',100,'AcDbLinetypeTableRecord',
        2,'CONTINUOUS',70,0,3,'Solid line',72,65,73,0,40,0,0,'ENDTAB',
        0,'TABLE',2,'LAYER',70,2)
    for layer in ('0','CORTE'):
        put(0,'LAYER',100,'AcDbSymbolTableRecord',100,'AcDbLayerTableRecord',
            2,layer,70,0,62,7,6,'CONTINUOUS',370,35)
    # A seção BLOCKS, mesmo vazia, é necessária para leitores como o importador
    # DXF do Inkscape reconhecerem onde começa a geometria.
    put(0,'ENDTAB',0,'ENDSEC',0,'SECTION',2,'BLOCKS',0,'ENDSEC',
        0,'SECTION',2,'ENTITIES')
    for part,dx,dy in objects:
        for ring in rings(part):
            put(0,'CIRCLE' if isinstance(ring,dict) else 'LWPOLYLINE',
                100,'AcDbEntity',8,'CORTE',62,7,370,-1)
            if isinstance(ring,dict):
                x,y=ring['centro']
                put(100,'AcDbCircle',10,f'{x+dx:.6f}',20,f'{y+dy:.6f}',30,0,40,f'{ring["raio"]:.6f}')
            else:
                put(100,'AcDbPolyline',90,len(ring),70,1)
                for x,y in ring:
                    put(10,f'{x+dx:.6f}',20,f'{y+dy:.6f}')
    put(0,'ENDSEC',0,'EOF')
    path.write_text('\n'.join(out)+'\n',encoding='ascii')


def shape_scad(part):
    out=['difference() {',f'polygon({json.dumps(part["contorno"])});']
    for hole in part['furos']:
        if isinstance(hole,dict):
            out.append(f'translate({json.dumps(hole["centro"])}) circle(r={hole["raio"]},$fn=64);')
        else:
            out.append(f'polygon({json.dumps(hole)});')
    return '\n'.join(out+['}'])
