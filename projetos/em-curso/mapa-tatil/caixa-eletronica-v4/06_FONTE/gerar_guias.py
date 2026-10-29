"""Guia e gabaritos vetoriais: painéis obrigatórios 500x380 mm."""
import json
import textwrap
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle
from matplotlib.backends.backend_pdf import PdfPages
INK='#203340'; BLUE='#d2e5e9'; GOLD='#e8cf97'; RED='#af443c'


def page(title,n):
    fig=plt.figure(figsize=(11.69,8.27),facecolor='white')
    fig.text(.045,.95,'MAPA TÁTIL • REVISÃO V4 • PAINÉIS 500 × 380',fontsize=9,color='#53727b',weight='bold')
    fig.text(.045,.902,title,fontsize=19,color=INK,weight='bold')
    fig.text(.045,.035,'MDF nominal 3 mm • Medidas em mm • 19/10/2026',fontsize=8,color='#53727b')
    fig.text(.955,.035,str(n),fontsize=8,color=INK,ha='right')
    return fig


def notes(fig,bounds,items,width=53):
    ax=fig.add_axes(bounds);ax.axis('off');y=1
    for title,text in items:
        ax.text(0,y,title,fontsize=11,color=INK,weight='bold',va='top',transform=ax.transAxes)
        y-=.05
        for line in textwrap.wrap(text,width=width,break_long_words=False):
            ax.text(0,y,line,fontsize=10,color=INK,va='top',transform=ax.transAxes)
            y-=.037
        y-=.022
    assert y>-.01,(items[-1][0],y)


def outline(ax,p,x=0,y=0,color=BLUE):
    ax.add_patch(Polygon(np.array(p['contorno'])+[x,y],facecolor=color,edgecolor=INK,lw=.7))
    for h in p['furos']:
        if isinstance(h,dict):
            ax.add_patch(Circle(np.array(h['centro'])+[x,y],h['raio'],facecolor='white',edgecolor=INK,lw=.5))
        else:
            ax.add_patch(Polygon(np.array(h)+[x,y],facecolor='white',edgecolor=INK,lw=.5))


