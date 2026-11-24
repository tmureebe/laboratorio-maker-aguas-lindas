"""Blender --background --factory-startup --python scripts/gerar_modelo.py -- [--config PATH] [--sem-render]
Geometria em milimetros; nao ha displacement de shader nem modificadores pendentes.
"""
import bpy, numpy as np, json, sys, argparse, math, os
from pathlib import Path
from mathutils import Vector
ROOT = Path(__file__).resolve().parents[1]
ap = argparse.ArgumentParser()
ap.add_argument('--config', type=Path, default=ROOT/'configuracao/modelo.json')
ap.add_argument('--sem-render', action='store_true')
args=ap.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
p=json.loads(args.config.read_text()); a=p['anatomia']; t=p['texturas']; out=ROOT/'saida'
(out/'renders').mkdir(parents=True,exist_ok=True); (out/'validacao').mkdir(exist_ok=True)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
bpy.context.preferences.filepaths.save_version=0
scene=bpy.context.scene; scene.unit_settings.system='METRIC'; scene.unit_settings.scale_length=0.001

def smooth(v):
    v=np.clip(v,0,1); return v*v*(3-2*v)
def gauss(x,y,cx,cy,rx,ry): return np.exp(-((x-cx)/rx)**2-((y-cy)/ry)**2)
L=a['comprimento_mm']; W=a['largura_proximal_mm']; step=p['malha']['passo_maximo_mm']
assert 0.12<=step<=0.4 and 180<=L<=230 and 65<=W<=105
assert 1<=a['lesao_profundidade_mm']<=4 and 0<=a['borda_irregularidade']<=0.16
ny=math.ceil(L/step)+1; nx=math.ceil(W*1.25/step)+1
u=np.linspace(-1,1,nx); y=np.linspace(-L/2,L/2,ny); yy=y*210/L
# Proximal calf taper, ankle waist, distal truncated hindfoot, viewed medially.
width=W*(0.78+0.22*smooth((yy+25)/95)+0.24*np.exp(-((yy+100)/20)**2))
center=8*np.exp(-((yy+105)/24)**2)*W/84
X=center[:,None]+width[:,None]*u[None,:]/2; Y=np.broadcast_to(y[:,None],X.shape)
U=np.broadcast_to(u,X.shape)
base=a['base_mm']; H=a['altura_relevo_mm']
Z0=base+H*np.maximum(0,1-U*U)**0.72*(0.83+0.17*smooth((Y+30*L/210)/(90*L/210)))
# Medial malleolus, tibial contour, Achilles/hindfoot transition; all smooth and integral.
Z0+=6.8*gauss(X,Y,-9*W/84,-64*L/210,12*W/84,16*L/210)*(1-U*U)
Z0+=2.0*gauss(X,Y,14*W/84,37*L/210,9*W/84,80*L/210)*(1-U*U)
Z0-=1.8*gauss(X,Y,-24*W/84,-65*L/210,9*W/84,27*L/210)*(1-U*U)
cx,cy=a['lesao_centro_mm']; dx=X-cx; dy=Y-cy
rx=a['lesao_largura_mm']/2; ry=a['lesao_comprimento_mm']/2
angle=np.arctan2(dy/ry,dx/rx)
radius=1+a['borda_irregularidade']*(0.63*np.sin(3*angle+0.4)+0.32*np.sin(5*angle-1.1)+0.24*np.cos(9*angle+0.8))
rho=np.sqrt((dx/rx)**2+(dy/ry)**2)/radius
edge=(1-rho)*rx; bed=smooth(edge/a['transicao_borda_mm']); peri=np.exp(-((rho-1.13)/0.26)**2)*(1-bed)
assert np.all(bed[:,[0,-1]]==0) and np.all(bed[[0,-1]]==0), 'Lesao fora da superficie'
fib=np.zeros_like(X)
for fx,fy,fw,fh in t['fibrina_ilhas']:
    fib=np.maximum(fib,gauss(dx+2.1*np.sin(dy*.26)+.8*np.sin(dy*.71),dy+2.8*np.sin(dx*.31),fx,fy,fw,fh))
fib=smooth((fib+0.055*np.sin(dx*.7+np.sin(dy*.25))-0.32)/0.35)*bed
rng=np.random.default_rng(p['malha']['semente']); gran=np.zeros_like(X)
# Jittered, scale-varied rounded nodules, with clustered amplitude. No independent solids.
s=t['granulacao_espacamento_mm']; diam=t['granulacao_diametro_mm']
# Poisson-like rejection avoids visible rows, with clustered size/height variation.
centres=[]
for attempt in range(6000):
    gx=rng.uniform(-rx*1.2,rx*1.2); gy=rng.uniform(-ry*1.2,ry*1.2)
    spacing=s*(.64+.12*np.sin(gx*.15+gy*.11))
    if any((gx-qx)**2+(gy-qy)**2<spacing**2 for qx,qy in centres): continue
    centres.append((gx,gy))
    px=cx+gx; py=cy+gy
    r=rng.uniform(*diam)/2; height=rng.uniform(.55,1.05)*(.88+.12*np.cos(gy*.2+gx*.3))
    ids=np.where((y>py-3*r)&(y<py+3*r))[0]
    if len(ids):
        sl=slice(ids[0],ids[-1]+1)
        bump=np.exp(-2*((X[sl]-px)**2+(Y[sl]-py)**2)/r**2)
        gran[sl]+=height*bump
