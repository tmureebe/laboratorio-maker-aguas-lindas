#!/usr/bin/env python3
"""Caixa adicional; conserva as 47 peças do pedestal v2. Medidas em mm.

Geometria/cortes: biblioteca padrão. Guias: numpy e matplotlib.
Executar desta pasta ou de qualquer diretório: python3 gerar_caixa.py.
"""
from pathlib import Path
import csv
import hashlib
import json
import math
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT.parent
OLD = WORK / 'pedestal_pecas_v2/Pedestal_MDF_LASER_600x400'
T = 3.0
W = 500.0
D = 380.0
H = 50.0
WALL = H - 2*T
RIB = 30.0
GAP = WALL - RIB
C = .15
SCREWS = [(x,y) for y in (13.,D-13.) for x in (30.,150.,400.,470.)]
RIB_Y = (110.,240.)
ZONES = [
    dict(nome='ESP32 + protoboard: reserva', caixa=[30,255,6,200,95,32]),
    dict(nome='DFPlayer: reserva', caixa=[275,255,6,100,95,32]),
    dict(nome='Alto-falante: reserva', caixa=[294,3,6,72,35,38]),
]


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
           '<desc>Contornos pretos de 0,35 mm para visualização. Cortar pelos eixos vetoriais, sem converter o traço em contorno. Painéis lisos contêm apenas um retângulo fechado.</desc>',
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


