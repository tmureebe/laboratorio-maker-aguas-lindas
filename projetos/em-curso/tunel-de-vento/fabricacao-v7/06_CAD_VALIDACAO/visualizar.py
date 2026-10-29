#!/usr/bin/python3
"""Renderização com profundidade e luz; visualizador WebGL offline do mesmo STL."""
from pathlib import Path
import base64,json,math,sys
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from malhas import read
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'05_VISUALIZACAO'
scene=json.loads((ROOT/'06_CAD_VALIDACAO/montagem.json').read_text())
for it in scene:it['tris']=read(ROOT/it['malha'])
PALETTE={'MDF':np.array([191,151,100]),'impresso':np.array([29,128,151]),
         'comprado':np.array([100,112,122]),'acrilico':np.array([155,223,236])}
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def explode(it):
    name=it['nome'];dx=dy=dz=0
    if name.startswith('entrada_') or name=='colmeia':dx=-80
    if name.startswith('saida_'):dx=80
    if name in ('moldura',):dz=65
    if name=='acrilico':dz=105
    if name.startswith(('presilha_','esp_presilha')):dz=140
    if name.startswith('pe_'):dz=-20
    if name in ('U01','U02','ligacao'):dx={'U01':-30,'U02':35,'ligacao':110}[name]
    if it['grupo']=='regulador' or name=='ventoinha':
        dx={'parte_5':140,'ventoinha':175,'parte_1':210,'grade':245,'espacador_regulador':275,
            'parte_2':310,'parte_3':345,'parte_4':380}.get(name,210)
    return np.array([dx,dy,dz])

def render(name,title,subtitle,selected,exploded=False,cut=False,direction=(-1.3,-2,1.25),size=(1800,1050)):
    if '--sensor-only' in sys.argv and name!='03_camara_sensor':return
    W,H=size;direction=np.array(direction,dtype=float);direction/=np.linalg.norm(direction)
    u=np.cross([0,0,1],direction);u/=np.linalg.norm(u);v=np.cross(direction,u)
    items=[]
    for it in selected:
        tri=it['tris'].copy()
        if cut and it['nome']=='camara':tri=tri[~((tri[:,:,1]<-59).all(1)&(tri[:,:,2].max(1)>62.4001))]
        if exploded:tri+=explode(it)
        items.append((it,tri))
    allv=np.concatenate([t.reshape(-1,3) for _,t in items]);plane=allv@np.column_stack([u,v])
    lo=plane.min(0);hi=plane.max(0);scale=min((W-130)/(hi[0]-lo[0]),(H-255)/(hi[1]-lo[1]));center=(lo+hi)/2
    canvas=np.full((H,W,3),247.,dtype=np.float32);depth=np.full((H,W),-np.inf,dtype=np.float32)
    light=np.array([-.35,-.5,1.]);light/=np.linalg.norm(light)
    def raster(it,tris,transparent=False):
        p=tris@np.column_stack([u,v]);p[:,:,0]=(p[:,:,0]-center[0])*scale+W/2
        p[:,:,1]=-(p[:,:,1]-center[1])*scale+H/2+10
        z=tris@direction
        normals=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);normals/=np.maximum(np.linalg.norm(normals,axis=1),1e-12)[:,None]
        shade=.62+.32*np.maximum(normals@light,0)+.08*np.maximum(normals@direction,0)
        base=PALETTE[it['material']].astype(float)
        if '_lamina_' in it['nome'] and int(it['nome'][-1])%2==0:base*=.93
        for j,t in enumerate(p):
            if normals[j]@direction<=0:continue
            minx=max(0,int(np.floor(t[:,0].min())));maxx=min(W-1,int(np.ceil(t[:,0].max())))
            miny=max(115,int(np.floor(t[:,1].min())));maxy=min(H-105,int(np.ceil(t[:,1].max())))
            if maxx<minx or maxy<miny:continue
            x,y=np.meshgrid(np.arange(minx,maxx+1)+.5,np.arange(miny,maxy+1)+.5)
            den=(t[1,1]-t[2,1])*(t[0,0]-t[2,0])+(t[2,0]-t[1,0])*(t[0,1]-t[2,1])
            if abs(den)<1e-7:continue
            aa=((t[1,1]-t[2,1])*(x-t[2,0])+(t[2,0]-t[1,0])*(y-t[2,1]))/den
            bb=((t[2,1]-t[0,1])*(x-t[2,0])+(t[0,0]-t[2,0])*(y-t[2,1]))/den
            cc=1-aa-bb;zz=aa*z[j,0]+bb*z[j,1]+cc*z[j,2]
            region=depth[miny:maxy+1,minx:maxx+1];mask=(aa>=-1e-6)&(bb>=-1e-6)&(cc>=-1e-6)&(zz>region+1e-5)
            pixels=canvas[miny:maxy+1,minx:maxx+1]
            if transparent:pixels[mask]=pixels[mask]*.73+(base*shade[j])*.27
            else:
                pixels[mask]=base*shade[j];region[mask]=zz[mask]
    for it,tri in items:
        if it['material']!='acrilico':raster(it,tri)
    for it,tri in items:
        if it['material']=='acrilico':raster(it,tri,True)
    # Contorno discreto nas descontinuidades, sem arestas de triangulação.
    mask=np.isfinite(depth);edge=np.zeros_like(mask)
    for dy,dx in ((1,0),(0,1)):
        diff=np.abs(np.where(mask,depth,0)-np.roll(np.where(mask,depth,0),(dy,dx),(0,1)))
        edge|=mask&((diff>4)|~np.roll(mask,(dy,dx),(0,1)))
    canvas[edge]*=.72
    image=Image.fromarray(np.uint8(np.clip(canvas,0,255)));draw=ImageDraw.Draw(image)
    draw.text((65,30),title,font=ImageFont.truetype(FONT,36),fill='#164956')
    draw.text((65,82),subtitle,font=ImageFont.truetype(FONT,20),fill='#49616a')
    x=65
    for label,color in [('MDF',PALETTE['MDF']),('Impressão 3D',PALETTE['impresso']),('Comprados',PALETTE['comprado']),('Acrílico',PALETTE['acrilico'])]:
        draw.rectangle((x,H-71,x+20,H-51),fill=tuple(map(int,color)))
        draw.text((x+30,H-76),label,font=ImageFont.truetype(FONT,19),fill='#314a55');x+=260
    draw.text((65,H-35),'Modelo digital. Referências comerciais simplificadas; ferragens não representadas.',font=ImageFont.truetype(FONT,15),fill='#657984')
    image.save(OUT/(name+'.png'));print('Vista:',name,flush=True)