def generate(root,data):
    out=root/'05_GUIA';p=data['pecas']
    heights=json.loads((out/'VERIFICACAO.json').read_text())['altura_face_superior_mm']
    with PdfPages(out/'Guia_de_montagem.pdf') as pdf:
        fig=page('Dois painéis de 500 × 380, sem furos',1)
        ax=fig.add_axes([.045,.18,.46,.63]);ax.set_aspect('equal');ax.axis('off')
        ax.add_patch(Rectangle((40,0),300,120,facecolor='#ddd2bb',edgecolor=INK))
        for z,h,col in [(120,3,'#a08b60'),(123,3,BLUE),(170,3,GOLD)]:
            ax.add_patch(Rectangle((0,z),380,h,facecolor=col,edgecolor=INK))
        for x in (0,377):ax.add_patch(Rectangle((x,126),3,44,facecolor=BLUE,edgecolor=INK))
        ax.annotate('C1: painel removível 500 × 380',(190,173),(190,225),ha='center',fontsize=10,color=INK,arrowprops=dict(arrowstyle='-',color=INK))
        ax.annotate('C0: fundo novo 500 × 380',(230,124),(235,148),ha='center',fontsize=9,color=INK,arrowprops=dict(arrowstyle='-',color=INK))
        ax.annotate('Tampo existente 500 × 380',(180,120),(190,80),ha='center',fontsize=10,color=INK,arrowprops=dict(arrowstyle='-',color=INK))
        ax.annotate('',(397,123),(397,173),arrowprops=dict(arrowstyle='<->',color=RED))
        ax.text(405,148,'50',va='center',fontsize=11,color=RED)
        ax.text(190,20,'Pedestal já cortado\nsem modificações',ha='center',fontsize=12,color=INK)
        ax.set(xlim=(-15,435),ylim=(-10,270))
        notes(fig,[.54,.13,.42,.69],[
            ('Dimensões obrigatórias','C0 e C1 medem exatamente 500 × 380, ambos sem qualquer furo. Caixa externa 500 × 380 × 50. Esta revisão substitui a V3 de 500 × 500.'),
            ('Reaproveitamento','Mantêm-se as 46 peças da estrutura e o tampo antigo com seus 25 encaixes. C0 é colado sobre esse tampo com as quatro bordas alinhadas. Não há abas adicionais.'),
            ('Acesso pela tampa','Oito parafusos horizontais pelas paredes frontal e traseira prendem tacos colados ao painel C1. Ao soltá-los, C1 sai com os tacos e as nervuras. Não há fixação pela face inferior.'),
            ('Implantação do mapa','O gabarito existente de 500 × 500 não cabe neste painel. Rever a distribuição antes da colagem. A caixa não altera nem reduz automaticamente a maquete existente.')])
        pdf.savefig(fig);fig.savefig(out/'Conceito.png',dpi=150);plt.close(fig)

        fig=page('Planta interna: 500 × 380 mm',2)
        ax=fig.add_axes([.055,.15,.52,.65]);ax.set_aspect('equal')
        ax.add_patch(Rectangle((0,0),500,380,facecolor='#f3f7f8',edgecolor=INK))
        for s in data['nervuras_s']:
            ax.add_patch(Rectangle((3,s-15),494,30,facecolor=RED,alpha=.16))
            ax.add_patch(Rectangle((3,s-1.5),494,3,facecolor=RED))
        ax.add_patch(Rectangle((235,3),30,374,facecolor=RED,alpha=.16))
        ax.add_patch(Rectangle((248.5,3),3,374,facecolor=RED))
        for i,(x,s) in enumerate(data['parafusos'],1):
            ax.add_patch(Rectangle((x-10,s-10),20,20,facecolor=GOLD,edgecolor=INK))
            ax.annotate('',(x,s),(x,-10 if s==13 else 390),arrowprops=dict(arrowstyle='->',color=INK))
            ax.text(x,s+(17 if s==13 else -22),str(i),ha='center',fontsize=8,color=INK)
        for zone,label in zip(data['reservas_nao_medidas'],['ESP32 + protoboard\n200 × 95','DFPlayer\n100 × 95','Falante\n72 × 35']):
            x,s,z,w,d,h=zone['caixa']
            ax.add_patch(Rectangle((x,s),w,d,facecolor='#c8dfc3',edgecolor='#527c52'))
            ax.text(x+w/2,s+d/2,label,fontsize=7,ha='center',va='center',color=INK)
        ax.text(72,375,'USB',ha='center',va='top',fontsize=8,color=INK)
        ax.text(250,-36,'FRENTE / USUÁRIO • origem (0,0) à esquerda',ha='center',fontsize=9,color=INK)
        ax.set(xlim=(-15,515),ylim=(-45,400),xlabel='x',ylabel='s (na chapa inclinada)')
        ax.tick_params(labelsize=8);ax.spines[['top','right']].set_visible(False)
        notes(fig,[.62,.14,.34,.68],[
            ('Vermelho: nervuras','NX1: s=110; NX2: s=240; NY: x=250. Comprimentos NX=494, NY=374. Altura 30; vão livre de 14 sobre o fundo para fios.'),
            ('Dourado: tacos','Centros x=30, 150, 400, 470; s=13 e 367. Tacos 20 × 20 × 44. Setas: direção dos parafusos horizontais, a 35 sobre a face inferior de C0.'),
            ('Verde: reservas','Não são componentes medidos. ESP32/protoboard e DFPlayer: altura 32. Falante: 38. Medir placas, suportes, conectores e cabo reais.'),
            ('Futuros botões','Nenhum furo definido. Evitar inicialmente 15 de cada lado dos eixos vermelhos e 30 junto às bordas. Conferir todo o corpo do botão, tampa e fios.')],43)
        pdf.savefig(fig);fig.savefig(out/'Planta_interna.png',dpi=160);plt.close(fig)

        fig=page('Cortar somente as peças adicionais',3)
        ax=fig.add_axes([.045,.24,.53,.57]);ax.set_aspect('equal');ax.axis('off')
        ax.add_patch(Rectangle((0,0),600,400,fill=False,edgecolor=INK,lw=1.3))
        ax.add_patch(Rectangle((20,20),560,360,fill=False,edgecolor='#8a9aa0',ls='--'))
        for part,pos in zip(p[2:],data['posicionamento_chapa']):
            outline(ax,part,pos['x'],pos['y'],GOLD if part['solidario_tampa'] else BLUE)
            ax.text(pos['x']+15,pos['y']+9,part['id'],fontsize=8,color=INK)
        ax.set(xlim=(-10,610),ylim=(-10,410))
        fig.text(.065,.18,'7 peças em 1 chapa 600 × 400 • útil 560 × 360\nMargens de 20 • intervalo mínimo de 8',fontsize=11,color=INK)
        notes(fig,[.62,.13,.34,.69],[
            ('Dois painéis lisos 500 × 380','C0_BASE e C1_TAMPO_LISO: uma unidade de cada, MDF 3. Sem furos ou encaixes. Não repetir os 25 encaixes antigos nos painéis novos.'),
            ('Paredes e reforços','C2/C3: 494 × 44. C4/C5: 380 × 44. NX1/NX2: 494 × 30. NY: 374 × 30. Os individuais repetem as peças da chapa; não cortar duas vezes.'),
            ('Área de corte dos painéis','Usar o processo do tampo inteiro v2, com área útil que comporte 500 × 380, ou serra com guia. A área útil 560 × 360 reservada às paredes não comporta a profundidade dos painéis.'),
            ('Escala e ajuste','DXF/SVG equivalentes, mm, 1:1, sem kerf. Compensar uma vez no CAM. Ranhuras 3,15 para MDF 3: testar retalho e ajustar por lixa se preciso. Não escalar para corrigir a espessura.')],43)
        pdf.savefig(fig);plt.close(fig)

        fig=page('Fixação pelas paredes da frente e de trás',4)
        ax=fig.add_axes([.045,.20,.52,.60]);ax.set_aspect('equal');ax.axis('off')
        ax.add_patch(Rectangle((0,-3),80,3,facecolor='#a08b60',edgecolor=INK))
        ax.add_patch(Rectangle((0,0),80,3,facecolor=BLUE,edgecolor=INK))
        ax.add_patch(Rectangle((0,3),3,44,facecolor=BLUE,edgecolor=INK))
        ax.add_patch(Rectangle((3,3),20,44,facecolor=GOLD,edgecolor=INK))
        ax.add_patch(Rectangle((0,47),80,3,facecolor=GOLD,edgecolor=INK))
        ax.add_patch(Rectangle((-1,34),17,2,facecolor='#5b6570',edgecolor=INK))
        ax.add_patch(Rectangle((-3,32),2,6,facecolor='#5b6570',edgecolor=INK))
        ax.annotate('Parafuso horizontal\n3 × 16 + arruela',(-2,35),(-17,64),fontsize=10,color=INK,arrowprops=dict(arrowstyle='->',color=INK))
        ax.annotate('Taco 20 × 20 × 44\ncolado SÓ ao painel',(17,25),(34,67),fontsize=10,color=INK,arrowprops=dict(arrowstyle='->',color=INK))
        ax.text(42,52,'C1 liso',fontsize=10,color=INK);ax.text(42,5,'C0 liso',fontsize=10,color=INK)
        ax.text(40,-10,'Tampo antigo alinhado',ha='center',fontsize=10,color=INK)
        ax.set(xlim=(-20,90),ylim=(-18,83))
        notes(fig,[.62,.13,.34,.69],[
            ('Oito parafusos de madeira','3 × 16, cabeça panela, com arruela externa de cerca de 7. Quatro pela frente e quatro por trás. Furos Ø3,5 somente nas paredes; não escarear o MDF de 3.'),
            ('Pré-furos nos tacos','Alinhar a seco e transferir os centros. Pré-furo Ø2, cerca de 13 de profundidade, a confirmar na madeira. Eixo a 35 sobre C0, ou 32 acima da borda inferior da parede.'),
            ('Colagem do painel removível','Colar tacos e nervuras somente a C1. Não colar tacos ao fundo nem às paredes. Conferir que o painel assenta sem empeno e que pode ser levantado após retirar os parafusos.'),
            ('Manutenção','Desconectar USB, apoiar C1 e retirar os oito parafusos. Levantar o painel com tacos e nervuras. Prever folga e conector nos futuros fios dos botões; microSD acessível com C1 aberto.')],43)
        pdf.savefig(fig);plt.close(fig)

        fig=page('Ordem de montagem',5)
        notes(fig,[.05,.12,.43,.70],[
            ('1. Preparar o pedestal','Concluir a montagem v2, incluindo lastro, grelha e tampo. Lixar os 25 dentes rentes. Nenhuma peça antiga será recortada ou furada.'),
            ('2. Montar a caixa separadamente','Colar as laterais C4/C5 por fora e C2/C3 entre elas, sobre C0. Borda inferior das paredes sobre o fundo; altura 44. Conferir esquadro e diagonais.'),
            ('3. Preparar C1','Colar tacos somente a C1. Montar NX com ranhuras para cima e NY para baixo; colar cruzamentos e arestas superiores ao painel. Testar fechamento e retirada antes da colagem definitiva.'),
            ('4. Colar C0 ao tampo antigo','Alinhar as quatro bordas 500 × 380, sem deslocamento nem abas. Usar cola compatível com MDF e acabamento, prensar sem empeno e aguardar cura. Inclinação mantida em 9,09°.')])
        notes(fig,[.54,.12,.42,.70],[
            ('5. Fixar placas e fios','Usar suportes isolantes e espaçadores, sem colar contatos. Vão interno 44. Separar fios e nervuras. Não furar o fundo até atingir o tampo antigo.'),
            ('6. USB e alívio de tração','O entalhe traseiro 24 × 14 recebe o cabo com C1 aberto. Os dois rasgos 3 × 8 na parede traseira recebem uma abraçadeira, acessível depois da colagem de C0.'),
            ('7. Alto-falante','Usar suporte removível ou cinta voltado à grade frontal; a grade não é suporte mecânico. Conferir o falante real na reserva 72 × 35 × 38. Não cobrir a saída com legendas.'),
            ('8. Fechar e conferir','Fixar o mapa só a C1 após rever sua implantação para 500 × 380. Testar rigidez, abertura, cabo e som. Botões ficam para a próxima revisão. Conferir lastro e limites na página 6.')])
        pdf.savefig(fig);plt.close(fig)

        fig=page('Altura, lastro e atualização dos botões',6)
        height_text=(f"Face superior: frente {heights['frente']/10:.1f} cm; centro {heights['centro']/10:.1f} cm; traseira {heights['tras']/10:.1f} cm, antes do relevo. Aumento central aproximado de 52 mm na vertical.").replace('.',',')
        notes(fig,[.05,.12,.43,.70],[
            ('Altura final',height_text),
            ('Referência estática: 19 kg totais','Hipóteses v2: força horizontal 20 N, fator 1,5, metade da profundidade da base 0,17 m, piso plano e massa centrada. Adotar altura de esforço 1,02 m, com margem para o relevo: m = 1,5 × 20 × 1,02 / (9,81 × 0,17) = 18,35 kg; arredondar para 19 kg.'),
            ('Pesar e completar o lastro','Os 19 kg substituem os 17 kg da configuração anterior, neste caso assumido. Lastro imobilizado sobre B3, antes de fechar H1. Não apoiar peso em H1/H2 ou na caixa. Se já fechado, avaliar a fixação ao piso do manual v2.'),
            ('Limites','O cálculo não define carga máxima no painel nem cobre alguém apoiando o corpo. Nesse uso permanece a orientação de fixação ao piso e avaliação estrutural. Conferir alcance, flexão e colagens fisicamente.')])
        notes(fig,[.54,.12,.42,.70],[
            ('Botões: informações necessárias','Centro x e s desde o canto dianteiro esquerdo de C1; formato/diâmetro do furo; profundidade do corpo; mecanismo e folga da tampa. Nervuras novas podem mudar depois, preservando o pedestal.'),
            ('Gabarito do mapa existente','O gabarito 500 × 500 não deve ser usado diretamente, recortado ou escalado sem rever a implantação tátil. Os 18 marcadores não definem os 10 botões do guia. Esta entrega contém a caixa e os painéis lisos.'),
            ('Adaptação do guia original','Mantidos espaço para módulos, acesso ao microSD, saída de som e alívio USB. A manutenção é pelo painel superior, devido à grelha e ao corpo fechado existentes. A caixa impressa antiga de altura 80 não cabe no vão de 44.'),
            ('Conferências','Dimensões, contornos, malhas e colisões das peças novas foram verificados. As reservas dos componentes exigem medição. Testar encaixe e funcionamento reais antes da colagem. Relatórios e fontes acompanham os cortes.')])
        pdf.savefig(fig);plt.close(fig)

    fig=plt.figure(figsize=(500/25.4,380/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_aspect('equal');ax.axis('off')
    ax.set(xlim=(0,500),ylim=(0,380))
    ax.add_patch(Rectangle((0,0),500,380,fill=False,edgecolor=INK,lw=.5))
    for s in data['nervuras_s']:ax.add_patch(Rectangle((3,s-1.5),494,3,facecolor=RED))
    ax.add_patch(Rectangle((248.5,3),3,374,facecolor=RED))
    for x,s in data['parafusos']:ax.add_patch(Rectangle((x-10,s-10),20,20,facecolor=GOLD,edgecolor=INK,lw=.5))
    ax.text(20,65,'PLANEJAMENTO • NÃO É CORTE\nPainel 500 × 380 • vermelho: nervuras • dourado: tacos\nC0 e C1 inteiramente lisos nesta revisão • escala 1:1',fontsize=11,color=INK)
    ax.plot([170,270],[30,30],color=INK,lw=1);ax.text(220,20,'CONFERIR: 100 mm',ha='center',fontsize=10,color=INK)
    ax.text(250,5,'FRENTE / USUÁRIO • origem (0,0) à esquerda',ha='center',fontsize=10,color=INK)
    fig.savefig(out/'Planejar_botoes_500x380_1_1.pdf');plt.close(fig)

    fig=plt.figure(figsize=(494/25.4,112/25.4));ax=fig.add_axes([0,0,1,1]);ax.set_aspect('equal');ax.axis('off')
    ax.set(xlim=(0,494),ylim=(0,112))
    outline(ax,p[2],0,0,'white');outline(ax,p[3],0,52,'white')
    ax.text(200,5,'C2 FRENTE',fontsize=9,color=INK);ax.text(200,57,'C3 TRÁS',fontsize=9,color=INK)
    ax.text(247,103,'GABARITO 1:1 • imprimir 100% • furos Ø3,5 a 32 da borda inferior de cada parede',ha='center',fontsize=9,color=INK)
    fig.savefig(out/'Gabarito_paredes_494x44_1_1.pdf');plt.close(fig)
