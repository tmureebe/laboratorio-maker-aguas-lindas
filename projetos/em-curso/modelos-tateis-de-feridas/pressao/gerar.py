"""Executar no Blender. Coordenadas em mm. Y positivo aponta para a panturrilha."""
import json
import math
import sys
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector

PASTA = Path(__file__).resolve().parent
sys.path.insert(0, str(PASTA.parent / 'scripts'))
from exportar_ply import exportar_ply

SAIDA = PASTA / 'saida'
for pasta in ('renders', 'validacao'):
    (SAIDA / pasta).mkdir(parents=True, exist_ok=True)
config = json.loads((PASTA / 'parametros.json').read_text())
a, textura = config['anatomia'], config['texturas']

def suave(t):
    t = np.clip(t, 0, 1)
    return t*t*(3-2*t)

def sino(x, y, rx, ry):
    return np.exp(-(x/rx)**2 - (y/ry)**2)

# Vista posterior: ponta distal arredondada, coxim do calcâneo, fossas laterais
# ao tendão de Aquiles e maléolos em alturas distintas.
L, W = a['comprimento_mm'], a['largura_mm']
passo = config['malha']['passo_mm']
assert L > 0 and W > 0 and 0.15 <= passo <= 0.45
ny, nx = math.ceil(L/passo)+1, math.ceil(W/passo)+1
longitudinal = np.linspace(0, 1, ny)[:,None]
u = np.linspace(-1, 1, nx)[None,:]
s = np.broadcast_to(longitudinal, (ny,nx))
casco = np.sqrt(1-np.clip(1-longitudinal/.21,0,1)**2 + .001)
largura = W*(.66+.25*np.exp(-((longitudinal-.19)/.15)**2)+.14*np.exp(-((longitudinal-.39)/.075)**2)+.34*suave((longitudinal-.45)/.55))
X = u*casco*largura/2 + W*.024*np.sin(2*np.pi*longitudinal)
Y = (s-.5)*L
perfil = np.maximum(0,1-u*u)**.64
posterior = .58 + .39*np.exp(-((s-.17)/.15)**2) + .28*suave((s-.55)/.45)
Z0 = a['base_mm'] + a['altura_mm']*perfil*casco*posterior
Z0 += perfil*(6.8*sino(X/W-.015,s-.48,.115,.23)
              + 7.0*sino(X/W+.345,s-.345,.135,.073)
              + 6.0*sino(X/W-.35,s-.395,.132,.072))
Z0 -= perfil*(2.2*sino(X/W+.17,s-.39,.09,.1)+2.1*sino(X/W-.17,s-.41,.09,.105))
centro_x, centro_y = a['centro_lesao_fracao']
dx = X-centro_x*W
dy = Y-(centro_y-.5)*L
rx, ry = a['largura_lesao_mm']/2, a['comprimento_lesao_mm']/2
angulo = np.arctan2(dy/ry, dx/rx)
contorno = 1+a['irregularidade_borda']*(.7*np.sin(3*angulo-.5)+.3*np.sin(5*angulo)+.17*np.cos(9*angulo+.6))
dist = (1-np.hypot(dx/rx,dy/ry)/contorno)*min(rx,ry)  # positivo dentro
assert max(dist[[0,-1]].max(),dist[:,[0,-1]].max()) < -4, 'Lesão excede o coxim'
escara = suave((dist-.15)/a['transicao_mm'])
borda = np.exp(-((dist+.45)/1.55)**2)*(.6+.4*suave(np.sin(angulo*2+.7)))
halo = np.exp(-((dist+2.3)/(3.7+.9*np.cos(angulo)))**2)*(1-escara)
# Superfície compacta com pequenas ondulações, sulcos interrompidos e
# variações largas sobrepostas. Nenhuma lâmina ou lasca solta.
rng = np.random.default_rng(config['malha']['semente'])
estrutura = np.zeros_like(X)
for _ in range(60):
    gx, gy = rng.uniform(-rx,rx), rng.uniform(-ry,ry)
    estrutura += rng.uniform(-.6,.9)*sino(dx-gx,dy-gy,rng.uniform(1.7,4.8),rng.uniform(2.3,6))
