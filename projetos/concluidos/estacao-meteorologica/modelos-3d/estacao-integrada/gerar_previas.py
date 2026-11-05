"""Renderiza as malhas reais dos STL com Matplotlib, sem alterar os modelos."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgb
from validar_modelo import ler_stl

PASTA = Path(__file__).resolve().parent
RX = np.diag([1,-1,-1])
a = np.deg2rad(30)
RZ = np.array([[np.cos(a),-np.sin(a),0],[np.sin(a),np.cos(a),0],[0,0,1]])
PORTA = np.array([[0,0,1],[1,0,0],[0,1,0]])

def malha(nome):
    return ler_stl(PASTA/"STL"/f"{nome}.stl")

def desfazer_impressao(t, altura):
    return (t-[0,0,altura]) @ RX.T

def rasterizar(objetos, largura=850, altura=1050, elevacao=20, azimute=-135):
    """Projecao ortogonal dos STL com teste de profundidade por pixel."""
    el, az = np.deg2rad([elevacao, azimute])
    vista = np.array([np.cos(el)*np.cos(az), np.cos(el)*np.sin(az), np.sin(el)])
    direita = np.array([-np.sin(az),np.cos(az),0])
    cima = np.cross(vista,direita)
    matriz = np.array([direita,cima,vista]).T
    projetados = [(t@matriz,t,cor) for t,cor in objetos]
    pts = np.concatenate([p.reshape(-1,3) for p,_,_ in projetados])
    lo, hi = pts.min(axis=0), pts.max(axis=0)
    meio=(lo+hi)/2
    escala=.92*min(largura/(hi[0]-lo[0]),altura/(hi[1]-lo[1]))
    rgb=np.ones((altura,largura,3))
    depth=np.full((altura,largura),-np.inf)
    luz=np.array([-.5,-.8,1]);luz/=np.linalg.norm(luz)
    for projetado,t,cor in projetados:
        n=np.cross(t[:,1]-t[:,0],t[:,2]-t[:,0])
        n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
        shade=.52+.48*np.maximum(n@luz,0)
        cores=np.array(to_rgb(cor))[None,:]*shade[:,None]
        for tri,normal,face in zip(projetado,n,cores):
            if normal@vista<=1e-10:
                continue
            x=(tri[:,0]-meio[0])*escala+largura/2
            y=altura/2-(tri[:,1]-meio[1])*escala
            xmin=max(0,int(np.floor(x.min())));xmax=min(largura-1,int(np.ceil(x.max())))
            ymin=max(0,int(np.floor(y.min())));ymax=min(altura-1,int(np.ceil(y.max())))
            if xmax<xmin or ymax<ymin:
                continue
            den=(y[1]-y[2])*(x[0]-x[2])+(x[2]-x[1])*(y[0]-y[2])
            if abs(den)<1e-10:
                continue
            xx,yy=np.meshgrid(np.arange(xmin,xmax+1)+.5,np.arange(ymin,ymax+1)+.5)
            w0=((y[1]-y[2])*(xx-x[2])+(x[2]-x[1])*(yy-y[2]))/den
            w1=((y[2]-y[0])*(xx-x[2])+(x[0]-x[2])*(yy-y[2]))/den
            w2=1-w0-w1
            z=w0*tri[0,2]+w1*tri[1,2]+w2*tri[2,2]
            d=depth[ymin:ymax+1,xmin:xmax+1]
            mask=(w0>=-1e-7)&(w1>=-1e-7)&(w2>=-1e-7)&(z>d)
            d[mask]=z[mask]
            rgb[ymin:ymax+1,xmin:xmax+1][mask]=face
    return np.uint8(np.clip(rgb*255,0,255))


def conjunto(explodido=False):
    gap=18 if explodido else 0
    objetos=[(malha("caixa"),"#96BDD0"),
             ((malha("portinha")-[0,0,1])@PORTA.T+[-61,0,16],"#96BDD0"),
             (desfazer_impressao(malha("tampa_caixa"),3)+[0,0,50+gap],"#42849D")]
    zbase=65+2*gap
    objetos.append((desfazer_impressao(malha("base_abrigo"),22.4)@RZ.T+[0,0,zbase],"#E9ECE9"))
    for i in range(1,6):
        objetos.append((desfazer_impressao(malha("aleta"),22.4)@RZ.T+[0,0,zbase+i*(18+gap)],"#E9ECE9"))
    objetos.append((desfazer_impressao(malha("teto"),22.4)@RZ.T+[0,0,zbase+6*(18+gap)],"#E9ECE9"))
    return objetos


if __name__=="__main__":
    fig,axes=plt.subplots(1,2,figsize=(13,10),facecolor="white")
    for ax,explodido in zip(axes,[False,True]):
        ax.imshow(rasterizar(conjunto(explodido)))
        ax.set_axis_off()
        ax.set_title("Vista explodida" if explodido else "Montado",fontsize=18,color="#233F4C")
    fig.suptitle("Estação meteorológica — caixa e abrigo integrados",fontsize=22,color="#233F4C",y=.96)
    fig.text(.5,.075,"Tampa com travas laterais • União por baioneta • Aletas encaixáveis",ha="center",fontsize=15,color="#3B5968")
    fig.text(.5,.045,"Caixa 120 × 80 × 50 mm  |  Abrigo Ø 140 mm  |  Altura montada 195,4 mm",ha="center",fontsize=13,color="#3B5968")
    fig.subplots_adjust(top=.89,bottom=.12,left=.01,right=.99,wspace=0)
    fig.savefig(PASTA/"previa_montagem.png",dpi=160)
    plt.close(fig)
    fig,axes=plt.subplots(1,3,figsize=(12,5.5),facecolor="white")
    for ax,(nome,titulo,cor) in zip(axes,[
        ("tampa_caixa","Tampa: travas e soquete interno","#42849D"),
        ("base_abrigo","Base: tubo, colar e três pinos","#D6DDD9"),
        ("teste_baioneta","Amostra da baioneta","#9DBDCA")]):
        ax.imshow(rasterizar([(malha(nome),cor)],800,700,35,-70))
        ax.set_axis_off()
        ax.set_title(titulo,fontsize=12,color="#233F4C")
    fig.suptitle("Peças na orientação de impressão",fontsize=19,color="#233F4C")
    fig.subplots_adjust(left=0,right=1,top=.85,bottom=.03,wspace=0)
    fig.savefig(PASTA/"detalhes_encaixes.png",dpi=160)
    plt.close(fig)
