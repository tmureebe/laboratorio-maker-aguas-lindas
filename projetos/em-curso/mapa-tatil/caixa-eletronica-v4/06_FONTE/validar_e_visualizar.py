#!/usr/bin/env python3
"""Confere colisões das peças novas, renderiza STL e gera vistas sem OpenGL.

Requer Python, numpy, matplotlib e OpenSCAD. As malhas STL são de verificação;
os vetores DXF/SVG são os arquivos de fabricação. Não é ensaio físico.
"""
from pathlib import Path
import hashlib
import json
import os
import struct
import subprocess
import tempfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

ROOT=Path(__file__).resolve().parents[1]


def inside(x,y,poly):
    yes=False
    for (a,b),(c,d) in zip(poly,poly[1:]+poly[:1]):
        if (b>y)!=(d>y) and x < (c-a)*(y-b)/(d-b)+a:
            yes=not yes
    return yes


def occupied(part):
    """Decomposição exata em caixas para perfis ortogonais, círculo conservador."""
    polys=[part['contorno']]+[h for h in part['furos'] if isinstance(h,list)]
    xs=sorted({x for poly in polys for x,y in poly})
    ys=sorted({y for poly in polys for x,y in poly})
    m=np.array(part['matriz'])
    result=[]
    for x0,x1 in zip(xs,xs[1:]):
        for y0,y1 in zip(ys,ys[1:]):
            x,y=(x0+x1)/2,(y0+y1)/2
            if inside(x,y,polys[0]) and not any(inside(x,y,p) for p in polys[1:]):
                pts=np.array([[x,y,z,1] for x in (x0,x1) for y in (y0,y1) for z in (0,3)])@m.T
                result.append((pts[:,:3].min(axis=0),pts[:,:3].max(axis=0)))
    return result


def load_stl(path):
    raw=path.read_bytes()
    count=struct.unpack('<I',raw[80:84])[0] if len(raw)>84 else 0
    if len(raw)==84+50*count:
        dtype=np.dtype([('normal','<f4',(3,)),('v','<f4',(3,3)),('attr','<u2')])
        return np.frombuffer(raw,dtype=dtype,offset=84)['v'].astype(float)
    vertices=[]
    for line in raw.decode('ascii').splitlines():
        fields=line.split()
        if fields and fields[0]=='vertex':vertices.append(list(map(float,fields[1:])))
    return np.array(vertices).reshape(-1,3,3)


def box_faces(lo,hi):
    p=np.array([[x,y,z] for x in (lo[0],hi[0]) for y in (lo[1],hi[1]) for z in (lo[2],hi[2])])
    return [p[list(ids)] for ids in [(0,1,3,2),(4,6,7,5),(0,4,5,1),(2,3,7,6),(0,2,6,4),(1,5,7,3)]]


def transform(mesh,matrix):
    flat=mesh.reshape(-1,3)
    q=np.c_[flat,np.ones(len(flat))]@np.array(matrix).T
    return q[:,:3].reshape(mesh.shape)


def preview(data,meshes):
    origin=np.array(data['matriz_caixa_no_pedestal'])
    ref=(ROOT/'04_MODELO_3D/pedestal_existente.scad').read_text()
    old={}
    for line in ref.splitlines():
        for key in ['nomes','contornos','matrizes','tipos']:
            if line.startswith(key+'='):old[key]=json.loads(line[len(key)+1:-1])
    def new_meshes(ax,lift=0,original=False):
        for p,mesh in zip(data['pecas'],meshes):
            mat=np.array(p['matriz'],float)
            if p['solidario_tampa']:mat[2,3]+=lift
            m=transform(mesh,(origin@mat) if original else mat)
            ax.add_collection3d(Poly3DCollection(m,facecolors='#e8cf97' if p['solidario_tampa'] else '#9dbfc7',
                                                alpha=1,shade=True,lightsource=matplotlib.colors.LightSource(azdeg=320,altdeg=45)),autolim=False)
        for x,y in data['parafusos']:
            faces=np.array(box_faces([x-10,y-10,3+lift],[x+10,y+10,47+lift]))
            if original:faces=transform(faces,origin)
            ax.add_collection3d(Poly3DCollection(faces,facecolor='#a67c4a',edgecolor='#6e532f',linewidth=.3),autolim=False)
    def draw_old(ax):
        for name,poly,m,kind in zip(old['nomes'],old['contornos'],old['matrizes'],old['tipos']):
            # Faces externas e internas; vistas de referência, sem cálculo de cargas.
            faces=[]
            for ring in poly:
                for a,b in zip(ring,ring[1:]+ring[:1]):
                    faces.append([[*a,0],[*b,0],[*b,3],[*a,3]])
            faces += [[[x,y,z] for x,y in poly[0]] for z in (0,3)]
            faces=[(np.c_[np.array(face),np.ones(len(face))]@np.array(m).T)[:,:3] for face in faces]
            ax.add_collection3d(Poly3DCollection(faces,facecolor='#aa9875' if kind!='G' else '#b58a9f',edgecolor='none',alpha=1),autolim=False)
    plt.rcParams['font.family']='DejaVu Sans'
    fig=plt.figure(figsize=(12,8),facecolor='white')
    ax=fig.add_subplot(121,projection='3d');draw_old(ax);new_meshes(ax,original=True)
    ax.set(xlim=(-70,510),ylim=(-100,450),zlim=(0,1080));ax.set_box_aspect((580,550,1080));ax.view_init(24,-55);ax.set_axis_off()
    ax.set_title('Pedestal com caixa adicional',fontsize=13,color='#203340',pad=4)
    ax=fig.add_subplot(122,projection='3d');new_meshes(ax,lift=130)
    ax.set(xlim=(-20,520),ylim=(-20,400),zlim=(0,260));ax.set_box_aspect((540,420,260));ax.view_init(26,-58);ax.set_axis_off()
    ax.set_title('Painel, tacos e nervuras removíveis',fontsize=13,color='#203340',pad=4)
    fig.suptitle('Caixa 500 × 380 × 50 mm • dois painéis sem furos',fontsize=19,color='#203340',y=.96)
    fig.text(.05,.04,'Azul: fundo e paredes fixos • Dourado: painel removível e reforços\nVista geométrica; eletrônica e mapa não representados.',fontsize=10,color='#203340')
    fig.subplots_adjust(left=0,right=1,bottom=.1,top=.9,wspace=0)
    fig.savefig(ROOT/'05_GUIA/Previa_3D.png',dpi=180)
    fig.savefig(ROOT/'05_GUIA/Previa_3D.pdf')
    plt.close(fig)


