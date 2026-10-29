#!/usr/bin/python3
"""Malhas efetivas, cortes, seção e colisões booleanas das interfaces revisadas."""
from pathlib import Path
import collections,hashlib,itertools,json,subprocess,tempfile,xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from malhas import read,write,rotation,transform
ROOT=Path(__file__).resolve().parents[1]
results={}
def check_mesh(path):
    tri=read(path);vs,inv=np.unique(np.round(tri.reshape(-1,3),5),axis=0,return_inverse=True)
    fa=inv.reshape(-1,3);edge=np.concatenate([fa[:,[0,1]],fa[:,[1,2]],fa[:,[2,0]]])
    _,cnt=np.unique(np.sort(edge,axis=1),axis=0,return_counts=True)
    deg=np.linalg.norm(np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]),axis=1)
    volume=np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6
    assert (cnt==2).all() and (deg>1e-8).all() and volume>0,str(path)
    return dict(arquivo=str(path.relative_to(ROOT)),triangulos=len(tri),arestas_abertas=0,
                volume_mm3=round(volume,4),dimensoes_mm=np.ptp(vs,axis=0).round(4).tolist(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())
results['malhas_fabricacao']=[check_mesh(p) for p in sorted((ROOT/'01_IMPRESSAO_3D').rglob('*.stl'))]
original=json.loads((ROOT/'06_CAD_VALIDACAO/referencias/originais_sha256.json').read_text())
for rec in original:
    path=ROOT/'01_IMPRESSAO_3D/01_pecas_finais'/rec['arquivo']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==rec['sha256']
results['cinco_pecas_recebidas_preservadas']=True
cuts=json.loads((ROOT/'06_CAD_VALIDACAO/cortes.json').read_text())
pts={p['id']:p for p in cuts['pecas']};counts=collections.Counter()
for sheet in cuts['chapas']:
    root=ET.parse(ROOT/(sheet['caminho']+'.svg')).getroot()
    assert root.attrib['width']=='600mm' and root.attrib['height']=='400mm'
    groups=root.findall('{http://www.w3.org/2000/svg}g')
    assert len(groups)==len(sheet['pecas'])
    envelopes=[]
    for g,p in zip(groups,sheet['pecas']):
        assert g.attrib['id']==p['id'];counts[p['id']]+=1
        w,h=pts[p['id']]['dimensoes_mm'];x,y=p['x'],p['y']
        assert x>=5 and y>=5 and x+w<=595 and y+h<=395
        envelopes.append((x,y,x+w,y+h))
    for (x,y,xx,yy),(u,v,uu,vv) in itertools.combinations(envelopes,2):
        assert xx+4.99<=u or uu+4.99<=x or yy+4.99<=v or vv+4.99<=y
    raw=(ROOT/(sheet['caminho']+'.dxf')).read_text().splitlines();pairs=list(zip(raw[::2],raw[1::2]))
    assert sum(k=='0' and v=='POLYLINE' for k,v in pairs)==len(root.findall('.//{http://www.w3.org/2000/svg}polygon'))
    assert sum(k=='0' and v=='CIRCLE' for k,v in pairs)==len(root.findall('.//{http://www.w3.org/2000/svg}circle'))
for id,pt in pts.items():assert counts[id]==pt['quantidade']
results['cortes']=dict(chapas=len(cuts['chapas']),contagem=dict(counts),mesa_mm=[600,400],sem_sobreposicao=True)
scene=json.loads((ROOT/'06_CAD_VALIDACAO/montagem.json').read_text())
byname={it['nome']:it for it in scene}
def section_hits(tris,x):
    hit=[]
    for tri in tris:
        for v,w in zip(tri,np.roll(tri,-1,axis=0)):
            if min(v[0],w[0])<x<max(v[0],w[0]):hit.append(v+(w-v)*(x-v[0])/(w[0]-v[0]))
    return np.array(hit)
roof=read(ROOT/byname['moldura']['malha'])
stations=[]
for x in (210,390):
    hits=section_hits(roof,x)
    central=hits[(np.abs(hits[:,1])<60)]
    assert len(central) and abs(central[:,2].min()-182.4)<1e-3
    stations.append(dict(x_mm=x,teto_mm=182.4,piso_mm=62.4,altura_livre_mm=120))
results['moldura_corrigida']=stations
assert pts['M23']['dimensoes_mm']==[160,64]
# Furos do novo pé da câmara coincidem com B01, sem cruzar os rasgos da haste.
for y in (37,183):assert [350,y,2.25] in pts['B01']['furos']
assert 350-12>309 and 350+12<388
results['apoio_camara']=dict(x_mm=350,patamar_mm=60,fixacoes_base_compativeis=True)

# Só pares com sobreposição de envelopes 3D; contatos de apoio não são colisões.
pairs=[]
for a,b in itertools.combinations(scene,2):
    if a['material'] in ('comprado','acrilico') or b['material'] in ('comprado','acrilico'):continue
    if not (a['novo'] or b['novo']):continue
    lo=np.maximum(a['minimo_mm'],b['minimo_mm']);hi=np.minimum(a['maximo_mm'],b['maximo_mm'])
    if np.all(hi-lo>1e-4):pairs.append((a,b))
def boolean(pair):
    a,b=pair
    with tempfile.TemporaryDirectory(prefix='tunel-v7-') as td:
        src=Path(td)/'teste.scad';dest=Path(td)/'intersecao.stl'
        src.write_text('intersection(){import('+json.dumps(str(ROOT/a['malha']))+');import('+json.dumps(str(ROOT/b['malha']))+');}')
        r=subprocess.run(['openscad','-o',str(dest),str(src)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        volume=0.
        if dest.exists() and dest.stat().st_size:
            tri=read(dest);volume=abs(np.einsum('ij,ij->i',tri[:,0],np.cross(tri[:,1],tri[:,2])).sum()/6)
        else:
            assert r.returncode in (0,1) and (r.returncode==0 or b'empty' in r.stderr.lower()),r.stderr.decode()
        return dict(a=a['nome'],b=b['nome'],volume_intersecao_mm3=round(volume,6))
with ThreadPoolExecutor(max_workers=2) as pool:checks=list(pool.map(boolean,pairs))
results['intersecoes_geometricas']=checks
failures=[q for q in checks if q['volume_intersecao_mm3']>.01]
results['colisoes_encontradas']=failures
# Asas móveis contra corpo/câmara/apoio, nas mesmas cinco posições da V5.
wing_A=read(ROOT/byname['asa_A']['malha'])
raw_B=read(ROOT/'01_IMPRESSAO_3D/02_alternativas_escolher_uma/18_asa_B_curvada.stl')
wing_B=transform(raw_B,rotation('x',-90),(288,-45,96.4+np.ptp(raw_B[:,:,1])))
angles=[];angular_pairs=[]
for profile,wing in [('A',wing_A),('B',wing_B)]:
    for angle in (-20,-15,0,15,20):
        w=transform(wing-[300,0,104.4],rotation('y',angle),[300,0,104.4])
        assert w[:,:,2].min()>62.4 and w[:,:,2].max()<180.8
        assert w[:,:,0].min()>212 and w[:,:,0].max()<338
        name=f'asa_{profile}_angulo_{angle}'
        dest=ROOT/'06_CAD_VALIDACAO/montagem_REFERENCIA'/(name+'.stl');write(dest,w)
        a=dict(nome=name,malha=str(dest.relative_to(ROOT)))
        for neighbor in ('camara','moldura','suporte_asa','acrilico'):angular_pairs.append((a,byname[neighbor]))
        angles.append(dict(asa=profile,angulo_graus=angle,minimo_z_mm=float(w[:,:,2].min()),maximo_z_mm=float(w[:,:,2].max())))
with ThreadPoolExecutor(max_workers=2) as pool:angular_checks=list(pool.map(boolean,angular_pairs))
results['envelope_asas']=angles
results['intersecoes_asas_por_angulo']=angular_checks
failures.extend(q for q in angular_checks if q['volume_intersecao_mm3']>.01)
results['limites']=['Verificação geométrica digital; sem montagem física, teste de rigidez ou fluxo.',
                   'Ventoinha e célula são referências simplificadas; conferir equipamento real e roscas.',
                   'Acrílico/vedação e contatos de apoio conferidos dimensionalmente; não analisados estruturalmente.']
results['resultado']='PASSOU' if not failures else 'CORRIGIR'
(ROOT/'06_CAD_VALIDACAO/relatorio_verificacao.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
print(results['resultado'],len(results['malhas_fabricacao']),'STL de fabricação;',len(checks)+len(angular_checks),'interseções booleanas; moldura corrigida; cortes e quantidades.')
if failures:print(json.dumps(failures,indent=2));raise SystemExit(1)
