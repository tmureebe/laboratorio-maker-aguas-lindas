#!/usr/bin/env python3
"""Gera a caixa integrada ao mapa, cortes, modelos, guia e verificações.

As posições/alturas são avaliadas pelo OpenSCAD no SCAD original do mapa.
A tampa é conferida contra uma seção real do painel desse mesmo SCAD.
"""
from pathlib import Path
from collections import Counter
import ast
import csv
import hashlib
import json
import os
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
os.environ.setdefault('MPLCONFIGDIR','/tmp/mpl-integracao-caixa')
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, Polygon
from matplotlib.backends.backend_pdf import PdfPages
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from gerar_tacos_3d import exportar_tacos
from formatos_corte import rect, circle, cut_svg, cut_dxf, shape_scad
from ler_cortes import svg_entities, dxf_entities

ROOT=Path(__file__).resolve().parents[1]
PROJECT=ROOT.parent
MAP=PROJECT/'relevo-500x380/construcoes_vista_aerea.scad'
MODELS=ROOT/'04_MODELO_3D'
GUIDE=ROOT/'05_GUIA'
SCREWS=[(x,y) for y,xs in [(13,[30,150,400,470]),(367,[30,150,270,470])] for x in xs]
CHANNELS={6:[(77,237),(307,367)],7:[(87,222),(277,447)],8:[(27,92),(122,217),(262,352)]}
# Envelopes conservadores dos sólidos da cena, em coordenadas da caixa.
ELECTRONICS=[
 dict(nome='Protoboard',min=[285,270,6],max=[455,340,15.3]),
 dict(nome='ESP32, pinos e USB',min=[320,286,15],max=[348,345.2,29.2]),
 dict(nome='DFPlayer, suportes e microSD',min=[420,160,3],max=[445,194,17.6]),
 dict(nome='Resistor 1k',min=[376,284.5,17.5],max=[392,287.5,20.5]),
 dict(nome='Falante',min=[314,4,9],max=[346,16,41]),
]
SERVICE=[dict(nome='Area livre protoboard/conectores',min=[280,265,3],max=[460,357,40]),
         dict(nome='Acesso microSD',min=[415,155,3],max=[450,205,24])]


def run_scad(source,output,defines=()):
    cmd=['openscad','-o',str(output)]
    for define in defines:cmd+=['-D',define]
    result=subprocess.run(cmd+[str(source)],capture_output=True,text=True)
    log=(result.stdout+result.stderr).replace('WARNING: Viewall and autocenter disabled in favor of $vp*\n','')
    if result.returncode or 'WARNING:' in log or 'ERROR:' in log:
        raise RuntimeError(' '.join(cmd)+'\n'+log)
    return log


def read_map(tmp):
    source=tmp/'dados.scad'
    source.write_text(f'include <{MAP.as_posix()}>\nmodo="peca";tipo_peca="painel";\n'
        'for(r=referencias) echo("BOTAO",[r[0],r[1],[for(v=xy_mm(r[3]))round(v*1000)],round(h_botao(r)*1000)]);\n'
        'echo("PARAMETROS",[painel_largura_mm,painel_profundidade_mm,espessura_painel_mm,diametro_furo_fio_painel_mm,passo_terminais_x_mm,passo_terminais_y_mm]);\n')
    out=tmp/'dados.echo';run_scad(source,out)
    raw=out.read_text()
    assert 'WARNING:' not in raw and 'ERROR:' not in raw,raw
    buttons=[];params=None
    for line in raw.splitlines():
        if line.startswith('ECHO: "BOTAO", '):
            n,name,xy,z=ast.literal_eval(line.split(', ',1)[1])
            buttons.append(dict(numero=n,nome=name,x_mm=xy[0]/1000,y_mm=xy[1]/1000,z_base_sobre_tampa_mm=z/1000))
        if line.startswith('ECHO: "PARAMETROS", '):params=ast.literal_eval(line.split(', ',1)[1])
    assert len(buttons)==18 and params[:3]==[500,380,3]
    return buttons,params


def make_parts(buttons,params):
    parts=[]
    def add(name,poly,holes,matrix,lid=False):
        parts.append(dict(id=name,contorno=poly,furos=holes,matriz=matrix,solidario_tampa=lid))
    flat=lambda z:[[1,0,0,0],[0,1,0,0],[0,0,1,z],[0,0,0,1]]
    across=lambda y,z:[[1,0,0,3],[0,0,1,y],[0,1,0,z],[0,0,0,1]]
    along=lambda x,z:[[0,0,1,x],[1,0,0,3],[0,1,0,z],[0,0,0,1]]
    _,_,_,diam,pitch_x,pitch_y=params
    holes=[]
    for b in buttons:
        x,y=b['x_mm'],b['y_mm']
        for sx in (-1,1):
            for sy in (-1,1):
                holes.append(circle(round(x+sx*pitch_x/2,6),round(y+sy*pitch_y/2,6),diam/2))
    add('C0_BASE',rect(0,0,500,380),[],flat(0))
    add('C1_TAMPO_FURADO',rect(0,0,500,380),holes,flat(47),True)
    add('C2_FRENTE',rect(0,0,494,44),[rect(303+6*i,11,2,22) for i in range(9)]+[circle(x-3,32,1.75) for x,y in SCREWS if y==13],across(0,3))
    # USB em x=334, coincidente com o conector do ESP32 deslocado para a direita.
    rear=[[0,0],[494,0],[494,44],[343,44],[343,30],[319,30],[319,44],[0,44]]
    add('C3_TRAS_USB',rear,[circle(x-3,32,1.75) for x,y in SCREWS if y==367]+[rect(x-3,15,3,8) for x in (362,374)],across(377,3))
    add('C4_ESQUERDA',rect(0,0,380,44),[],along(0,3))
    add('C5_DIREITA',rect(0,0,380,44),[],along(497,3))
    # Rasgos superiores para meia-madeira; passagens de cabos saem da borda inferior.
    def profile(width,notches):
        pts=[[0,0]]
        for a,b,h in sorted(notches):pts.extend([[a,0],[a,h],[b,h],[b,0]])
        return pts+[[width,0],[width,30],[0,30]]
    # Para NX, uma rotação de 180 graus do percurso superior deixa a ranhura no topo.
    for idx,y in [(6,110),(7,240)]:
        lower=[]
        for a,b in CHANNELS[idx]:lower.extend([[a,0],[a,12],[b,12],[b,0]])
        nx=[[0,0]]+lower+[[494,0],[494,30],[248.575,30],[248.575,14.925],[245.425,14.925],[245.425,30],[0,30]]
        add(f'C{idx}_NX{idx-5}',nx,[],across(y-1.5,17),True)
    notches=[(105.425,108.575,15.075),(235.425,238.575,15.075)]+[(a,b,12) for a,b in CHANNELS[8]]
    add('C8_NY',profile(374,notches),[],along(248.5,17),True)
    return parts