# Non-periodic perilesional relief: broad patches and smaller rounded elevations.
rough=np.zeros_like(X)
for i in range(500):
    px=cx+rng.uniform(-rx*1.6,rx*1.6); py=cy+rng.uniform(-ry*1.5,ry*1.5)
    sx=rng.uniform(.8,2.8); sy=rng.uniform(1.0,4.0)
    ids=np.where((y>py-3*sy)&(y<py+3*sy))[0]
    if len(ids):
        sl=slice(ids[0],ids[-1]+1)
        rough[sl]+=rng.uniform(-.35,1.0)*gauss(X[sl],Y[sl],px,py,sx,sy)
rough=np.tanh(rough)
wrinkle=np.exp(-(np.sin((dx+.8*np.sin(dy*.25))*math.pi/4.8)/(t['fibrina_prega_largura_mm']/3.33))**2)
fibrin=t['fibrina_altura_mm']*(.35+.65*wrinkle)
# Smooth taper of ALL tactile fields at the cut perimeter.
fade=smooth((1-np.abs(U))/.12)*smooth((L/2-np.abs(Y))/3)
textures=bed*((1-fib)*t['granulacao_altura_mm']*gran+fib*fibrin)+peri*t['pele_perilesional_altura_mm']*rough
skin=(1-bed)*(1-peri)*t['pele_integra_altura_mm']*np.sin(X*1.6+np.sin(Y*.8))*np.sin(Y*1.3)
# Counterclockwise perimeter in XY.
boundary=np.concatenate([np.arange(nx),np.arange(2*nx-1,ny*nx,nx),np.arange(ny*nx-2,(ny-1)*nx-1,-1),np.arange((ny-2)*nx,0,-nx)])
idx=np.arange((ny-1)*(nx-1)); row=idx//(nx-1); col=idx%(nx-1); v=row*nx+col
ftop=np.concatenate([np.stack([v,v+1,v+nx+1],1),np.stack([v,v+nx+1,v+nx],1)])
nb=len(boundary); nt=X.size
# Strip triangulation preserves every perimeter vertex without collinear cap triangles.
bmap={int(v):nt+i for i,v in enumerate(boundary)}
cap=[]
for j in range(ny-1):
    l0=j*nx; r0=l0+nx-1; l1=l0+nx; r1=l1+nx-1
    if j==0:
        cap.extend([(l0+i,l0+i+1,l1) for i in range(nx-1)])
        cap.append((r0,r1,l1))
    elif j==ny-2:
        cap.append((l0,r0,r1))
        cap.extend([(l0,l1+i+1,l1+i) for i in range(nx-1)])
    else:
        cap.extend([(l0,r0,r1),(l0,r1,l1)])
fbottom=np.array([[bmap[i] for i in reversed(tri)] for tri in cap],dtype=np.int32)
k=np.arange(nb); kn=(k+1)%nb
fsides=np.concatenate([np.stack([boundary[k],nt+k,nt+kn],1),np.stack([boundary[k],nt+kn,boundary[kn]],1)])
faces=np.concatenate([ftop,fsides,fbottom]).astype(np.int32)
# Clinical colors interpolate continuously; geometry is independently exported in STL.
colors=np.empty((*X.shape,4)); colors[:]=[.43,.245,.125,1]
mottle=.04*np.sin(X*.13+np.cos(Y*.09))*np.sin(Y*.19)
colors[:,:,:3]+=mottle[:,:,None]
def mix(col,weight):
    colors[:,:,:3] *= (1-weight[:,:,None]); colors[:,:,:3] += np.array(col)*weight[:,:,None]
mix([.22,.095,.060],np.clip(peri*.85+.15*np.exp(-((rho-1.1)/.55)**2),0,1))
mix([.52,.22,.17],smooth((edge+1)/2.6))
mix([.43,.035,.035],bed)
mix([.65,.48,.19],fib*.94)
colors[:,:,:3]+=((gran*.04)*bed)[:,:,None]
mat=bpy.data.materials.new('Tecidos • cor clinica por vertice'); mat.use_nodes=True
bs=mat.node_tree.nodes.get('Principled BSDF'); bs.inputs['Roughness'].default_value=.62
attr=mat.node_tree.nodes.new('ShaderNodeVertexColor'); attr.layer_name='CorClinica'
mat.node_tree.links.new(attr.outputs['Color'],bs.inputs['Base Color'])
mono=bpy.data.materials.new('PLA monocromatico • marfim'); mono.diffuse_color=(.65,.61,.49,1); mono.use_nodes=True
mono.node_tree.nodes.get('Principled BSDF').inputs['Base Color'].default_value=(.65,.61,.49,1)
mono.node_tree.nodes.get('Principled BSDF').inputs['Roughness'].default_value=.72
objects=[]; reports={}

