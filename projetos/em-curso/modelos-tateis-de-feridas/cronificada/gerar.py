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

# Segmento anteromedial distal com transição da panturrilha para o tornozelo.
L, W = a['comprimento_mm'], a['largura_mm']
passo = config['malha']['passo_mm']
ny, nx = math.ceil(L/passo)+1, math.ceil(W/passo)+1
s = np.linspace(0,1,ny)[:,None]
u = np.linspace(-1,1,nx)[None,:]
largura = W*(.69 + .31*suave((s-.25)/.65) + .12*np.exp(-((s-.13)/.085)**2))
X = largura*u/2 + .025*W*np.sin(s*5)
Y = np.broadcast_to((s-.5)*L, X.shape)
perfil = np.maximum(0,1-u*u)**.64
Z0 = a['base_mm'] + perfil*(a['altura_mm']*(.77+.23*suave(s)) +
      6.5*sino(u+.46,s-.14,.33,.075) + 2.0*sino(u-.30,s-.55,.18,.45))
centro_x, centro_y = a['centro_lesao_fracao']
dx, dy = X-centro_x*W, Y-(centro_y-.5)*L

# Pontos da margem visível no último painel da fotografia, em pixels da prancha.
pontos = np.array([(843,289),(858,291),(874,295),(890,291),(912,296),(931,313),
 (935,333),(929,350),(916,370),(902,378),(889,375),(877,363),(871,370),
 (870,392),(881,400),(895,400),(902,413),(894,431),(882,445),(880,463),
 (874,480),(880,496),(875,512),(873,528),(862,532),(852,519),(851,498),
 (845,477),(838,467),(835,449),(829,430),(819,415),(815,398),(816,378),
 (820,359),(819,343),(825,325),(833,307)],float)
# Suavizar cantos por subdivisão de Chaikin e calibrar os dois eixos.
for _ in range(2):
    seguinte = np.roll(pontos,-1,axis=0)
    pontos = np.stack((.75*pontos+.25*seguinte,.25*pontos+.75*seguinte),axis=1).reshape(-1,2)
pontos = ((pontos-pontos.min(axis=0))/np.ptp(pontos,axis=0)-.5)*[a['largura_lesao_mm'],-a['comprimento_lesao_mm']]
interno = np.zeros_like(X,dtype=bool)
dist2 = np.full_like(X,np.inf)
for (x0,y0),(x1,y1) in zip(pontos,np.roll(pontos,-1,axis=0)):
    vx,vy = x1-x0,y1-y0
    t = np.clip(((dx-x0)*vx+(dy-y0)*vy)/(vx*vx+vy*vy),0,1)
    dist2 = np.minimum(dist2,(dx-x0-t*vx)**2+(dy-y0-t*vy)**2)
    if vy:
        interno ^= ((dy>y0)!=(dy>y1)) & (dx<x0+vx*(dy-y0)/vy)
dist = np.where(interno,1,-1)*np.sqrt(dist2)
dist += a['irregularidade_borda_mm']*np.sin(.58*dy+.33*dx)*np.cos(.37*dx)
assert max(dist[[0,-1]].max(),dist[:,[0,-1]].max()) < -5
leito = suave(dist/a['transicao_mm'])
borda = np.exp(-((dist+.25)/1.35)**2)
halo = np.exp(-((dist+2.8)/4.8)**2)*(1-leito)
# Grânulos com posição, largura e altura variáveis, avaliados em faixas locais.
rng = np.random.default_rng(config['malha']['semente'])
granulos = np.zeros_like(X)
diam = textura['largura_granulos_mm']
for gy in np.arange(dy.min(),dy.max(),diam*1.35):
    if abs(gy)>a['comprimento_lesao_mm']/2+diam*3:
        continue
    linhas = abs(dy[:,0]-gy)<diam*4
    for gx in np.arange(-a['largura_lesao_mm']/2-diam,a['largura_lesao_mm']/2+diam,diam*1.35):
        cx,cy = [gx,gy]+rng.uniform(-.58,.58,2)*diam
        g = sino(dx[linhas]-cx,dy[linhas]-cy,diam*rng.uniform(.46,.82),diam*rng.uniform(.51,.88))
        granulos[linhas] = np.maximum(granulos[linhas],rng.uniform(.58,1.0)*g)
xrel = dx/a['largura_lesao_mm']
yrel = dy/a['comprimento_lesao_mm']
manchas = (sino(xrel+.19,yrel-.28,.16,.15)+.88*sino(xrel+.10,yrel+.21,.14,.09)
           +.85*sino(xrel-.23,yrel-.39,.11,.075))
fibrina = suave((textura['extensao_fibrina']*manchas+.08*np.sin(.9*dx+.26*dy)-.30)/.55)
faixas = (.5+.5*np.cos(2.1*dx+.45*dy+np.sin(.49*dy)))
textura_leito = (textura['altura_granulacao_mm']*granulos*(1-fibrina)
                 + textura['altura_fibrina_mm']*(.4+.6*faixas)*fibrina)
ondulacao = .5*np.sin(.61*dx+.24*dy)+.5*np.cos(.80*dy+np.sin(.32*dx))
relevo = (leito*textura_leito + borda*textura['altura_borda_mm']
          + halo*textura['rugosidade_perilesional_mm']*ondulacao)