def write_models(parts,buttons):
    origin=[[1,0,0,-30],[0,.9874406319167053,-.15799050110667284,-18.087691567494037],[0,.15799050110667284,.9874406319167053,865.9441266854824],[0,0,0,1]]
    out=['// Geometria compartilhada: corte, inspeção e conjunto usam os mesmos perfis.',
         'use <Taco_impressao_3D.scad>',
         'nomes_caixa='+json.dumps([p['id'] for p in parts])+';',
         'origem_caixa='+json.dumps(origin)+';',
         'botoes_mapa='+json.dumps([[b['numero'],b['x_mm'],b['y_mm'],b['z_base_sobre_tampa_mm']] for b in buttons])+';',
         'tacos_caixa='+json.dumps(SCREWS)+';',
         'module perfil_caixa(i) {']
    for i,p in enumerate(parts):out.append(f'if(i=={i}) '+shape_scad(p))
    out+=['}', 'module caixa_integrada(tampa=true,abertura=0,alpha=1,impressos=false) {']
    for i,p in enumerate(parts):
        show='if(tampa)' if p['solidario_tampa'] else ''
        dz='abertura' if p['solidario_tampa'] else '0'
        out.append(f'{show} color([{.88 if p["solidario_tampa"] else .5},.68,.48,alpha]) translate([0,0,{dz}]) multmatrix({json.dumps(p["matriz"])}) linear_extrude(3) perfil_caixa({i});')
    out+=['if(tampa) for(p=tacos_caixa) color([.65,.45,.26,alpha]) translate([p[0]-10,p[1]-10,3+abertura])',
          'if(impressos) {if(p[1]>190) translate([20,20,0]) rotate([0,0,180]) taco_montagem(); else taco_montagem();} else cube([20,20,44]);','}']
    (MODELS/'Geometria_caixa.scad').write_text('\n'.join(out)+'\n')
    # Chamadas dos tacos impressos usam a geometria local original e sua orientação.
    taco=(MODELS/'Taco_impressao_3D.scad').read_text()
    assert 'module taco' in taco
    scene='''/* Caixa integrada 500 x 380 x 50 mm; 18 KFC-A06 nas posições e alturas do mapa.
Componentes eletrônicos são representações nominais da V4, a conferir na peça real.
Fios ilustram rotas mecânicas; não constituem esquema elétrico nem atribuição de GPIO.
A tampa de CNC está em 01_CORTE_PAINEIS/C1_TAMPO_FURADO_500x380.dxf.
*/
/* [Visualizacao] */
vista="inspecao"; // [inspecao,fechada,aberta,sem_tampa,eletronica]
mostrar_pedestal=false;
mostrar_paredes=true;
mostrar_fios=true;
mostrar_fios_botoes=true;
mostrar_rotulos=true;
mostrar_botoes=true;
mostrar_relevo=true;
tacos_impressos=false;
abertura_tampa=105;
/* [Hidden] */
$fn=24;
use <../../relevo-500x380/botao_tatil_KFC-A06_12x12x4p3.scad>
use <../../relevo-500x380/construcoes_vista_aerea.scad>
include <pedestal_existente.scad>
include <Geometria_caixa.scad>
include <Componentes_eletronicos.scad>
module botao_mapa(b,abertura=0) {
 translate([b[1],b[2],50+b[3]+abertura]) botao_kfc_a06(com_terminais=true);
}
module cabos(abertura=0,botoes=true,fios_botoes=true) {
 // Rotas baixas sob as nervuras; folga de serviço ao abrir a tampa.
 fio([[334,345,25],[334,362,39],[334,394,39]],[.12,.13,.15],1.9);
 fio([[435,333,16],[465,333,9],[465,210,9],[421,164,13]],[.85,.05,.05]);
 fio([[435,337,16],[470,337,8],[470,205,8],[444,164,13]],[.06,.06,.07]);
 fio([[347,326,24],[376,286,19]],[.9,.65,.05]);
 fio([[392,286,19],[460,250,8],[421,167,13]],[.9,.65,.05]);
 fio([[444,170,13],[460,250,9],[347,323,24]],[.15,.62,.78]);
 fio([[444,179,13],[460,150,8],[350,65,8],[336,18,19]],[.70,.15,.65],.7);
 fio([[444,182,13],[465,150,8],[355,65,8],[324,18,19]],[.24,.22,.65],.7);
 if(botoes && fios_botoes) for(i=[0:len(botoes_mapa)-1]) {
  b=botoes_mapa[i]; z=50+b[3]-3.5+abertura;
  // Cada fio sobe pelo furo de MDF alinhado ao seu terminal.
  fio([[367+i*3,294,17.5],[367+i*3,250,8],[b[1]-6.25,250,8],
       [b[1]-6.25,b[2]-2.5,8],[b[1]-6.25,b[2]-2.5,z]],[.95,.52,.08],.7);
  fio([[430,337,16],[475,250,7],[b[1]+6.25,250,7],
       [b[1]+6.25,b[2]-2.5,7],[b[1]+6.25,b[2]-2.5,z]],[.09,.09,.10],.7);
 }
}
module cena_integrada(v="inspecao",relevo=true,abertura=105,botoes=true,fios=true,fios_botoes=true,impressos=false,rotulos=true) {
 $mostrar_rotulos=rotulos;
 dz=v=="aberta"?abertura:0;
 assert(v=="inspecao"||v=="fechada"||v=="aberta"||v=="sem_tampa"||v=="eletronica");
 if(v!="eletronica") caixa_integrada(tampa=v!="sem_tampa",abertura=dz,alpha=v=="inspecao"?.25:1,impressos=impressos);
 eletronica();
 if(relevo && v!="sem_tampa" && v!="eletronica") translate([0,0,50+dz]) {
  // Peças de relevo; o painel real é exclusivamente C1, evitando duplicação.
  relevos_tateis();
 }
 if(botoes) for(b=botoes_mapa) botao_mapa(b,dz);
 if(fios) cabos(dz,botoes,fios_botoes);
}
$vpt=mostrar_pedestal?[220,170,740]:[250,190,40];
$vpr=[42,0,25];$vpd=mostrar_pedestal?1600:880;
if(mostrar_pedestal) {pedestal_existente();multmatrix(origem_caixa) cena_integrada(vista,mostrar_relevo,abertura_tampa,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);}
else cena_integrada(vista,mostrar_relevo,abertura_tampa,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);
'''
    (MODELS/'Caixa_com_sistema_eletronico.scad').write_text(scene)
    pedestal='''/* Conjunto integrado; a eletrônica e os 18 botões usam a cena compartilhada. */
modo="conjunto"; // [conjunto,caixa,explodido,peca2d,peca3d]
numero_peca=1; // [1:9]
mostrar_paredes=true;
mostrar_tampa=true;
mostrar_eletronica=true;
mostrar_relevo=true;
mostrar_botoes=true;
mostrar_fios=true;
mostrar_fios_botoes=true;
mostrar_rotulos=false;
tacos_impressos=false;
abertura=105;
/* [Hidden] */
use <Caixa_com_sistema_eletronico.scad>
include <pedestal_existente.scad>
include <Geometria_caixa.scad>
module conjunto_caixa(explodido=false) {
 if(mostrar_eletronica) cena_integrada(!mostrar_tampa?"sem_tampa":explodido?"aberta":"fechada",mostrar_relevo,abertura,mostrar_botoes,mostrar_fios,mostrar_fios_botoes,tacos_impressos,mostrar_rotulos);
 else caixa_integrada(tampa=mostrar_tampa,abertura=explodido?abertura:0,impressos=tacos_impressos);
}
if(modo=="conjunto"||modo=="explodido") {
 pedestal_existente();multmatrix(origem_caixa) conjunto_caixa(modo=="explodido");
} else if(modo=="caixa") conjunto_caixa();
else if(modo=="peca2d") perfil_caixa(numero_peca-1);
else if(modo=="peca3d") linear_extrude(3) perfil_caixa(numero_peca-1);
else assert(false,"Modo inválido");
$vpt=[220,170,730];$vpr=[65,0,25];$vpd=1700;
'''
    (MODELS/'Pedestal_com_caixa.scad').write_text(pedestal)