estrutura = np.tanh(estrutura)
sulcos = np.zeros_like(X)
for gx, gy, inclinacao, ext in [(-8,1,.3,10),(3,-4,-.44,7),(4,8,.18,7),(-3,-11,.6,5),(12,2,.5,6)]:
    curvatura = dx-gx-inclinacao*(dy-gy)-.8*np.sin((dy-gy)/2.7)
    sulcos = np.maximum(sulcos,sino(curvatura,dy-gy,textura['largura_sulcos_mm']/1.665,ext))
ondulacao = .5*np.sin(dx*.62+np.sin(dy*.32))+.5*np.cos(dy*.84+.25*dx)
relevo = (escara*textura['altura_escara_mm']*(.7*estrutura-.95*sulcos)
          + borda*textura['altura_borda_mm'] + halo*textura['rugosidade_perilesional_mm']*ondulacao)
pele = textura['rugosidade_pele_mm']*np.sin(.86*X+.4*np.sin(Y*.22))*np.sin(Y*.94)
# Campo de cor em RGB linear, incluindo variação lenta de tom na placa escura.
cores = np.empty((ny,nx,4)); cores[:] = [.48,.30,.215,1]
cores[:,:,:3] += (.014*np.sin(.18*X+.12*Y)*np.cos(.16*Y))[:,:,None]
def misturar(cor, peso):
    peso = np.clip(peso,0,1)[:,:,None]
    cores[:,:,:3] = cores[:,:,:3]*(1-peso)+cor*peso
misturar([.40,.135,.125],np.exp(-((dist+2)/5.5)**2)*(.7+.2*np.cos(angulo)))
misturar([.61,.43,.32],borda*.85)
tom = (.5+.18*estrutura+.20*np.sin(.18*dx+.07*dy)-.20*sulcos)[:,:,None]
misturar(np.array([.021,.012,.009])+tom*np.array([.054,.029,.015]),suave((dist+.15)/1.35))

# Topo triangulado e base em faixas. As duas tampas usam o mesmo perímetro.
ids = np.arange(nx*ny).reshape(ny,nx)
v = ids[:-1,:-1].ravel()
ftop = np.vstack((np.column_stack((v,v+1,v+nx+1)), np.column_stack((v,v+nx+1,v+nx))))
cont = np.r_[ids[0,:],ids[1:,-1],ids[-1,-2::-1],ids[-2:0:-1,0]]
base_ids = np.arange(len(cont))+ids.size
proximo = np.roll(base_ids,-1)
lados = np.vstack((np.column_stack((cont,base_ids,proximo)),
                   np.column_stack((cont,proximo,np.roll(cont,-1)))))
mapa = dict(zip(cont,base_ids))
tampa = []
for j in range(ny-1):
    a0,b0 = ids[j,[0,-1]]
    a1,b1 = ids[j+1,[0,-1]]
    if j==0:
        tampa.extend(zip(ids[j,:-1],ids[j,1:],np.full(nx-1,a1)))
        tampa.append((b0,b1,a1))
    elif j==ny-2:
        tampa.append((a0,b0,b1))
        tampa.extend(zip(np.full(nx-1,a0),ids[-1,1:],ids[-1,:-1]))
    else:
        tampa.extend([(a0,b0,b1),(a0,b1,a1)])
faces = np.vstack((ftop,lados,[[mapa[i] for i in reversed(face)] for face in tampa])).astype(np.int32)

def escrever_stl(arquivo, vertices):
    triangulos = vertices[faces]
    normais = np.cross(triangulos[:,1]-triangulos[:,0], triangulos[:,2]-triangulos[:,0])
    normais /= np.linalg.norm(normais,axis=1)[:,None]
    registros = np.zeros(len(faces), dtype=[('normal','<f4',3),('tri','<f4',(3,3)),('atributo','<u2')])
    registros['normal'], registros['tri'] = normais, triangulos
    with arquivo.open('wb') as f:
        f.write(b'Calcaneo - lesao por pressao - mm'.ljust(80,b' '))
        f.write(len(faces).to_bytes(4,'little'))
        registros.tofile(f)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = .001
bpy.context.preferences.filepaths.save_version = 0

def material(nome, rgb, rugosidade):
    mat = bpy.data.materials.new(nome)
    mat.diffuse_color = (*rgb,1)
    mat.use_nodes = True
    bs = mat.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*rgb,1)
    bs.inputs['Roughness'].default_value = rugosidade
    return mat, bs

