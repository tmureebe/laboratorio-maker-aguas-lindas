#!/usr/bin/env python3
"""Exporta as 13 peças imprimíveis do mapa atual e confere suas malhas.

Requer OpenSCAD e NumPy. Os modelos são exportados individualmente, em mm,
com a base em Z=0. Uma pasta de exportação anterior é preservada no histórico.
"""
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
import csv
import hashlib
import json
import shutil
import struct
import subprocess
import tempfile
import numpy as np

BASE=Path(__file__).resolve().parent
SOURCE=BASE/'construcoes_vista_aerea.scad'
OUT=BASE/'STL_para_impressao'
PARTS=[
 ('01_Bloco_administrativo','edificio',0),
 ('02_Bloco_de_ensino','edificio',1),
 ('03_Restaurante','edificio',2),
 ('04_Quadra_poliesportiva','edificio',3),
 ('05_Passarelas_rede_central','passagem',0),
 ('06_Passarela_continuacao_norte','passagem',1),
 ('07_Acesso_entrada','passagem',2),
 ('08_Piso_entrada_principal','piso',0),
 ('09_Piso_estacionamento','piso',1),
 ('10_Piso_bicicletario','piso',2),
 ('11_Rampa','rampa',0),
 ('12_Escada_administrativo','escada',0),
 ('13_Escada_ensino','escada',1),
]
DTYPE=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])


def clean_triangulation(mesh):
    """Retira faces colineares e subdivide arestas para manter a superfície fechada.

    O STL binário reduz coordenadas a float32. Uma aresta compartilhada pode
    ganhar triângulos de área zero na exportação; o contorno é preservado.
    """
    area=np.linalg.norm(np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0]),axis=1)/2
    removed=int(np.sum(area<=1e-20))
    if not removed:return mesh,dict(faces_colineares_removidas=0,arestas_retrianguladas=0)
    mesh=mesh[area>1e-20]
    vertices,ids=np.unique(mesh.reshape(-1,3),axis=0,return_inverse=True)
    faces=ids.reshape(-1,3).tolist();splits=0
    for _ in range(100):
        edges=Counter()
        for face in faces:
            for a,b in zip(face,face[1:]+face[:1]):edges[tuple(sorted((a,b)))]+=1
        boundary={e for e,n in edges.items() if n==1}
        if not boundary:break
        candidates=set(v for e in boundary for v in e);done=False
        for fi,face in enumerate(faces):
            for i in range(3):
                a,b,c=face[i],face[(i+1)%3],face[(i+2)%3]
                if tuple(sorted((a,b))) not in boundary:continue
                v=vertices[b]-vertices[a];vv=float(v@v);inside=[]
                for q in candidates-{a,b}:
                    t=float((vertices[q]-vertices[a])@v/vv)
                    if 1e-7<t<1-1e-7 and np.linalg.norm(vertices[q]-(vertices[a]+t*v))<=1e-7:inside.append((t,q))
                if not inside:continue
                chain=[a]+[q for t,q in sorted(inside)]+[b]
                faces[fi:fi+1]=[[u,v,c] for u,v in zip(chain,chain[1:])]
                splits+=1;done=True;break
            if done:break
        if not done:raise AssertionError('Não foi possível fechar a triangulação sem alterar contornos')
    else:raise AssertionError('Excedida a quantidade de reparos de triangulação')
    return vertices[np.array(faces)],dict(faces_colineares_removidas=removed,arestas_retrianguladas=splits)