pele = textura['rugosidade_pele_mm']*np.sin(.86*X+.4*np.sin(Y*.22))*np.sin(Y*.94)
base_leito = leito*(.73+.27*sino(xrel+.13,yrel-.19,.36,.35))
cores = np.empty((*X.shape,4))
cores[:] = [.51,.31,.255,1]
marmore = np.sin(.11*dx+.13*dy+np.sin(.15*dx))*np.cos(.20*dx-.09*dy)
cores[:,:,:3] += (.022*marmore)[:,:,None]
def misturar(cor,peso):
    peso = np.clip(peso,0,1)[:,:,None]
    cores[:,:,:3] = cores[:,:,:3]*(1-peso)+cor*peso
misturar([.395,.17,.16],halo*(.72+.18*marmore))
misturar([.67,.41,.37],borda*.85)
tom = np.clip(.25+.31*granulos+.17*marmore+.14*np.sin(dx*.5+dy*.24),0,1)[:,:,None]
misturar(np.array([.235,.027,.025])+tom*np.array([.29,.075,.044]),suave((dist+.2)/1.3))
misturar([.61,.36,.17],fibrina*leito*(.65+.28*faixas))
misturar([.73,.54,.49],sino(xrel-.07,yrel-.1,.13,.08)*(1-leito)*.89)

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
        f.write(b'Lesao cronificada - mm'.ljust(80,b' '))
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

clinico, shader = material('Pele, margem e leito',(.5,.27,.18),.81)
atributo = clinico.node_tree.nodes.new('ShaderNodeVertexColor')
atributo.layer_name = 'CorClinica'
clinico.node_tree.links.new(atributo.outputs['Color'],shader.inputs['Base Color'])
marfim, _ = material('PLA marfim',(.58,.53,.40),.82)
objetos = {}
for nome, ganho in config['ampliacao_tatil'].items():
    superficie = ganho*relevo + pele*(1-leito)*perfil
    interior = base_leito > 0
    # Impõe a profundidade máxima após a aplicação das texturas, em ambas as versões.
    escala = np.min((a['profundidade_maxima_mm']+superficie[interior])/base_leito[interior])
    Z = Z0 + superficie - escala*base_leito
    assert abs(np.max(Z0-Z)-a['profundidade_maxima_mm'])<1e-5
    topo = np.column_stack((X.ravel(),Y.ravel(),Z.ravel()))
    base = topo[cont].copy(); base[:,2]=0
    vertices = np.vstack((topo,base)).astype(np.float32)
    assert vertices[:ids.size,2].min()>2, 'Pele cruza a face de apoio'
    escrever_stl(SAIDA/f'lesao_cronificada_{nome}.stl',vertices)
    dados = SAIDA/'validacao'/f'geometria_{nome}.npz'
    np.savez_compressed(dados,vertices=vertices,faces=faces,top_faces=len(ftop),base_surface=Z0,
                        bed=leito,heights=Z,grid_shape=(ny,nx),colors=cores)
    mesh = bpy.data.meshes.new('Perna distal '+nome)
    mesh.from_pydata(vertices.tolist(),[],faces.tolist()); mesh.update()
    obj = bpy.data.objects.new('Perna distal • '+nome,mesh); scene.collection.objects.link(obj)
    mesh.materials.append(clinico)
    cor = mesh.color_attributes.new(name='CorClinica',type='FLOAT_COLOR',domain='POINT')
    cores_base = np.tile([.35,.19,.09,1],(len(cont),1))
    cor.data.foreach_set('color',np.vstack((cores.reshape(-1,4),cores_base)).astype(np.float32).ravel())
    mesh.polygons.foreach_set('use_smooth',np.arange(len(faces))<len(ftop))
    obj.hide_set(nome!='tatil'); obj.hide_render = nome!='tatil'
    objetos[nome] = obj
    if nome=='tatil':
        exportar_ply(dados,SAIDA/'lesao_cronificada_tatil_colorida.ply')

scene.render.engine = 'CYCLES'; scene.cycles.samples=12; scene.cycles.use_denoising=True
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
vistas=[('01_vista_obliqua',(125,-195,265),(0,-5,16),207),('02_anteromedial',(0,-.01,330),(0,0,16),216),
        ('03_detalhe_leito',(30,-145,181),(2,(centro_y-.5)*L,29),101),
        ('04_detalhe_monocromatico',(-50,-175,142),(2,(centro_y-.5)*L,29),102)]
for indice,(nome,pos,alvo,zoom) in enumerate(vistas):
    cam.location=pos; cam.rotation_euler=(Vector(alvo)-cam.location).to_track_quat('-Z','Y').to_euler(); camdata.ortho_scale=zoom
    if indice==0:
        bpy.ops.object.select_all(action='DESELECT'); objetos['tatil'].select_set(True)
        bpy.context.view_layer.objects.active=objetos['tatil']
        for area in bpy.context.screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.region_3d.view_perspective='CAMERA'
                area.spaces.active.shading.color_type='VERTEX'
        bpy.ops.wm.save_as_mainfile(filepath=str(SAIDA/'lesao_cronificada.blend'))
    if indice==3: objetos['tatil'].data.materials[0]=marfim
    scene.render.filepath=str(SAIDA/'renders'/f'{nome}.png')
    bpy.ops.render.render(write_still=True)
