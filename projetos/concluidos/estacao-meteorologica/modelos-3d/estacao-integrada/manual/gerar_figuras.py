from pathlib import Path
import sys
import numpy as np
from PIL import Image
BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE))
from gerar_previas import rasterizar, malha, RX
OUT=Path(__file__).parent/'figuras'
for nome in ['teste_baioneta','teste_tampa','teste_aletas']:
 t=malha(nome)
 limite=14 if nome=='teste_aletas' else 0
 a=t[t[:,:,0].mean(axis=1)<limite];b=t[t[:,:,0].mean(axis=1)>limite]
 Image.fromarray(rasterizar([(a,'#64A6AF'),(b,'#E8AC67')],1300,470,32,-90)).save(OUT/f'{nome}.png')
 if nome=='teste_baioneta':
  femea=(a+[40,0,0])@RX+[0,0,3]
  macho=(b-[40,0,0])@RX+[0,0,6]
  for label,ang,gap in [('alinhar',0,18),('girar',0,1.2),('travado',30,0)]:
   r=np.deg2rad(ang); rz=np.array([[np.cos(r),-np.sin(r),0],[np.sin(r),np.cos(r),0],[0,0,1]])
   Image.fromarray(rasterizar([(femea,'#64A6AF'),(macho@rz.T+[0,0,gap],'#E8AC67')],700,650,22,-75)).save(OUT/f'baioneta_{label}.png')
 elif nome=='teste_tampa':
  femea=a+[20,0,0]
  macho=(b-[20,0,3])@RX+[0,-.3,16]
  Image.fromarray(rasterizar([(femea,'#64A6AF'),(macho,'#E8AC67')],700,600,22,-60)).save(OUT/'tampa_montada.png')
 else:
  femea=(a-[0,0,22.4])@RX
  macho=(b-[28,0,22.4])@RX+[0,0,18]
  Image.fromarray(rasterizar([(femea,'#64A6AF'),(macho+[0,0,12],'#E8AC67')],700,650,18,-75)).save(OUT/'aletas_alinhar.png')