def main():
    data=json.loads((ROOT/'06_FONTE/parametros_e_geometria.json').read_text())
    groups=[(p['id'],occupied(p)) for p in data['pecas']]
    for i,(x,y) in enumerate(data['parafusos'],1):
        groups.append((f'TACO_{i}',[(np.array([x-10,y-10,3]),np.array([x+10,y+10,47]))]))
    collisions=[]
    for i,(a,aa) in enumerate(groups):
        for b,bb in groups[i+1:]:
            volume=0.
            for lo,hi in aa:
                for lo2,hi2 in bb:
                    volume+=float(np.maximum(0,np.minimum(hi,hi2)-np.maximum(lo,lo2)).prod())
            if volume>1e-6:collisions.append(dict(pecas=[a,b],volume_mm3=volume))
    assert not collisions,collisions
    originals=json.loads((ROOT/'05_GUIA/ORIGINAIS_PRESERVADOS_SHA256.json').read_text())
    assert all(hashlib.sha256((ROOT.parent/p).read_bytes()).hexdigest()==h for p,h in originals.items())
    logs=ROOT/'05_GUIA/logs_OpenSCAD';logs.mkdir(exist_ok=True)
    checks=[];meshes=[]
    with tempfile.TemporaryDirectory(prefix='caixa_v4_') as temp:
        for i,part in enumerate(data['pecas'],1):
            target=Path(temp)/f'{part["id"]}.stl'
            result=subprocess.run(['openscad','-o',str(target),'-D','modo="peca3d"','-D',f'numero_peca={i}',
                                   str(ROOT/'04_MODELO_3D/Pedestal_com_caixa.scad')],capture_output=True,text=True)
            (logs/f'{part["id"]}.log').write_text(result.stdout+result.stderr)
            assert result.returncode==0 and target.exists(),result.stderr
            assert 'ERROR' not in result.stderr and 'WARNING' not in result.stderr,result.stderr
            mesh=load_stl(target)
            assert len(mesh)>0
            flat=mesh.reshape(-1,3)
            # Arestas orientadas por vértices quantizados: toda aresta tem duas faces.
            edges={}
            for tri in mesh:
                vs=[tuple(np.round(p,5)) for p in tri]
                for a,b in zip(vs,vs[1:]+vs[:1]):
                    key=tuple(sorted((a,b)))
                    edges.setdefault(key,[]).append((a,b))
            assert all(len(v)==2 and v[0]==v[1][::-1] for v in edges.values()),part['id']
            vol=float(np.einsum('ij,ij->i',mesh[:,0],np.cross(mesh[:,1],mesh[:,2])).sum()/6)
            assert vol>0
            checks.append(dict(id=part['id'],triangulos=len(mesh),malha_fechada=True,volume_mm3=round(vol,3),
                               minimo_mm=flat.min(axis=0).tolist(),maximo_mm=flat.max(axis=0).tolist()))
            meshes.append(mesh)
        csg=subprocess.run(['openscad','-o',str(Path(temp)/'conjunto.csg'),str(ROOT/'04_MODELO_3D/Pedestal_com_caixa.scad')],capture_output=True,text=True)
        assert csg.returncode==0 and not csg.stderr,csg.stderr
    report=dict(colisoes_pecas_novas_e_tacos=collisions,originais_com_hash_conferido=len(originals),
                metodo_colisoes='Decomposição de perfis ortogonais em prismas retangulares; furos circulares conservadoramente preenchidos.',
                geometria_OpenSCAD=checks,conjunto_CSG_compilado=True,
                limites='Sem ensaios físicos. O modelo de referência conserva os dentes antigos; na montagem real são lixados rentes antes da colagem.')
    (ROOT/'05_GUIA/VALIDACAO_3D.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
    preview(data,meshes)
    print(f'{len(checks)} malhas fechadas; zero colisões entre peças novas; {len(originals)} arquivos originais preservados.')


if __name__=='__main__':main()
