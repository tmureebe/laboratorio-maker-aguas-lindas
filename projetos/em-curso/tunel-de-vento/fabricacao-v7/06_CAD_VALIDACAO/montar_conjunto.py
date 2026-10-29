#!/usr/bin/python3
"""Reconstrói a montagem completa pelas coordenadas de projeto. Sem fontes externas."""
from pathlib import Path
import json,subprocess
import numpy as np
from malhas import read,write,rotation,transform
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'01_IMPRESSAO_3D/01_pecas_finais'
M=ROOT/'06_CAD_VALIDACAO/malhas_MDF_REFERENCIA'
OUT=ROOT/'05_VISUALIZACAO'; OUT.mkdir(exist_ok=True)
scene=[]
def add(name,tris,material,source='',matrix=None,xyz=(0,0,0),group='',new=False):
    scene.append(dict(nome=name,tris=transform(tris,matrix,xyz),material=material,
                      fonte=source,grupo=group or material,novo=new))
def imp(name,file,xyz=(0,0,0),matrix=None,group='impresso',new=False):
    path=P/file;add(name,read(path),'impresso',str(path.relative_to(ROOT)),matrix,xyz,group,new)
def mdf(name,id,xyz,matrix=None,group='MDF'):
    add(name,read(M/(id+'.stl')),'MDF',f'02_CORTE_LASER/pecas_individuais/MDF_{3 if id in ("M01","M02","M03","M04") else 6}mm/{id}.svg',matrix,xyz,group,True)
for x,prefix,piso,lateral in [(0,'entrada','M01','M02'),(400,'saida','M03','M04')]:
    mdf(prefix+'_piso',piso,(x,-63,59.4),group='duto_piso')
    mdf(prefix+'_teto',piso,(x,-63,182.4),group='duto_teto')
    for y,side in [(-60,'frente'),(63,'fundo')]:
        mdf(prefix+'_lateral_'+side,lateral,(x,y,62.4),rotation('x',90),'duto_'+side)
perm=np.array([[0,0,1],[1,0,0],[0,1,0]])
for x,id in [(25,'M13'),(150,'M13'),(350,'M23'),(450,'M13'),(550,'M13'),(695,'M19')]:
    for layer in range(4):mdf(f'pe_{x}_lamina_{layer+1}',id,(x-12+6*layer,-90 if id=='M19' else -80,0),perm,'apoios')
mdf('base_entrada','B01',(0,-110,-6),group='base')
mdf('base_saida','B02',(375,-110,-6),group='base')
for y in (-80,80):mdf('tala_'+str(y),'B03',(275,y-20,-12),group='base')
imp('camara','03_camara_aberta_200mm.stl',(200,-77,60),group='camara')
imp('moldura','04_moldura_V7_passagem_120mm.stl',(200,-77,180.8),group='janela',new=True)
for name,file,x in [('U01','U01_uniao_entrada_MDF_camara.stl',188),('U02','U02_uniao_camara_saida_MDF.stl',388),
                    ('ligacao','08_ligacao_MDF_parte5_126p2.stl',588)]:
    imp(name,file,(x,0,122.4),rotation('y',90),'conexoes',True)
imp('colmeia','07_colmeia_canais_46mm.stl',(-2.4,-65.5,187.9),rotation('y',90),'colmeia')
imp('grade','09_grade_compativel_partes1e2.stl',(692,-75,197.4),rotation('y',90),'regulador')
imp('espacador_regulador','20_espacador_regulador_8mm.stl',(695.2,-75,197.4),rotation('y',90),'regulador')
for x in (240,300,360):
    for sign in (-1,1):
        rot=rotation('z',0 if sign>0 else 180)
        pos=rot@np.array([-4,-16,0])+np.array([x,69*sign,188.3])
        imp(f'presilha_{x}_{sign}','11_presilha_janela.stl',pos,rot,'janela')
        imp(f'esp_presilha_{x}_{sign}','12_espacador_presilha_3p5mm.stl',(x-4,69*sign-4,184.8),group='janela')