def export(part):
    name,kind,index=part
    path=OUT/(name+'.stl')
    result=subprocess.run(['openscad','--export-format','binstl','-o',str(path),
        '-D','modo="peca"','-D',f'tipo_peca="{kind}"','-D',f'numero_peca={index}',str(SOURCE)],
        capture_output=True,text=True)
    log=result.stdout+result.stderr
    (OUT/'verificacao'/f'{name}.log').write_text(log)
    assert result.returncode==0 and 'ERROR:' not in log and 'WARNING:' not in log,log
    raw=path.read_bytes();count=struct.unpack('<I',raw[80:84])[0]
    assert len(raw)==84+50*count
    records=np.frombuffer(raw,dtype=DTYPE,offset=84,count=count).copy()
    mesh=records['v'].astype(float)
    before_min=mesh.reshape(-1,3).min(0)
    # Alterar apenas a posição na mesa; a geometria e a orientação são preservadas.
    records['v']-=before_min.astype(np.float32)
    mesh,cleanup=clean_triangulation(records['v'].astype(float))
    count=len(mesh)
    normals=np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0])
    normals/=np.maximum(np.linalg.norm(normals,axis=1,keepdims=True),1e-20)
    records=np.zeros(count,dtype=DTYPE);records['v']=mesh;records['normal']=normals
    with path.open('wb') as f:
        f.write(raw[:80]);f.write(struct.pack('<I',count));f.write(records.tobytes())
    mesh=records['v'].astype(float)
    vertices,ids=np.unique(mesh.reshape(-1,3),axis=0,return_inverse=True)
    faces=ids.reshape(-1,3)
    edges=Counter();directed=Counter();adjacency=defaultdict(set)
    for face in faces:
        for a,b in zip(face,np.roll(face,-1)):
            a,b=int(a),int(b)
            edges[tuple(sorted((a,b)))]+=1;directed[a,b]+=1
            adjacency[a].add(b);adjacency[b].add(a)
    assert all(n==2 for n in edges.values()),name+': aresta aberta ou não manifold'
    assert all(directed[a,b]==directed[b,a] for a,b in edges),name+': orientação incoerente'
    area=np.linalg.norm(np.cross(mesh[:,1]-mesh[:,0],mesh[:,2]-mesh[:,0]),axis=1)/2
    assert np.all(area>1e-20),name+': face degenerada'
    volume=float(np.einsum('ij,ij->i',mesh[:,0],np.cross(mesh[:,1],mesh[:,2])).sum()/6)
    assert volume>0,name+': volume inválido'
    todo=set(range(len(vertices)));groups=0
    while todo:
        groups+=1;pending=[todo.pop()]
        while pending:
            for neighbor in adjacency[pending.pop()]:
                if neighbor in todo:todo.remove(neighbor);pending.append(neighbor)
    assert groups==1,(name,'peça desconectada',groups)
    lo=vertices.min(0);hi=vertices.max(0)
    assert np.allclose(lo,[0,0,0],atol=1e-5)
    assert max(hi[:2])<=256,(name,'dimensão na mesa maior que 256 mm',hi)
    return dict(arquivo=path.name,tipo=kind,numero_no_scad=index,quantidade=1,
        dimensoes_xyz_mm=np.round(hi-lo,4).tolist(),triangulos=count,
        componentes=groups,malha_fechada=True,orientacao_coerente=True,
        limpeza_triangulacao=cleanup,
        volume_mm3=round(volume,4),base_z_mm=0,
        translacao_aplicada_mm=(-before_min).tolist(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def main():
    assert shutil.which('openscad'),'OpenSCAD não encontrado'
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    if OUT.exists():
        archive=BASE/'99_HISTORICO'/('STL_para_impressao_'+datetime.now().strftime('%Y%m%d_%H%M%S_%f'))
        archive.parent.mkdir(parents=True,exist_ok=True);OUT.rename(archive)
        print('Exportação anterior preservada:',archive,flush=True)
    (OUT/'verificacao').mkdir(parents=True)
    rows=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending={pool.submit(export,part):part for part in PARTS}
        for future in as_completed(pending):
            row=future.result();rows.append(row)
            print(row['arquivo'],row['dimensoes_xyz_mm'],'OK',flush=True)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash,'Fonte alterada durante exportação'
    rows.sort(key=lambda r:r['arquivo'])
    with (OUT/'Lista_de_impressao.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f,delimiter=';');writer.writerow(['arquivo','quantidade','x_mm','y_mm','z_mm'])
        for r in rows:writer.writerow([r['arquivo'],1,*r['dimensoes_xyz_mm']])
    report=dict(fonte='../construcoes_vista_aerea.scad',sha256_fonte=source_hash,
        unidade='mm',escala=1,total_arquivos=len(rows),todas_pecas_verificadas=True,pecas=rows)
    (OUT/'VERIFICACAO.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines=['# Maquete — STL para impressão 3D',
        '', 'Imprimir **uma unidade de cada um dos 13 STL** desta pasta, em **milímetros e escala 100%**. As peças estão separadas, orientadas com a face de montagem para baixo e apoiadas em **Z=0**.',
        '', '## Lista de peças', '', '| Arquivo | Dimensões X × Y × Z (mm) |', '|---|---|']
    for r in rows:lines.append('| '+r['arquivo']+' | '+' × '.join(f'{v:.2f}' for v in r['dimensoes_xyz_mm'])+' |')
    lines += ['', '## Impressão e montagem', '',
        'Importar cada STL no fatiador e conferir a prévia das camadas, a adesão das peças estreitas e as pontes sobre os canais inferiores. A maior dimensão na mesa de cada arquivo é inferior a 256 mm; verificar a área útil da sua impressora antes de fatiar.',
        '', 'Os alojamentos, assentos, cavidades de acesso à solda e números fazem parte dos edifícios e pisos. Os botões KFC-A06 são componentes físicos. O tampo de MDF é cortado na CNC com 72 furos de 2,6 mm, quatro por botão, alinhados aos terminais.',
        '', 'As duas escadas são impressas separadamente e coladas sobre os respectivos edifícios, conforme o modelo completo. A rampa e as três peças de circulação são montadas ao redor dos blocos. Usar o SCAD principal como referência de posicionamento.',
        '', 'Cada botão tem uma cavidade inferior de 15,3 × 12,5 mm, aberta até 1,2 mm abaixo do corpo. O assento é fechado no centro, com quatro rasgos de terminais de 2,8 × 2,8 mm. O assento e as paredes de pelo menos 1,2 mm continuam sustentando o botão. Fazer a soldagem pela face inferior com o relevo fora do MDF, ou soldar antes de encaixar. Passar cada fio pelo furo de MDF alinhado ao seu terminal antes de fixar o relevo. Os canais e furos foram dimensionados para fios e soldas; conectores fêmea com capa plástica precisam de dimensionamento próprio. Conferir primeiro com o botão, os fios e a ponta de ferro reais.',
        '', 'Esta pasta contém as 13 peças principais da maquete. As legendas externas opcionais de texto/Braille continuam disponíveis no SCAD como `tipo_peca="legenda"`.',
        '', '## Conferência', '',
        'Todos os STL foram relidos e conferidos: malha fechada, orientação coerente, volume positivo, uma peça conectada por arquivo e base em Z=0. As dimensões e hashes estão em `VERIFICACAO.json`; a lista resumida está em `Lista_de_impressao.csv`.',
        '', 'Fonte: `../construcoes_vista_aerea.scad`. Para regenerar, executar `python ../exportar_stl_maquete.py` a partir desta pasta. A exportação anterior será preservada no histórico.', '']
    (OUT/'LEIA_ANTES_DE_IMPRIMIR.md').write_text('\n'.join(lines))
    print('Concluído:',OUT,flush=True)


if __name__=='__main__':main()