def main():
    for folder in ['01_CORTE_PAINEIS','02_CHAPA_600x400','03_PECAS','04_MODELO_3D','05_GUIA']:
        (ROOT/folder).mkdir(exist_ok=True)
    parts=[]
    def add(ident,poly,holes,matrix,lid=False):
        part=dict(id=ident,contorno=poly,furos=holes,matriz=matrix,solidario_tampa=lid)
        parts.append(part)
        return part
    def flat(z):
        return [[1,0,0,0],[0,1,0,0],[0,0,1,z],[0,0,0,1]]
    def across(y,z,x=0):
        return [[1,0,0,x],[0,0,1,y],[0,1,0,z],[0,0,0,1]]
    def along(x,z,y=0):
        return [[0,0,1,x],[1,0,0,y],[0,1,0,z],[0,0,0,1]]

    base=add('C0_BASE',rect(0,0,W,D),[],flat(0))
    top=add('C1_TAMPO_LISO',rect(0,0,W,D),[],flat(H-T),True)
    add('C2_FRENTE',rect(0,0,W-2*T,WALL),
        [rect(303+6*i,11,2,22) for i in range(9)]
        + [circle(x-T,32,1.75) for x,y in SCREWS if y==13],across(0,T,T))
    # Entalhe aberto no bordo superior: o conector USB passa com a tampa aberta.
    rear=[[0,0],[494,0],[494,44],[81,44],[81,30],[57,30],[57,44],[0,44]]
    add('C3_TRAS_USB',rear,
        [circle(x-T,32,1.75) for x,y in SCREWS if y==D-13]
        + [rect(x-T,15,3,8) for x in (100,112)],across(D-T,T,T))
    add('C4_ESQUERDA',rect(0,0,D,WALL),[],along(0,T))
    add('C5_DIREITA',rect(0,0,D,WALL),[],along(W-T,T))

    # Ranhuras de meia-madeira; folga lateral total 0,15 mm.
    length=494.
    cx=250-T
    a,b=cx-(T+C)/2,cx+(T+C)/2
    nx=[[0,0],[length,0],[length,30],[b,30],[b,15-C/2],
        [a,15-C/2],[a,30],[0,30]]
    for i,y in enumerate(RIB_Y,6):
        add(f'C{i}_NX{i-5}',nx,[],across(y-T/2,T+GAP,T),True)
    a1,b1=RIB_Y[0]-T-(T+C)/2,RIB_Y[0]-T+(T+C)/2
    a2,b2=RIB_Y[1]-T-(T+C)/2,RIB_Y[1]-T+(T+C)/2
    ny=[[0,0],[a1,0],[a1,15+C/2],[b1,15+C/2],[b1,0],
        [a2,0],[a2,15+C/2],[b2,15+C/2],[b2,0],
        [D-2*T,0],[D-2*T,30],[0,30]]
    add('C8_NY',ny,[],along(250-T/2,T+GAP,T),True)

    placements=[(p,20.,20.+sum((44 if k<4 else 30)+8 for k in range(i)))
                for i,p in enumerate(parts[2:])]
    for part in parts:
        w=max(x for x,y in part['contorno'])
        h=max(y for x,y in part['contorno'])
        cut_svg(ROOT/'03_PECAS'/f'{part["id"]}.svg',[(part,0,0)],w,h)
        cut_dxf(ROOT/'03_PECAS'/f'{part["id"]}.dxf',[(part,0,0)])
    for part in (base,top):
        cut_svg(ROOT/'01_CORTE_PAINEIS'/f'{part["id"]}_500x380.svg',[(part,0,0)],W,D)
        cut_dxf(ROOT/'01_CORTE_PAINEIS'/f'{part["id"]}_500x380.dxf',[(part,0,0)])
    cut_svg(ROOT/'02_CHAPA_600x400/PAREDES_E_REFORCOS.svg',placements,600,400)
    cut_dxf(ROOT/'02_CHAPA_600x400/PAREDES_E_REFORCOS.dxf',placements)
    with (ROOT/'05_GUIA/Lista_de_pecas.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f,delimiter=';')
        wr.writerow(['identificacao','quantidade','largura_mm','altura_mm','espessura_mm','origem'])
        for p in parts:
            wr.writerow([p['id'],1,max(x for x,y in p['contorno']),
                         max(y for x,y in p['contorno']),T,
                         'Painel separado 500x380' if p in (base,top) else 'Chapa adicional 600x400'])
        wr.writerow(['TACO_MADEIRA',8,20,20,44,'Madeira maciça; corte fora do laser'])
    with (ROOT/'05_GUIA/Coordenadas_montagem.csv').open('w',encoding='utf-8-sig',newline='') as f:
        wr=csv.writer(f,delimiter=';')
        wr.writerow(['item','x_mm','s_mm','observacao'])
        for i,(x,y) in enumerate(SCREWS,1):
            wr.writerow([f'Centro do taco {i}',x,y,'Parafuso horizontal na parede frontal/traseira; eixo z=35; taco colado apenas na tampa'])
        wr.writerow(['Tampo antigo: canto dianteiro esquerdo',0,0,'500x380; lixar dentes rentes antes da colagem'])
        wr.writerow(['Tampo antigo: canto traseiro direito',500,380,'Sem recorte ou furação'])
        wr.writerow(['Nervura NX1',3,RIB_Y[0],'Eixo; comprimento 494; solidária à tampa'])
        wr.writerow(['Nervura NX2',3,RIB_Y[1],'Eixo; comprimento 494; solidária à tampa'])
        wr.writerow(['Nervura NY',250,3,'Eixo; comprimento 374; solidária à tampa'])

    # Copia geométrica de referência, sem modificar os originais.
    oldsource=(OLD/'04_MODELOS_3D/Pedestal_MDF.scad').read_text()
    old={}
    for line in oldsource.splitlines():
        for key in ['esp','nomes','contornos','matrizes','tipos']:
            if line.startswith(key+'='):
                old[key]=json.loads(line[len(key)+1:-1])
    oldmat=old['matrizes'][old['nomes'].index('TAMPO')]
    # Mesma projeção do tampo existente; fundo apoiado na face superior antiga.
    origin=[[float(v) for v in row] for row in oldmat]
    for i in range(3):
        origin[i][3]=oldmat[i][3]+T*oldmat[i][2]
    ref=['// Geometria original preservada; extraída sem alterar os cortes.',
         'module pedestal_existente(){']
    for key in ['esp','nomes','contornos','matrizes','tipos']:
        ref.append(key+'='+json.dumps(old[key],separators=(',',':'))+';')
    ref += ['for(i=[0:len(nomes)-1]) if(mostrar_paredes || !(tipos[i]=="F" || tipos[i]=="T" || tipos[i]=="E" || tipos[i]=="D"))',
            'color(tipos[i]=="G"?[.67,.43,.56]:nomes[i]=="TAMPO"?[.64,.51,.33]:[.70,.59,.43])',
            'multmatrix(matrizes[i]) linear_extrude(esp) difference(){',
            'polygon(contornos[i][0]);',
            'if(len(contornos[i])>1) for(j=[1:len(contornos[i])-1]) polygon(contornos[i][j]);','}','}']
    (ROOT/'04_MODELO_3D/pedestal_existente.scad').write_text('\n'.join(ref))
    scad=['/* Caixa adicional 500x380x50. Cortes em 01/02/03; unidades mm.',
          'Tampo liso; sem botões. Volumes coloridos são reservas, não componentes medidos. */',
          'modo="conjunto"; // [conjunto,caixa,explodido,peca2d,peca3d]',
          'numero_peca=1; // [1:9]',
          'mostrar_paredes=true;', 'mostrar_tampa=true;', 'mostrar_reservas=false;',
          'abertura=100;', 'include <pedestal_existente.scad>',
          'nomes_caixa='+json.dumps([p['id'] for p in parts])+';',
          'origem_caixa='+json.dumps(origin)+';',
          'module perfil_caixa(i){']
    for i,p in enumerate(parts):
        scad.append(f'if(i=={i}) '+shape_scad(p))
    scad += ['}', 'module caixa(explodida=false){']
    for i,p in enumerate(parts):
        matrix=json.dumps(p['matriz'])
        offset='abertura' if p['solidario_tampa'] else '0'
        col='[.88,.75,.48]' if p['solidario_tampa'] else '[.50,.68,.72]'
        show='if(mostrar_tampa)' if p['solidario_tampa'] else ''
        scad.append(f'{show} color({col}) translate([0,0,explodida?{offset}:0]) multmatrix({matrix}) linear_extrude(3) perfil_caixa({i});')
    for x,y in SCREWS:
        scad.append(f'if(mostrar_tampa) color([.65,.45,.26]) translate([{x-10},{y-10},3+(explodida?abertura:0)]) cube([20,20,44]);')
    for zone in ZONES:
        x,y,z,w,d,h=zone['caixa']
        scad.append(f'if(mostrar_reservas) color([.2,.65,.3,.45]) translate([{x},{y},{z}]) cube([{w},{d},{h}]);')
    scad += ['}',
             'if(modo=="conjunto") {pedestal_existente(); multmatrix(origem_caixa) caixa();}',
             'else if(modo=="caixa") caixa();',
             'else if(modo=="explodido") {pedestal_existente(); multmatrix(origem_caixa) caixa(true);}',
             'else if(modo=="peca2d") perfil_caixa(numero_peca-1);',
             'else if(modo=="peca3d") linear_extrude(3) perfil_caixa(numero_peca-1);',
             'else assert(false,"Modo invalido");']
    (ROOT/'04_MODELO_3D/Pedestal_com_caixa.scad').write_text('\n'.join(scad),encoding='utf-8')
    data=dict(unidade='mm',espessura_mdf=T,dimensoes_externas=[W,D,H],altura_interna=WALL,
              vao_sob_nervuras=GAP,folga_meia_madeira_total=C,
              parafusos=SCREWS,eixo_parafusos_z=35,nervuras_s=list(RIB_Y),
              fixacao='8 parafusos horizontais pelas paredes frontal/traseira; painéis sem furos',
              reservas_nao_medidas=ZONES,pecas=parts,
              posicionamento_chapa=[dict(id=p['id'],x=x,y=y) for p,x,y in placements],
              matriz_caixa_no_pedestal=origin,
              fontes_locais=['guia_projeto_18_mapa_tatil.pdf (páginas 5, 9, 19)',
                             'pedestal_pecas_v2/Pedestal_MDF_LASER_600x400',
                             'mapa_tatil_alto-relevo/entrega_A1/LEIA_PRIMEIRO.md'])
    (ROOT/'06_FONTE/parametros_e_geometria.json').write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding='utf-8')
    manifest={str(p.relative_to(WORK)):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(OLD.rglob('*')) if p.is_file() and '__pycache__' not in str(p)}
    manifest['caixa_120x200x80_com_tampa.scad']=hashlib.sha256((WORK/'caixa_120x200x80_com_tampa.scad').read_bytes()).hexdigest()
    (ROOT/'05_GUIA/ORIGINAIS_PRESERVADOS_SHA256.json').write_text(json.dumps(manifest,indent=2))
    verify(data)
    from gerar_guias import generate
    generate(ROOT,data)
    print('Gerados: 9 peças MDF, 1 chapa 600x400, 2 painéis 500x380 sem furos, modelo e guias.')