imp('base_celula','14_base_celula_85mm.stl',(215,-28,0),group='sensor')
imp('espacador_celula','15_espacador_ponta_livre.stl',(282,-7.5,37),group='sensor')
imp('suporte_asa','16_suporte_asa_hastes_integradas.stl',(280,-18,40),group='sensor')
wing=read(P/'17_asa_A_simetrica.stl')
imp('asa_A','17_asa_A_simetrica.stl',(288,-45,96.4+np.ptp(wing[:,:,1])),rotation('x',-90),'sensor')
for i in range(1,6):
    path=P/f'parte_{i}.stl';tris=read(path)
    if i==5:
        tris=np.stack([-tris[:,:,2],tris[:,:,0],-tris[:,:,1]],axis=2)+[650,0,122.4]
    else:
        if i==3:tris=tris*[1,-1,-1]+[0,0,11.2]
        if i==4:tris=np.stack([-tris[:,:,1],tris[:,:,0],tris[:,:,2]],axis=2)+[0,58,11.2]
        tris=np.stack([tris[:,:,2],tris[:,:,0],tris[:,:,1]],axis=2)+[680 if i==1 else 703.2,0,122.4]
    add('parte_'+str(i),tris,'impresso',str(path.relative_to(ROOT)),group='regulador')
refs=ROOT/'03_COMPRADOS_NAO_FABRICAR/modelos_REFERENCIA';refs.mkdir(parents=True,exist_ok=True)
codes={
 'ventoinha':'''$fn=96;difference(){cube([30,120,120]);translate([-1,60,60])rotate([0,90,0])cylinder(h=32,r=55);}
 translate([0,60,60])rotate([0,90,0])cylinder(h=30,r=19);
 for(a=[0:60:300])translate([15,60,60])rotate([a,0,0])translate([-2,-3,14])cube([4,6,39]);''',
 'celula':'''difference(){cube([85,15,15]);for(x=[6.2,20.6,64.4,78.8])translate([x,7.5,-1])cylinder(h=17,r=2.2,$fn=32);
 for(x=[38,45])translate([x,-1,7.5])rotate([-90,0,0])cylinder(h=17,r=6,$fn=48);}''',
 'acrilico':'cube([172,120,3]);'}
for name,code in codes.items():
    src=refs/(name+'.scad');src.write_text('// REFERENCIA COMERCIAL: NAO IMPRIMIR ESTE MODELO\n'+code)
    subprocess.run(['openscad','-o',str(src.with_suffix('.stl')),str(src)],check=True)
    pos={'ventoinha':(650,-60,62.4),'celula':(225,-7.5,22),'acrilico':(214,-60,185.3)}[name]
    add(name,read(src.with_suffix('.stl')),'acrilico' if name=='acrilico' else 'comprado',str(src.relative_to(ROOT)),xyz=pos,group='janela' if name=='acrilico' else 'comprados')
global_dir=ROOT/'06_CAD_VALIDACAO/montagem_REFERENCIA';global_dir.mkdir(exist_ok=True)
metadata=[]
for item in scene:
    path=global_dir/(item['nome']+'.stl');write(path,item['tris'])
    rec={k:v for k,v in item.items() if k!='tris'}
    rec.update(malha=str(path.relative_to(ROOT)),minimo_mm=item['tris'].reshape(-1,3).min(0).tolist(),
               maximo_mm=item['tris'].reshape(-1,3).max(0).tolist())
    metadata.append(rec)
write(OUT/'Conjunto_COMPLETO_APENAS_VISUALIZAR.stl',np.concatenate([it['tris'] for it in scene]))
(ROOT/'06_CAD_VALIDACAO/montagem.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2))
colors={'MDF':(.69,.49,.27),'impresso':(.08,.43,.52),'comprado':(.25,.28,.31),'acrilico':(.56,.82,.9)}
mtl=''
for material,color in colors.items():
    mtl+='newmtl '+material+'\nKd '+' '.join(map(str,color))+'\nKa 0.15 0.15 0.15\n'
    if material=='acrilico':mtl+='d 0.25\n'
(OUT/'materiais.mtl').write_text(mtl)
with (OUT/'Conjunto_COMPLETO.obj').open('w') as out:
    out.write('mtllib materiais.mtl\n');start=1
    for item in scene:
        out.write('o '+item['nome']+'\nusemtl '+item['material']+'\n')
        for vert in item['tris'].reshape(-1,3):out.write('v '+' '.join(f'{q:.4f}' for q in vert)+'\n')
        for j in range(len(item['tris'])):out.write(f'f {start+3*j} {start+3*j+1} {start+3*j+2}\n')
        start+=3*len(item['tris'])
print('Montagem completa:',len(scene),'componentes/referências; STL + OBJ com materiais.')