if '--html-only' not in sys.argv:
    render('01_conjunto_completo','Túnel híbrido · V7','Corpo de 600 mm · passagem 120 × 120 mm · seis apoios · base de 750 × 220 mm',scene)
    render('02_explodido','Sequência de montagem','Vista explodida esquemática: deslocamentos servem para identificar as peças.',scene,True,direction=(-.6,-2,1.5),size=(2100,1200))
    sensor=[it for it in scene if it['grupo'] in ('sensor','camara') or it['nome']=='celula']
    render('03_camara_sensor','Câmara e medição','Parede frontal e tampa omitidas nesta vista para mostrar a célula e a liberdade das hastes.',sensor,cut=True,direction=(-1,-2,1.1),size=(1600,1150))
    window=[it for it in scene if it['grupo'] in ('camara','janela')]
    render('04_janela_explodida','Fechamento da janela','Câmara → moldura V7 → vedação fina → acrílico → espaçadores e presilhas.',window,True,direction=(-1,-2,1.6),size=(1600,1200))
    head=[it for it in scene if it['grupo']=='regulador' or it['nome'] in ('ligacao','ventoinha')]
    render('08_ventoinha_regulador','Ventoinha e regulador','Ligação → parte 5 → ventoinha → parte 1 → grade → espaçador → parte 2 → disco → alavanca',head,True,direction=(1,-2,1.4),size=(2000,1100))
    

# Um HTML local e autossuficiente; sem CDN, servidor, rede ou instalação.
arrays=[];groups=[];start=0
for it in scene:
    tri=it['tris'];normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);normal/=np.maximum(np.linalg.norm(normal,axis=1),1e-12)[:,None]
    data=np.concatenate([((tri-[375,0,95])/375).reshape(-1,3),np.repeat(normal,3,axis=0),
                         np.tile(PALETTE[it['material']]/255,(len(tri)*3,1))],axis=1).astype('<f4')
    groups.append(dict(name=it['nome'],group=it['grupo'],material=it['material'],start=start,count=len(data),explode=(explode(it)/375).tolist()))
    start+=len(data);arrays.append(data)
encoded=base64.b64encode(np.concatenate(arrays).tobytes()).decode()
template=Path(__file__).with_name('visualizador_template.html').read_text()
(OUT/'ABRIR_VISUALIZADOR_3D.html').write_text(template.replace('__DATA__',encoded).replace('__GROUPS__',json.dumps(groups,ensure_ascii=False)))
print('Visualizador 3D offline criado.')