def verify(data):
    """Confere arquivos exportados e condições da interface com o pedestal."""
    report={}
    # Bounding boxes da chapa, lidos dos parâmetros usados na exportação.
    boxes=[]
    for p,pos in zip(data['pecas'][2:],data['posicionamento_chapa']):
        xs,ys=zip(*p['contorno']); x,y=pos['x'],pos['y']
        bounds=(min(xs)+x,min(ys)+y,max(xs)+x,max(ys)+y)
        assert bounds[0]>=20 and bounds[1]>=20 and bounds[2]<=580 and bounds[3]<=380
        boxes.append(bounds)
    gaps=[max(b[0]-a[2],a[0]-b[2],b[1]-a[3],a[1]-b[3])
          for i,a in enumerate(boxes) for b in boxes[i+1:]]
    assert min(gaps)>=8-1e-9
    report['chapa_area_util_mm']=[560,360]
    report['intervalo_minimo_pecas_mm']=min(gaps)
    report['encaixe_sob_nervuras_mm']=GAP
    assert not data['pecas'][0]['furos'] and not data['pecas'][1]['furos']
    assert data['dimensoes_externas']==[500,380,50]
    assert all(max(y for x,y in p['contorno'])==380 for p in data['pecas'][:2])
    report['furos_tampo_superior']=0
    report['furos_painel_inferior']=0
    report['paineis_mm']=[[W,D],[W,D]]
    report['parafusos_acessiveis_pelas_paredes_frente_tras']=len(SCREWS)
    report['tampo_antigo_intervalo_s_mm']=[0,D]
    # Read-back: dimensões físicas SVG e unidades/fechamento DXF.
    exports=[]
    for p in data['pecas']:
        dx=ROOT/'03_PECAS'/f'{p["id"]}.dxf'
        sv=ROOT/'03_PECAS'/f'{p["id"]}.svg'
        xml=ET.parse(sv).getroot()
        xs,ys=zip(*p['contorno'])
        assert xml.attrib['width']==f'{max(xs):g}mm'
        assert xml.attrib['height']==f'{max(ys):g}mm'
        for elem in xml.iter('{http://www.w3.org/2000/svg}path'):
            assert elem.attrib['d'].endswith(' Z')
        lines=dx.read_text().splitlines()
        pairs=list(zip(lines[::2],lines[1::2]))
        assert pairs[pairs.index(('9','$INSUNITS'))+1]==('70','4')
        entities=[]
        for code,val in pairs:
            if code=='0':
                if val in ('LWPOLYLINE','CIRCLE'): entities.append([(code,val)])
                else: entities.append([])
            elif entities and entities[-1]: entities[-1].append((code,val))
        ents=[e for e in entities if e]
        assert len(ents)==1+len(p['furos'])
        for e in ents:
            if e[0][1]=='LWPOLYLINE':
                assert ('70','1') in e
                count=int(next(v for k,v in e if k=='90'))
                assert sum(k=='10' for k,v in e)==count
        exports.append(dict(id=p['id'],contornos=len(ents),unidade='mm',fechados=True))
    report['cortes_relidos']=exports
    # Reservas e tacos: volumes medidos devem ficar abaixo das nervuras.
    fixed=[]
    for zone in ZONES:
        x,y,z,w,d,h=zone['caixa']
        assert 3<=x and 3<=y and x+w<=W-3 and y+d<=D-3 and z>=3 and z+h<=47
        assert x+w<=248.5 or x>=251.5 or z+h<=17
        assert all(y+d<=s-1.5 or y>=s+1.5 or z+h<=17 for s in RIB_Y)
        for sx,sy in SCREWS:
            assert x+w<=sx-10 or x>=sx+10 or y+d<=sy-10 or y>=sy+10
        fixed.append(zone['nome'])
    report['reservas_sem_interferencia_com_tacos_e_nervuras']=fixed
    report['altura_face_superior_mm']={
        name:round(sum(data['matriz_caixa_no_pedestal'][2][k]*v for k,v in enumerate([250,y,H,1])),2)
        for name,y in [('frente',0),('centro',D/2),('tras',D)]}
    report['limites']='Verificação dimensional e read-back dos vetores; não é ensaio de resistência, acústica ou encaixe físico. Reservas de componentes precisam de medição.'
    (ROOT/'05_GUIA/VERIFICACAO.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')


if __name__=='__main__':
    main()
