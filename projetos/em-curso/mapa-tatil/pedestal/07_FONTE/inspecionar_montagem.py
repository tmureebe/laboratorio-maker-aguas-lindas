from pathlib import Path
import json
import numpy as np
from shapely.geometry import Polygon, LineString, box
from shapely.ops import unary_union
from shapely.affinity import affine_transform

root=Path(__file__).resolve().parents[1]
data={}
for line in (root/'04_MODELOS_3D'/'Pedestal_MDF.scad').read_text().splitlines():
 for key in ['esp','nomes','contornos','matrizes']:
  if line.startswith(key+'='):
   data[key]=json.loads(line[len(key)+1:-1])
T=data['esp']
parts=[]
levels={0.01}
for name,rings,m in zip(data['nomes'],data['contornos'],data['matrizes']):
 g=Polygon(rings[0],rings[1:])
 m=np.array(m)
 zvalues=[]
 for ring in rings:
  p=np.array(ring)
  for n in [0,T]:
   h=np.c_[p,np.zeros(len(p))+n,np.ones(len(p))]
   zvalues.extend((h@m.T)[:,2])
 for z in zvalues:
  levels.add(round(float(z),8))
 parts.append((name,g,m,min(zvalues),max(zvalues)))
ordered=sorted(levels)
heights=sorted(set([z-.002 for z in ordered]+[z+.002 for z in ordered]+[(a+b)/2 for a,b in zip(ordered,ordered[1:])]))

def section(part,z):
 name,g,m,zmin,zmax=part
 if not zmin+1e-8 < z < zmax-1e-8:
  return None
 if abs(m[2,1]-1)<1e-8:  # Vertical 2D panel, thickness horizontal.
  v=z-m[2,3]
  line=g.intersection(LineString([(-1000,v),(2000,v)]))
  lines=[]
  if line.geom_type=='LineString': lines=[line]
  elif hasattr(line,'geoms'): lines=[p for p in line.geoms if p.geom_type=='LineString']
  shapes=[]
  for seg in lines:
   lo,_,hi,_=seg.bounds
   coords=[]
   for u,n in [(lo,0),(hi,0),(hi,T),(lo,T)]:
    q=m@np.array([u,v,n,1])
    coords.append(q[:2])
   shape=Polygon(coords)
   if shape.area>1e-9: shapes.append(shape)
  return unary_union(shapes) if shapes else None
 if abs(m[2,2]-1)<1e-8:  # Horizontal floor/diaphragm.
  return affine_transform(g,[m[0,0],m[0,1],m[1,0],m[1,1],m[0,3],m[1,3]])
 # Inclined cap: clip to the band intersected by the horizontal plane.
 sin,cos=m[2,1],m[2,2]
 lo=(z-m[2,3]-T*cos)/sin
 hi=(z-m[2,3])/sin
 band=g.intersection(box(-1000,lo,2000,hi))
 return affine_transform(band,[1,0,0,1/cos,m[0,3],m[1,3]-sin*(z-m[2,3])/cos])

collisions={}
for z in heights:
 slices=[]
 for part in parts:
  q=section(part,z)
  if q is not None and not q.is_empty:
   slices.append((part[0],q))
 for i,(an,ag) in enumerate(slices):
  ax0,ay0,ax1,ay1=ag.bounds
  for bn,bg in slices[i+1:]:
   bx0,by0,bx1,by1=bg.bounds
   if ax0>=bx1-1e-8 or bx0>=ax1-1e-8 or ay0>=by1-1e-8 or by0>=ay1-1e-8:
    continue
   area=ag.intersection(bg).area
   if area>1e-5:
    pair=an+' / '+bn
    prev=collisions.get(pair,dict(area=0))
    if area>prev['area']:
     collisions[pair]=dict(z=round(z,6),area=round(area,6))
report=dict(secoes_horizontais_inspecionadas=len(heights),pecas=len(parts),colisoes=collisions,
            metodo='Seções nos vértices, +/- 0,002 mm e ponto médio dos intervalos; não é ensaio estrutural nem prova contínua de ausência de colisões.')
(root/'05_GUIA'/'INSPECAO_MONTAGEM.json').write_text(json.dumps(report,indent=2,ensure_ascii=False))
print(json.dumps(report,indent=2,ensure_ascii=False))