def stl_write(path,verts,faces):
    tri=verts[faces].astype('<f4'); normal=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); normal/=np.linalg.norm(normal,axis=1)[:,None]
    data=np.zeros(len(faces),dtype=[('n','<f4',3),('v','<f4',(3,3)),('a','<u2')]); data['n']=normal; data['v']=tri
    with open(path,'wb') as f: f.write(b'Ulcer venosa; millimeters; integral relief'.ljust(80,b' ')); f.write(np.uint32(len(data)).tobytes()); data.tofile(f)

for name,scale in p['ampliacao_tatil'].items():
    Z=Z0-a['lesao_profundidade_mm']*bed+fade*(scale*textures+skin)
    verts=np.concatenate([np.stack([X.ravel(),Y.ravel(),Z.ravel()],1),np.stack([X.ravel()[boundary],Y.ravel()[boundary],np.zeros(nb)],1)]).astype(np.float32)
    mesh=bpy.data.meshes.new('Superficie integrada '+name); mesh.from_pydata(verts.tolist(),[],faces.tolist()); mesh.update()
    obj=bpy.data.objects.new('Ulcera venosa • '+name,mesh); scene.collection.objects.link(obj); objects.append(obj)
    obj['unidade']='mm'; obj['versao']=name; obj['escala_tatil']=scale
    obj.data.materials.append(mat)
    ca=mesh.color_attributes.new(name='CorClinica',type='FLOAT_COLOR',domain='POINT')
    bottom_col=np.tile([.35,.19,.09,1],(nb,1)); ca.data.foreach_set('color',np.concatenate([colors.reshape(-1,4),bottom_col]).astype(np.float32).ravel())
    # Top smooth shading only; the mesh itself retains all relief.
    smooth_flags=np.zeros(len(faces),dtype=bool); smooth_flags[:len(ftop)]=True; mesh.polygons.foreach_set('use_smooth',smooth_flags)
    stl_write(out/('ulcera_venosa_'+name+'.stl'),verts,faces)
    np.savez_compressed(out/'validacao'/('geometria_'+name+'.npz'),vertices=verts,faces=faces,top_faces=len(ftop),base_surface=Z0,bed=bed,heights=Z,grid_shape=[ny,nx],colors=colors)
    obj.hide_render=name!='tatil'; obj.hide_set(name!='tatil')
    print('GERADO',name,verts.shape,faces.shape,flush=True)
(out/'parametros_utilizados.json').write_text(json.dumps(p,indent=2,ensure_ascii=False))
# Render studio with geometry in mm. Background and lighting excluded from STL.
scene.render.engine='CYCLES'; scene.cycles.samples=p['render']['amostras']; scene.cycles.use_denoising=True
scene.render.resolution_x=p['render']['resolucao']; scene.render.resolution_y=p['render']['resolucao']; scene.render.resolution_percentage=100
scene.world.color=(.22,.22,.22); scene.view_settings.view_transform='AgX'
scene.render.image_settings.file_format='PNG'
for name,loc,power,size in [('Principal',(-110,-20,190),650000,140),('Preenchimento',(100,70,150),420000,110),('Recorte',(-20,150,90),350000,90)]:
    data=bpy.data.lights.new(name,'AREA'); data.energy=power*.5; data.shape='DISK'; data.size=size
    ob=bpy.data.objects.new(name,data); scene.collection.objects.link(ob); ob.location=loc; ob.rotation_euler=(Vector((0,0,15))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.25)); floor=bpy.context.object; floor.name='Cenario • nao exportar'
fm=bpy.data.materials.new('Fundo neutro'); fm.diffuse_color=(.11,.14,.16,1); floor.data.materials.append(fm)
camdata=bpy.data.cameras.new('Camera'); cam=bpy.data.objects.new('Camera',camdata); scene.collection.objects.link(cam); scene.camera=cam; camdata.type='ORTHO'
def camera(loc,target,scale):
    cam.location=loc; cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.ortho_scale=scale
camera((155,-230,290),(0,0,12),250)
# Save colored scene with tactile mesh visible and anatomical alternative hidden.
bpy.context.view_layer.objects.active=objects[1]; bpy.ops.object.select_all(action='DESELECT'); objects[1].select_set(True)
bpy.ops.wm.save_as_mainfile(filepath=str(out/'ulcera_venosa.blend'))
if not args.sem_render:
    shots=[('01_perspectiva_clinica',(155,-230,290),(0,0,12),250,False),('02_vista_medial',(0,0,330),(0,0,12),235,False),('03_detalhe_monocromatico',(85,-100,180),(2,-7,28),105,True),('04_perfil_monocromatico',(-175,-200,130),(0,0,12),245,True)]
    for name,loc,target,zoom,is_mono in shots:
        camera(loc,target,zoom); objects[1].data.materials[0]=mono if is_mono else mat
        scene.render.filepath=str(out/'renders'/(name+'.png')); bpy.ops.render.render(write_still=True)
print('CONCLUIDO',flush=True)
# Some host audio backends stall normal Blender shutdown; data already flushed.
sys.stdout.flush(); os._exit(0)
