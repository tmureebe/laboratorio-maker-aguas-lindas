"""Medicoes independentes sobre as malhas exportadas; execucao apos validar_modelo.py."""
from pathlib import Path
import json, hashlib, subprocess, tempfile
import numpy as np
from validar_modelo import ler_stl
P=Path(__file__).resolve().parent

def componentes(t, nome):
 # Os pares fornecidos nao cruzam o plano X de separacao.
 limite=14 if nome=="teste_aletas" else 0
 return [t[t[:,:,0].mean(axis=1)<limite],t[t[:,:,0].mean(axis=1)>limite]]

def corte(t,z,centro=(0,0)):
 seg=[]
 for tri in t:
  pts=[]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   if (a[2]<z<b[2]) or (b[2]<z<a[2]):
    pts.append((a+(b-a)*(z-a[2])/(b[2]-a[2]))[:2]-centro)
  if len(pts)==2:seg.append(pts)
 return np.array(seg)

def diametros(seg,ri,ro):
 m=np.linalg.norm(seg.mean(axis=1),axis=1)
 s=seg[(m>ri)&(m<ro)]
 assert len(s)>5
 a,b=s[:,0],s[:,1];ab=b-a
 u=np.clip(-np.einsum('ij,ij->i',a,ab)/np.einsum('ij,ij->i',ab,ab),0,1)
 v=a+u[:,None]*ab
 return [round(float(2*np.linalg.norm(v,axis=1).min()),5),round(float(2*np.linalg.norm(s,axis=2).max()),5)]

if __name__=='__main__':
 r={};parts={}
 for nome in ['teste_baioneta','teste_tampa','teste_aletas']:
  t=ler_stl(P/'STL'/f'{nome}.stl');a,b=componentes(t,nome)
  parts[nome]=[a,b]
  r[nome]=[{'min_mm':v.min(axis=(0,1)).round(5).tolist(),'max_mm':v.max(axis=(0,1)).round(5).tolist(),'dimensoes_mm':np.ptp(v,axis=(0,1)).round(5).tolist()} for v in [a,b]]
 f,m=parts['teste_baioneta']
 r['soquete_diametro_livre_mm']=diametros(corte(f,16,(-40,0)),20,23)
 r['tubo_diametro_externo_mm']=diametros(corte(m,8,(40,0)),20,22)
 r['tubo_diametro_interno_mm']=diametros(corte(m,8,(40,0)),18,20)
 f,m=parts['teste_aletas']
 r['furo_aletas_diametro_livre_mm']=diametros(corte(f,1),3,4)
 t=ler_stl(P/'STL/portinha.stl')
 r['portinha_aba_mm']=np.ptp(corte(t,4.5).reshape(-1,2),axis=0).round(5).tolist()
 r['portinha_ressaltos_mm']=np.ptp(corte(t,3.5).reshape(-1,2),axis=0).round(5).tolist()
 assert np.allclose(r['portinha_aba_mm'],[29.6,19.6],atol=1e-4)
 assert np.allclose(r['portinha_ressaltos_mm'],[30.3,20.3],atol=1e-4)
 # Amplitude maxima que a cabeca exige ao atravessar o furo, sem simular elasticidade.
 fonte=(P/'estacao_integrada.scad').read_text().split('validar() {\n    if (visualizacao')[0]
 with tempfile.TemporaryDirectory(dir='/tmp') as tmp:
  scad=Path(tmp)/'pino.scad';stl=Path(tmp)/'pino.stl'
  scad.write_text(fonte+'\npino_bipartido();\n')
  q=subprocess.run(['openscad','--export-format','binstl','-o',str(stl),str(scad)],capture_output=True,text=True)
  assert q.returncode==0,q.stderr
  v=ler_stl(stl).reshape(-1,3);v=v[(v[:,2]>=1.2-1e-4)&(v[:,2]<=1.7+1e-4)]
  assert len(v)>10
  v[:,0]-=.5*np.sign(v[:,0]);raio=float(np.linalg.norm(v[:,:2],axis=1).max())
  assert raio<=3.5+1e-5
  r['cabeca_aletas_comprimida']={'recuo_por_metade_mm':.5,'raio_maximo_mm':round(raio,5),'fenda_restante_mm':.6,'nota':'Conferencia do contorno, sem simulacao da flexao ou da resistencia do material.'}
 assert r['soquete_diametro_livre_mm'][0]>=42.5999
 assert r['tubo_diametro_externo_mm'][1]<=42.0001
 assert abs(r['teste_tampa'][0]['dimensoes_mm'][2]-16)<.0001
 assert r['furo_aletas_diametro_livre_mm'][0]>=6.9999
 r['parametros_de_montagem_mm']={'vao_caixa':[114,74],'saia_tampa':[113.4,73.4],'folga_por_lado_tampa':.3,'gancho_janela_lateral_por_lado':.5,'gancho_janela_vertical_inferior':.3,'gancho_janela_vertical_superior':.4,'deflexao_geometrica_gancho_para_entrada':1.2,'baioneta_folga_vertical_inferior_em_giro':.3,'baioneta_folga_vertical_superior_em_giro':.3,'baioneta_assento_final_folga_sob_pino':.3,'altura_conjunto':195.4}
 r['sha256_scad']=hashlib.sha256((P/'estacao_integrada.scad').read_bytes()).hexdigest()
 r['sha256_stl']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted((P/'STL').glob('*.stl'))}
 (P/'auditoria_medidas.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(r,ensure_ascii=False,indent=2))