clinico, shader = material('Pele, borda e escara',(.5,.27,.18),.81)
atributo = clinico.node_tree.nodes.new('ShaderNodeVertexColor')
atributo.layer_name = 'CorClinica'
clinico.node_tree.links.new(atributo.outputs['Color'],shader.inputs['Base Color'])
marfim, _ = material('PLA marfim',(.58,.53,.40),.82)
objetos = {}
for nome, ganho in config['ampliacao_tatil'].items():
    Z = Z0-a['rebaixo_visivel_mm']*escara + ganho*relevo + pele*(1-escara)*perfil*casco
    topo = np.column_stack((X.ravel(),Y.ravel(),Z.ravel()))
    base = topo[cont].copy(); base[:,2]=0
    vertices = np.vstack((topo,base)).astype(np.float32)
    assert vertices[:ids.size,2].min()>2, 'Pele cruza a face de apoio'
    escrever_stl(SAIDA/f'pressao_calcaneo_{nome}.stl',vertices)
    dados = SAIDA/'validacao'/f'geometria_{nome}.npz'
    np.savez_compressed(dados,vertices=vertices,faces=faces,top_faces=len(ftop),base_surface=Z0,
                        bed=escara,heights=Z,grid_shape=(ny,nx),colors=cores)
    mesh = bpy.data.meshes.new('Calcâneo '+nome)
    mesh.from_pydata(vertices.tolist(),[],faces.tolist()); mesh.update()
    obj = bpy.data.objects.new('Calcâneo • '+nome,mesh); scene.collection.objects.link(obj)
    mesh.materials.append(clinico)
    cor = mesh.color_attributes.new(name='CorClinica',type='FLOAT_COLOR',domain='POINT')
    cores_base = np.tile([.35,.19,.09,1],(len(cont),1))
    cor.data.foreach_set('color',np.vstack((cores.reshape(-1,4),cores_base)).astype(np.float32).ravel())
    mesh.polygons.foreach_set('use_smooth',np.arange(len(faces))<len(ftop))
    obj.hide_set(nome!='tatil'); obj.hide_render = nome!='tatil'
    objetos[nome] = obj
    if nome=='tatil':
        exportar_ply(dados,SAIDA/'pressao_calcaneo_tatil_colorida.ply')

scene.render.engine = 'CYCLES'; scene.cycles.samples=16; scene.cycles.use_denoising=True
scene.render.resolution_x = scene.render.resolution_y = 1000
scene.render.resolution_percentage=100
scene.world=bpy.data.worlds.new('Estúdio'); scene.world.color=(.14,.14,.14)
for nome, pos, energia, diam in [('Principal',(-85,-96,140),255000,70),('Preenchimento',(130,105,170),190000,105)]:
    luz = bpy.data.lights.new(nome,'AREA'); luz.energy=energia; luz.size=diam
    ob=bpy.data.objects.new(nome,luz); scene.collection.objects.link(ob); ob.location=pos
    ob.rotation_euler=(Vector((0,-30,15))-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.mesh.primitive_plane_add(size=1800,location=(0,0,-.12))
chao=bpy.context.object; chao.name='Estúdio'; chao.data.materials.append(material('Fundo',(.14,.17,.18),.9)[0])
camdata=bpy.data.cameras.new('Câmera'); camdata.type='ORTHO'; camdata.clip_end=2000
cam=bpy.data.objects.new('Câmera',camdata); scene.collection.objects.link(cam); scene.camera=cam
vistas=[('01_posterior_obliqua',(125,-195,265),(0,-5,16),207),('02_posterior',(0,-.01,330),(0,0,16),210),
        ('03_detalhe_escara',(30,-145,181),(2,(centro_y-.5)*L,29),73),
        ('04_detalhe_monocromatico',(-50,-175,142),(2,(centro_y-.5)*L,29),80)]
for indice,(nome,pos,alvo,zoom) in enumerate(vistas):
    cam.location=pos; cam.rotation_euler=(Vector(alvo)-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.ortho_scale=zoom
    if indice==0:
        bpy.ops.object.select_all(action='DESELECT'); objetos['tatil'].select_set(True)
        bpy.context.view_layer.objects.active=objetos['tatil']
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.color_type='VERTEX'
        bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA/'pressao_calcaneo.blend'))
    if indice==3: objetos['tatil'].data.materials[0]=marfim
    scene.render.filepath=str(SAIDA/'renders'/f'{nome}.png')
    bpy.ops.render.render(write_still=True)