def export_cuts(parts):
    coupon=dict(id='CUPOM_BOTAO_KFC_A06',contorno=rect(0,0,42,42),furos=[])
    first=parts[1]['furos'][:4]
    center=np.mean([h['centro'] for h in first],axis=0)
    coupon['furos']=[circle(*[round(v,6) for v in np.array(h['centro'])-center+21],h['raio']) for h in first]
    coupon_dir=ROOT/'08_TESTE_ENCAIXE';coupon_dir.mkdir(exist_ok=True)
    cut_svg(coupon_dir/'CUPOM_BOTAO_KFC_A06.svg',[(coupon,0,0)],42,42)
    cut_dxf(coupon_dir/'CUPOM_BOTAO_KFC_A06.dxf',[(coupon,0,0)])
    placements=[(p,20,20+sum((44 if k<4 else 30)+8 for k in range(i))) for i,p in enumerate(parts[2:])]
    for p in parts:
        w=max(x for x,y in p['contorno']);h=max(y for x,y in p['contorno'])
        for folder,suffix in [('03_PECAS','')]+([('01_CORTE_PAINEIS','_500x380')] if p in parts[:2] else []):
            cut_svg(ROOT/folder/(p['id']+suffix+'.svg'),[(p,0,0)],w,h)
            cut_dxf(ROOT/folder/(p['id']+suffix+'.dxf'),[(p,0,0)])
    cut_svg(ROOT/'02_CHAPA_600x400/PAREDES_E_REFORCOS.svg',placements,600,400)
    cut_dxf(ROOT/'02_CHAPA_600x400/PAREDES_E_REFORCOS.dxf',placements)
    with (GUIDE/'Lista_de_pecas.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.writer(f,delimiter=';');wr.writerow(['id','quantidade','largura_mm','altura_mm','espessura_mm','acao'])
        for i,p in enumerate(parts):
            wr.writerow([p['id'],1,max(x for x,y in p['contorno']),max(y for x,y in p['contorno']),3,'REFABRICAR' if i in (1,3,6,7,8) else 'REAPROVEITAR V4'])
        wr.writerow(['TACO_20x20x44',8,20,20,44,'IMPRIMIR modelo com furo cego Ø2,8 × 18 mm para parafuso 3,5 × 12 ou 3,5 × 20 mm'])
    with (GUIDE/'Coordenadas_montagem.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.writer(f,delimiter=';');wr.writerow(['item','x_mm','y_mm','z_mm','observacao'])
        for x,y in SCREWS:wr.writerow(['Taco',x,y,3,'centro em XY; 20x20x44; furo horizontal z35; colar só à tampa'])
        for y in (110,240):wr.writerow(['Nervura NX',3,y,17,'494x30x3; face superior z47'])
        wr.writerow(['Nervura NY',250,3,17,'374x30x3; face superior z47'])
        for e in ELECTRONICS:wr.writerow([e['nome'],*e['min'],'limites max='+str(e['max'])])


def bounds(poly):
    a=np.array(poly);return np.r_[a.min(0),a.max(0)]


def overlap(a,b):
    return bool(np.all(np.minimum(a[3:],b[3:])-np.maximum(a[:3],b[:3])>1e-6))


def check_geometry(parts,buttons,tmp):
    # Corte real no meio da espessura do painel: não usa o gabarito de traços duplos.
    source=tmp/'painel.scad';svg=tmp/'painel_fonte.svg'
    source.write_text(f'use <{MAP.as_posix()}>\nprojection(cut=true) translate([0,0,1.5]) painel_tatil();\n')
    run_scad(source,svg)
    raw=ET.parse(svg).getroot().find('{http://www.w3.org/2000/svg}path').attrib['d']
    contours=[]
    for s in re.findall(r'M\s*(.*?)\s*[zZ]',raw,re.S):
        nums=np.array(list(map(float,re.findall(r'-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?',s))))
        a=nums.reshape(-1,2);a[:,1]*=-1;contours.append(a)
    assert len(parts[1]['furos'])==4*len(buttons)==72
    assert len(contours)==1+len(parts[1]['furos'])==73
    reference=sorted([bounds(c).tolist() for c in contours],key=lambda b:tuple(round(v,2) for v in b))
    actual=[]
    for h in [parts[1]['contorno']]+parts[1]['furos']:
        if isinstance(h,dict):x,y=h['centro'];r=h['raio'];actual.append([x-r,y-r,x+r,y+r])
        else:actual.append(bounds(h).tolist())
    actual.sort(key=lambda b:tuple(round(v,2) for v in b))
    delta=float(np.max(np.abs(np.array(reference)-np.array(actual))))
    assert delta<=.0011,delta
    pairs=0
    for svgfile in sorted(ROOT.glob('0[1238]*/*.svg')):
        a=svg_entities(svgfile.read_text());b=dxf_entities(svgfile.with_suffix('.dxf').read_text())
        assert len(a)==len(b)
        for x,y in zip(a,b):
            assert x['tipo']==y['tipo']
            if x['tipo']=='circulo':assert np.allclose(x['centro'],y['centro'],atol=1e-6) and x['raio']==y['raio']
            else:assert np.allclose(x['pontos'],y['pontos'],atol=1e-6)
        pairs+=1
    # Envelopes de colisão conservadores das peças estruturais e dos módulos reais da cena.
    structure=[('base',[0,0,0,500,380,3]),('tampa',[0,0,47,500,380,50]),
               ('frente',[3,0,3,497,3,47]),('tras',[3,377,3,497,380,47]),
               ('esquerda',[0,0,3,3,380,47]),('direita',[497,0,3,500,380,47]),
               ('NX1',[3,108.5,17,497,111.5,47]),('NX2',[3,238.5,17,497,241.5,47]),
               ('NY',[248.5,3,17,251.5,377,47])]
    structure.extend((f'taco {x},{y}',[x-10,y-10,3,x+10,y+10,47]) for x,y in SCREWS)
    collisions=[]
    for e in ELECTRONICS+SERVICE:
        for name,bb in structure:
            if overlap(np.r_[e['min'],e['max']],np.array(bb)):collisions.append([e['nome'],name])
    assert not collisions,collisions
    for i,e in enumerate(ELECTRONICS):
        for other in ELECTRONICS[i+1:]:
            # Pinos do ESP32 entram na protoboard: contato intencional de montagem.
            if e['nome']=='Protoboard' and other['nome']=='ESP32, pinos e USB':continue
            assert not overlap(np.r_[e['min'],e['max']],np.r_[other['min'],other['max']]),(e,other)
    # As 72 passagens precisam permanecer separadas e livres ate o espaco interno.
    holes=parts[1]['furos']
    for i,h in enumerate(holes):
        for other in holes[i+1:]:
            assert np.linalg.norm(np.array(h['centro'])-other['centro'])>h['raio']+other['raio']
    min_clearance=1e9
    for i,h in enumerate(holes):
        x,y=h['centro'];r=h['raio']
        assert r<x<500-r and r<y<380-r
        hole=np.array([x-r,y-r,3,x+r,y+r,50])
        for name,bb in structure[2:]:assert not overlap(hole,np.array(bb)),(i+1,name)
        for e in ELECTRONICS:assert not overlap(hole,np.r_[e['min'],e['max']]),(i+1,e['nome'])
        min_clearance=min(min_clearance,abs(x-250)-1.5-r,abs(y-110)-1.5-r,abs(y-240)-1.5-r)
    # Abertura USB x322..346, z33..47; cabo r1.9 em x334,z39.
    assert 334-1.9>322 and 334+1.9<346 and 39-1.9>33 and 39+1.9<47
    (GUIDE/'Painel_extraido_do_mapa.svg').write_bytes(svg.read_bytes())
    return dict(botoes=len(buttons),furos_por_botao=4,furos_fios=72,diametro_furos_fios_mm=2*holes[0]['raio'],
        furos_centrais=0,rasgos_terminais=0,contornos_tampa=73,furos_separados=True,
        comparacao_com_secao_real_scad=True,erro_maximo_furacao_mm=round(delta,6),
        resolucao_coordenadas_mm=.001,pares_svg_dxf_conferidos=pairs,
        colisoes_eletronica_estrutura=collisions,areas_servico_livres=True,
        descidas_dos_18_botoes_livres=True,folga_minima_conservadora_passagens_nervuras_mm=round(min_clearance,3),
        usb_alinhado=True,componentes_sao_modelos_nominais=True,contato_pinos_esp32_protoboard_previsto=True)


def draw_profile(ax,p,dx=0,dy=0,color='#d8bd86'):
    ax.add_patch(Polygon(np.array(p['contorno'])+[dx,dy],facecolor=color,edgecolor='#3d4d52',lw=.55))
    for h in p['furos']:
        if isinstance(h,dict):ax.add_patch(Circle(np.array(h['centro'])+[dx,dy],h['raio'],facecolor='white',edgecolor='#3d4d52',lw=.4))
        else:ax.add_patch(Polygon(np.array(h)+[dx,dy],facecolor='white',edgecolor='#3d4d52',lw=.4))


def top_view(ax,parts,buttons,lid=False):
    ax.set_aspect('equal');ax.set_xlim(-15,515);ax.set_ylim(-24,405)
    ax.add_patch(Rectangle((0,0),500,380,fc='#fcf9f0',ec='#253c46',lw=1.4))
    for y in (110,240):ax.add_patch(Rectangle((3,y-1.5),494,3,fc='#c38a55',alpha=.7))
    ax.add_patch(Rectangle((248.5,3),3,374,fc='#c38a55',alpha=.7))
    for x,y in SCREWS:ax.add_patch(Rectangle((x-10,y-10),20,20,fc='#936744',alpha=.8))
    for e in ELECTRONICS:
        x,y,z=e['min'];u,v,w=e['max'];ax.add_patch(Rectangle((x,y),u-x,v-y,fc='#4eac98',ec='#176b63',alpha=.7))
        ax.text((x+u)/2,(y+v)/2,e['nome'].split(',')[0],fontsize=6,ha='center',va='center',rotation=90 if u-x<50 else 0)
    for hole in parts[1]['furos']:
        ax.add_patch(Circle(hole['centro'],hole['raio'],fc='white',ec='#8d3754',lw=.8))
    for b in buttons:
        x,y=b['x_mm'],b['y_mm']
        ax.text(x,y+6,str(b['numero']),ha='center',fontsize=6,color='#8d3754')
    ax.annotate('USB: x = 334',xy=(334,380),xytext=(335,394),fontsize=7,ha='center',arrowprops=dict(arrowstyle='->'))
    ax.text(250,-18,'FRENTE / GRADE DO FALANTE',ha='center',fontsize=8)
    ax.set_xlabel('x (mm)');ax.set_ylabel('y (mm) — origem no canto dianteiro esquerdo')


def box_mesh(lo,hi):
    x,y,z=lo;u,v,w=hi
    verts=np.array([[x,y,z],[u,y,z],[u,v,z],[x,v,z],[x,y,w],[u,y,w],[u,v,w],[x,v,w]])
    return [[verts[i] for i in f] for f in [[0,1,2,3],[4,5,6,7],[0,1,5,4],[1,2,6,5],[2,3,7,6],[3,0,4,7]]]


def previews(parts,buttons):
    fig,ax=plt.subplots(figsize=(11.7,8.3));top_view(ax,parts,buttons)
    ax.set_title('Caixa integrada — 18 botões, 4 furos por botão (72 passagens)',fontsize=14)
    fig.tight_layout();fig.savefig(GUIDE/'Planta_interna.png',dpi=170);plt.close(fig)
    fig,ax=plt.subplots(figsize=(11.7,8.3));
    for i,p in enumerate(parts[2:]):
        dy=20+sum((44 if k<4 else 30)+8 for k in range(i));draw_profile(ax,p,20,dy)
        ax.text(523,dy+12,p['id'],fontsize=7)
    ax.set_aspect('equal');ax.set_xlim(0,600);ax.set_ylim(0,400);ax.set_title('Chapa 600 × 400 mm — paredes e nervuras; C0/C1 separados')
    fig.tight_layout();fig.savefig(GUIDE/'Previa_dos_cortes.png',dpi=160);plt.close(fig)
    # Projeção ortográfica com ordenação global das faces: evita o encobrimento
    # incorreto entre coleções do mplot3d quando a base ocupa todo o painel.
    from matplotlib.collections import PolyCollection
    from matplotlib.colors import to_rgb
    import struct
    triangles=[];colors=[];alphas=[]
    for p in parts:
        if p['id'].startswith('C1_'):continue
        raw=(MODELS/'PECAS_STL'/(p['id']+'.stl')).read_bytes()
        n=struct.unpack('<I',raw[80:84])[0]
        dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
        mesh=np.frombuffer(raw,dtype=dtype,offset=84,count=n)['v'].astype(float)
        points=np.c_[mesh.reshape(-1,3),np.ones(n*3)]@np.array(p['matriz']).T
        triangles.extend(points[:,:3].reshape(n,3,3))
        colors.extend([to_rgb('#d7b680')]*n)
        alphas.extend([.16 if p['id'] in ('C2_FRENTE','C5_DIREITA') else 1]*n)
    for e in ELECTRONICS:
        for face in box_mesh(e['min'],e['max']):
            for indices in [[0,1,2],[0,2,3]]:
                triangles.append(np.array(face)[indices]);colors.append(to_rgb('#329889'));alphas.append(1)
    for x,y in SCREWS:
        for face in box_mesh([x-10,y-10,3],[x+10,y+10,47]):
            for indices in [[0,1,2],[0,2,3]]:
                triangles.append(np.array(face)[indices]);colors.append(to_rgb('#986735'));alphas.append(1)
    tri=np.array(triangles);az=np.radians(-63);el=np.radians(42)
    right=np.array([-np.sin(az),np.cos(az),0])
    up=np.array([-np.cos(az)*np.sin(el),-np.sin(az)*np.sin(el),np.cos(el)])
    view=np.cross(right,up)
    projected=np.stack([tri@right,tri@up],axis=-1)
    depth=(tri@view).mean(1)
    depth[:12]=-1e9  # C0 está inteiramente sob todos os componentes.
    order=np.argsort(depth)
    normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-12)
    light=np.array([.2,-.5,.84]);light/=np.linalg.norm(light)
    shade=.62+.38*np.abs(normals@light)
    rgba=np.c_[np.array(colors)*shade[:,None],alphas]
    fig,ax=plt.subplots(figsize=(11.7,8.3))
    ax.add_collection(PolyCollection(projected[order],facecolors=rgba[order],edgecolors='none'))
    ax.autoscale();ax.set_aspect('equal');ax.axis('off')
    ax.set_title('Interior da caixa — tampa removida',fontsize=15,pad=20)
    fig.text(.5,.08,'Perfis de MDF exportados em STL; verde = envelopes nominais da eletrônica.',ha='center',fontsize=10)
    fig.text(.5,.045,'Frente e lateral direita transparentes para inspeção; desenho sem escala.',ha='center',fontsize=9,color='#617980')
    fig.tight_layout(rect=[0,.1,1,1]);fig.savefig(GUIDE/'Previa_3D.png',dpi=170);plt.close(fig)


def manual(parts,buttons,report):
    import textwrap
    def page(pdf,title,paragraphs,figure=None):
        fig=plt.figure(figsize=(8.27,11.69),facecolor='white')
        fig.text(.08,.94,title,fontsize=19,weight='bold',color='#244951')
        y=.89
        for text in paragraphs:
            for line in textwrap.wrap(text,width=86):
                fig.text(.08,y,line,fontsize=10.5,color='#263d46');y-=.020
            y-=.016
        if figure:fig.add_axes([.06,.07,.88,max(.22,y-.10)]).imshow(plt.imread(figure));plt.gca().axis('off')
        fig.text(.08,.035,f'Caixa integrada • 18/11/2026 • mm • página {pdf.get_pagecount()+1}',fontsize=8,color='#617980')
        pdf.savefig(fig);plt.close(fig)
    with PdfPages(GUIDE/'Guia_de_montagem.pdf') as pdf:
        page(pdf,'Caixa eletrônica integrada',[
            'Revisão para painel de 500 × 380 × 3 mm e mapa com 18 botões KFC-A06. Caixa externa 500 × 380 × 50 mm; vão interno de 44 mm. A estrutura do pedestal permanece a mesma.',
            'A tampa C1 tem 72 furos circulares de 2,6 mm: quatro por botão, um alinhado a cada terminal. Os centros de cada grupo formam um retângulo de 12,5 × 5 mm. Os relevos têm cavidades inferiores de 15,1 × 12,5 mm para acesso à solda; somente os fios atravessam o MDF.',
            'As peças de MDF, a cena elétrica e o conjunto do pedestal compartilham a mesma geometria. Componentes eletrônicos são modelos nominais: confirmar as medidas e os suportes no material disponível.'],GUIDE/'Planta_interna.png')
        page(pdf,'1. Peças e materiais',[
            'Refabricar C1_TAMPO_FURADO (500 × 380 × 3), C3_TRAS_USB (494 × 44 × 3), C6_NX1 e C7_NX2 (494 × 30 × 3) e C8_NY (374 × 30 × 3). A traseira tem USB deslocado para x=334 e o taco antes em x=400 passa para x=270.',
            'Reaproveitar C0_BASE, C2_FRENTE, C4_ESQUERDA e C5_DIREITA da V4, se já fabricados. A chapa de paredes contém todas as sete peças; para reposição usar os individuais em 03_PECAS, sem cortar novamente as peças reaproveitadas.',
            'Imprimir oito tacos de 20 × 20 × 44 mm com furo cego de Ø2,8 × 18 mm. Usar oito parafusos para madeira de cabeça panela, 3,5 × 12 ou 3,5 × 20 mm, oito arruelas e adesivo compatível com MDF e plástico. Testar a pega em um taco antes de imprimir o lote.',
            '18 chaves KFC-A06 de 12 × 12 × 4,3 mm; placas, falante, cabo USB e fios conforme o sistema. A visualização não define alimentação, pinagem nem GPIO dos 18 botões.'],GUIDE/'Previa_dos_cortes.png')
        page(pdf,'2. Corte da tampa na CNC',[
            'Arquivo: 01_CORTE_PAINEIS/C1_TAMPO_FURADO_500x380.dxf; alternativa SVG em milímetros e escala 1:1. O contorno externo é 500 × 380 mm. Origem no canto dianteiro esquerdo, olhando a face superior; x para a direita e y para a traseira. Não espelhar.',
            'Há 73 contornos fechados: um perímetro e 72 círculos. Não há furo central nem rasgos de terminais no MDF. Cada botão tem furos em x=centro±6,25 e y=centro±2,5 mm. Consultar Coordenadas_furos_tampa.csv. O PDF Tampa_CNC_500x380_1_1.pdf é referência 1:1; seus números não são cortes.',
            'Cortar os furos antes do perímetro. Os vetores estão em milímetros, sem compensação: aplicar o raio da fresa ou a compensação do feixe uma vez no CAM. Selecionar ferramenta e parâmetros para o material e o diâmetro dos furos. Esta revisão não fornece G-code.',
            'Fazer o cupom de MDF com quatro furos de 2,6 mm para conferir o diâmetro, o alinhamento e a passagem dos fios reais. Testar separadamente o encaixe do botão e das soldas no suporte impresso. O corpo do botão é sustentado pelo assento do relevo impresso.'])
        page(pdf,'3. Paredes e passagem USB',[
            'Montar as quatro paredes sobre C0, em encaixe a seco. Laterais medem 380 × 44; frente e traseira 494 × 44, entre as laterais. Conferir esquadro e o contorno externo 500 × 380.',
            'Usar a nova traseira C3: abertura USB em x=322..346, aberta de z=33 a 47. Os dois rasgos de abraçadeira estão em x=362..365 e x=374..377. O conector do ESP32 aponta para a traseira e o cabo passa em x=334.',
            'Frente: centros de parafusos x=30,150,400,470. Traseira: x=30,150,270,470. Todos os eixos ficam em z=35 desde a face inferior de C0, ou 32 mm desde a borda inferior da parede. Os cortes têm furos de Ø3,5 mm. Se a rosca prender no MDF, retirar a tampa e alargar somente a passagem na parede para Ø4 mm.',
            'Se a traseira anterior já estiver cortada, a substituição evita manter o entalhe USB e os furos antigos na nova montagem. Fixar a abraçadeira no cabo com folga de serviço; não puxar o conector da placa.'])
        page(pdf,'4. Nervuras e tacos',[
            'Montar NX1 em y=110 e NX2 em y=240; NY em x=250. A borda inferior permanece em z=17 e a superior em z=47. As meias-madeiras conservam folga total de 0,15 mm; fazer o encaixe a seco antes da cola.',
            'As novas passagens inferiores têm 12 mm de profundidade; nelas o vão desde o fundo da caixa passa de 14 para 26 mm. Resta uma faixa superior de 18 mm para colagem à tampa. Usar os perfis novos; não confundir com as nervuras lisas da V4.',
            'Tacos: frente em (30,13), (150,13), (400,13), (470,13); traseira em (30,367), (150,367), (270,367), (470,367). O taco traseiro x=270 libera o espaço atrás da protoboard. Base dos tacos em z=3; topo em z=47.',
            'Colar nervuras e tacos somente à face inferior de C1. Não colar o conjunto removível ao fundo nem às paredes. Transferir os furos horizontais a seco e fazer pré-furo na madeira; para tacos impressos usar o furo cego previsto no modelo.'],GUIDE/'Previa_3D.png')
        page(pdf,'5. Eletrônica e caminhos dos fios',[
            'Protoboard: canto inferior esquerdo (285,270,6), corpo de aproximadamente 170 × 70 × 9 mm. ESP32 deslocado junto com ela: origem (320,286,22), conector USB para a traseira. Não fixar a placa diretamente no MDF sem isolamento e retenção.',
            'DFPlayer: origem (420,160,10), com suportes até z=3 e espaço para retirar o microSD na direção +y. Falante: centro acústico (330,4,25), voltado para a grade frontal. Fixar o falante com suporte próprio; não usar a grade como apoio.',
            'A área à esquerda permanece livre sob os botões. Descer os fios pelas passagens do painel e conduzi-los na zona baixa, antes de subir à protoboard. Nas nervuras, usar os vazios inferiores e os canais; não prensar fios nas meias-madeiras ou sob os tacos.',
            'Os fios da cena são esquemáticos. A ligação elétrica completa de 18 entradas precisa seguir o circuito escolhido; a antiga lista de GPIO de dez botões não foi estendida por suposição. Reservar laço de serviço para levantar a tampa 105 mm e desconectar quando necessário.'],GUIDE/'Planta_interna.png')
        page(pdf,'6. Botões, relevos e fechamento',[
            'Usar os relevos do arquivo relevo-500x380/construcoes_vista_aerea.scad. A face superior da tampa da caixa é z=50; corresponde ao z=0 do mapa. Os corpos dos botões ficam em z=50+h_botao, em alturas diferentes conforme edifícios e pisos.',
            'Não instalar todos os botões diretamente no MDF nem nivelar suas alturas. Os 18 componentes KFC-A06 são os mesmos do arquivo do mapa, com os quatro terminais e a orientação original. Alinhar os centros pelo CSV atual antes de colar os relevos. Os pontos 14 e 15 foram afastados 0,5 mm cada em x para manter a parede entre os canais ampliados.',
            'A cavidade inferior dos relevos mede 15,1 × 12,5 mm e sobe até 1,2 mm abaixo do corpo, preservando o assento. Soldar pela face inferior antes de fixar o relevo no MDF, ou soldar fora antes de encaixar. Acomodar as juntas nos canais e passar cada fio pelo furo alinhado ao terminal. Os quatro furos ficam disponíveis mesmo quando só dois recebem fios. Nos pontos 1–3 a base do corpo permanece em z=5. Conferir as juntas, o acionamento e a passagem livre dos fios antes de fechar.',
            'Assentar a tampa com os tacos e nervuras, sem forçar cabos. Colocar os oito parafusos horizontais com arruelas. Apertar sem esmagar o MDF. Para manutenção, retirar os parafusos e levantar a tampa pelo laço de serviço.'])
        page(pdf,'7. Conferência da revisão',[
            f'Validação digital: {report["botoes"]} botões e {report["furos_fios"]} furos circulares, quatro por botão; comparação com seção real do SCAD, erro máximo {report["erro_maximo_furacao_mm"]:.6f} mm. Os 13 pares SVG/DXF (incluindo o cupom) foram relidos e comparados.',
            'Os envelopes conservadores dos componentes e das áreas de acesso foram confrontados com todas as paredes, nervuras e tacos, sem interseção volumétrica. As descidas dos 18 botões também estão livres. A verificação não inclui dimensões de placas diferentes das representadas.',
            'Os nove perfis são exportados em STL para verificar fechamento e espessura. O relatório VALIDACAO_INTEGRACAO.json registra os resultados e os hashes das fontes.',
            'Antes da fabricação definitiva, testar encaixes e montar a seco com os componentes reais. A alteração das nervuras requer avaliação física da rigidez e da colagem. O cálculo anterior de estabilidade (massa total de referência de 19 kg) continua na documentação arquivada da V4; esta revisão não refaz o dimensionamento estrutural.'])
    # Gabarito de conferência do painel em escala física, sem margem ou ajuste à página.
    fig=plt.figure(figsize=(500/25.4,380/25.4));ax=fig.add_axes([0,0,1,1])
    draw_profile(ax,parts[1],color='white')
    for b in buttons:ax.text(b['x_mm'],b['y_mm']+6,str(b['numero']),ha='center',fontsize=6)
    ax.set(xlim=(0,500),ylim=(0,380));ax.set_aspect('equal');ax.axis('off')
    fig.savefig(GUIDE/'Tampa_CNC_500x380_1_1.pdf',pad_inches=0);plt.close(fig)


def validate_stls(parts,tmp):
    results=[]
    for i,p in enumerate(parts):
        output=MODELS/'PECAS_STL'/(p['id']+'.stl');output.parent.mkdir(exist_ok=True)
        source=tmp/'peca.scad';source.write_text('use <'+(MODELS/'Geometria_caixa.scad').as_posix()+'>\nlinear_extrude(3) perfil_caixa('+str(i)+');\n')
        # Solicitar o STL binário uma única vez por perfil.
        result=subprocess.run(['openscad','--export-format','binstl','-o',str(output),str(source)],capture_output=True,text=True)
        assert result.returncode==0 and 'WARNING:' not in result.stderr and 'ERROR:' not in result.stderr,result.stderr
        import struct
        data=output.read_bytes();n=struct.unpack('<I',data[80:84])[0]
        mesh=np.frombuffer(data,dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')]),offset=84,count=n)['v'].astype(float)
        vertices,ids=np.unique(np.round(mesh.reshape(-1,3),5),axis=0,return_inverse=True)
        faces=ids.reshape(-1,3);edges=Counter();directed=Counter()
        for f in faces:
            for a,b in zip(f,np.roll(f,-1)):edges[tuple(sorted((int(a),int(b))))]+=1;directed[int(a),int(b)]+=1
        assert all(v==2 for v in edges.values()),p['id']
        assert all(directed[a,b]==directed[b,a] for a,b in edges),p['id']
        assert np.isclose(vertices[:,2].ptp() if hasattr(vertices[:,2],'ptp') else np.ptp(vertices[:,2]),3)
        results.append(dict(peca=p['id'],triangulos=n,malha_fechada=True,normais_coerentes=True,espessura_mm=3))
    return results


def main():
    for d in ['01_CORTE_PAINEIS','02_CHAPA_600x400','03_PECAS','04_MODELO_3D','05_GUIA','06_FONTE','07_IMPRESSAO_3D']:(ROOT/d).mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='caixa-integrada-') as temp:
        tmp=Path(temp)
        buttons,params=read_map(tmp)
        parts=make_parts(buttons,params)
        export_cuts(parts);write_models(parts,buttons)
        print('Cortes e modelos gerados; conferindo seção do mapa...',flush=True)
        report=check_geometry(parts,buttons,tmp)
        print('Furação e interferências conferidas; exportando nove STL...',flush=True)
        report['pecas_mdf']=validate_stls(parts,tmp)
        exportar_tacos(parts, SCREWS)
        # CSG de todas as entradas garante resolução de includes e dos módulos compartilhados.
        for name in ['Caixa_com_sistema_eletronico','Pedestal_com_caixa']:
            for defines in [[],['tacos_impressos=true'],['mostrar_eletronica=false'] if name.startswith('Pedestal') else ['vista="sem_tampa"']]:
                run_scad(MODELS/(name+'.scad'),tmp/(name+'.csg'),defines)
        previews(parts,buttons);manual(parts,buttons,report)
    data=dict(revisao='quatro_furos_por_botao_2026-11-09',unidade='mm',dimensoes_externas=[500,380,50],
        furacao_tampa=dict(furos_por_botao=4,total_furos=72,diametro_mm=params[3],passo_x_mm=params[4],passo_y_mm=params[5]),
        pecas=parts,botoes=buttons,tacos=SCREWS,eletronica=ELECTRONICS,areas_servico=SERVICE)
    (ROOT/'06_FONTE/parametros_e_geometria.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    with (GUIDE/'Coordenadas_botoes.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=list(buttons[0]),delimiter=';');wr.writeheader();wr.writerows(buttons)
    with (GUIDE/'Coordenadas_furos_tampa.csv').open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.writer(f,delimiter=';');wr.writerow(['botao','passagem_no_botao','x_mm','y_mm','diametro_mm'])
        for b in buttons:
            for j,h in enumerate(parts[1]['furos'][4*(b['numero']-1):4*b['numero']],1):
                wr.writerow([b['numero'],j,*h['centro'],2*h['raio']])
    report['fontes_sha256']={str(p.relative_to(PROJECT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [MAP,MAP.parent/'botao_tatil_KFC-A06_12x12x4p3.scad',Path(__file__),MODELS/'Componentes_eletronicos.scad',MODELS/'Geometria_caixa.scad']}
    (GUIDE/'VALIDACAO_INTEGRACAO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=='__main__':main()
