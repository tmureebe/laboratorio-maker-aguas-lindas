"""Gera o catálogo vetorial das ferragens. Requer ReportLab (Python do sistema)."""
from pathlib import Path
import math
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, black, white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Manual_Ilustrado_Ferragens_V7.pdf'
for name, filename in [('DV','DejaVuSans.ttf'), ('DVB','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + filename))
W,H=A4
C=canvas.Canvas(str(OUT),pagesize=A4)
C.setTitle('Ferragens V7 — catálogo ilustrado com medições — revisão 05')
C.setAuthor('Laboratório MAKER')
INK=HexColor('#19242c'); BLUE=HexColor('#244d64'); LIGHT=HexColor('#e9eff2'); LINE=HexColor('#bac7ce')

def text(x,y,s,size=9,bold=False,color=INK):
    C.setFillColor(color); C.setFont('DVB' if bold else 'DV',size); C.drawString(x,y,s)

def wrap(x,y,s,width,size=9,leading=13,bold=False):
    words=s.split(); line=''
    for word in words:
        attempt=(line+' '+word).strip()
        if pdfmetrics.stringWidth(attempt,'DVB' if bold else 'DV',size)>width and line:
            text(x,y,line,size,bold); y-=leading; line=word
        else: line=attempt
    if line: text(x,y,line,size,bold); y-=leading
    return y

def poly(points,fill=0):
    p=C.beginPath(); p.moveTo(*points[0])
    for point in points[1:]: p.lineTo(*point)
    p.close(); C.drawPath(p,stroke=1,fill=fill)

def arrow(x,y,angle):
    a=math.radians(angle)
    for off in [-25,25]:
        b=a+math.radians(off); C.line(x,y,x+5*math.cos(b),y+5*math.sin(b))

def dim(x1,y1,x2,y2,label):
    C.setStrokeColor(INK); C.setLineWidth(.55); C.line(x1,y1,x2,y2)
    a=math.degrees(math.atan2(y2-y1,x2-x1))
    arrow(x1,y1,a); arrow(x2,y2,a+180)
    if abs(y2-y1)<1:
        C.setFillColor(white); tw=pdfmetrics.stringWidth(label,'DV',8)
        C.rect((x1+x2-tw)/2-3,y1-3,tw+6,11,stroke=0,fill=1)
        text((x1+x2-tw)/2,y1, label,8)
    else: text(x1+5,(y1+y2)/2-2,label,8)

def measurement_table(y,widths,headers,rows,row_h=32):
    x=34
    for row_index,row in enumerate([headers]+rows):
        xx=x
        for width,value in zip(widths,row):
            C.setFillColor(LIGHT if row_index==0 else white)
            C.setStrokeColor(LINE); C.setLineWidth(.5)
            C.rect(xx,y-row_h,width,row_h,stroke=1,fill=1)
            wrap(xx+8,y-13,value,width-16,8,10,row_index==0)
            xx+=width
        y-=row_h
    return y

def screw(x,y,length,d,kind='pan',scale=2.7,top=True,dimensions=True):
    """Vista lateral: eixo horizontal, cabeça à esquerda. Contornos ilustrativos."""
    C.setStrokeColor(INK); C.setLineWidth(1); C.setFillColor(white)
    shaft=d*scale; r=shaft/2; headw=d*scale*.8; headr=d*scale
    if kind=='flat':
        start=x+headw; end=x+length*scale
        poly([(x,y-headr),(x,y+headr),(start,y+r),(start,y-r)],1)
    elif kind=='allen':
        start=x+headw; end=start+length*scale
        C.rect(x,y-headr,headw,2*headr,stroke=1,fill=1)
        C.line(x+headw*.3,y-headr,x+headw*.3,y+headr)
    else:
        start=x+headw; end=start+length*scale
        p=C.beginPath(); p.moveTo(start,y-headr)
        p.curveTo(x-headw*.3,y-headr,x-headw*.3,y+headr,start,y+headr)
        p.close(); C.drawPath(p,stroke=1,fill=1)
    poly([(start,y-r),(end-2,y-r),(end,y-r+2),(end,y+r-2),(end-2,y+r),(start,y+r)],1)
    C.setLineWidth(.5)
    t=start+3
    while t<end-3:
        C.line(t,y-r,t+3,y+r); t+=4
    if kind!='allen': C.line(x+headw*.15,y-2,x+headw*.15,y+2)
    if top:
        tx=end+43
        C.setLineWidth(1); C.circle(tx,y,headr,stroke=1,fill=0)
        if kind=='allen':
            rr=headr*.48
            poly([(tx+rr*math.cos(math.radians(60*i)),y+rr*math.sin(math.radians(60*i))) for i in range(6)])
        else:
            rr=headr*.55
            C.setLineWidth(2); C.line(tx-rr,y,tx+rr,y); C.line(tx,y-rr,tx,y+rr)
        text(tx-headr-3,y-headr-13,'cabeça',6.5)
    if dimensions:
        base=x if kind=='flat' else start
        C.setLineWidth(.4); C.line(base,y-headr-2,base,y-35); C.line(end,y-r-2,end,y-35)
        dim(base,y-30,end,y-30,f'{length} mm')
        dx=end+8; C.line(end,y-r,dx+3,y-r); C.line(end,y+r,dx+3,y+r)
        dim(dx,y-r,dx,y+r,f'Ø{d}')
    return start,end

def nut(x,y,d,scale=6):
    C.setStrokeColor(INK); C.setLineWidth(1); C.setFillColor(white)
    r=d*scale
    pts=[(x+r*math.cos(math.radians(30+60*i)),y+r*.68*math.sin(math.radians(30+60*i))) for i in range(6)]
    low=[(px,py-10) for px,py in pts]
    poly([pts[i] for i in [3,4,5,0]]+[low[i] for i in [0,5,4,3]],1)
    poly(pts,1)
    C.ellipse(x-r*.42,y-r*.28,x+r*.42,y+r*.28,stroke=1,fill=0)
    C.ellipse(x-r*.32,y-r*.2,x+r*.32,y+r*.2,stroke=1,fill=0)

def washer(x,y,d,wide=False):
    C.setStrokeColor(INK); C.setLineWidth(1); C.setFillColor(white)
    r=30 if wide else 23
    C.ellipse(x-r,y-r*.48-4,x+r,y+r*.48-4,stroke=1,fill=1)
    C.ellipse(x-r,y-r*.48,x+r,y+r*.48,stroke=1,fill=1)
    ir=10 if wide else 9
    C.ellipse(x-ir,y-ir*.48,x+ir,y+ir*.48,stroke=1,fill=1)
    if wide:
        C.line(x-r,y-22,x-r,y-35); C.line(x+r,y-22,x+r,y-35)
        dim(x-r,y-31,x+r,y-31,'≈ 12 mm')

def page(number,title,subtitle):
    C.setFillColor(BLUE); C.rect(0,H-9,W,9,stroke=0,fill=1)
    text(34,H-43,'TÚNEL HÍBRIDO V7',9,True,BLUE)
    text(34,H-72,title,21,True)
    wrap(34,H-93,subtitle,W-68,9,13)
    C.setStrokeColor(LINE); C.setLineWidth(.5); C.line(34,35,W-34,35)
    text(34,22,'20/10/2026 • Rev. 05 • Desenhos sem escala • Medidas em mm',7)
    text(W-47,22,str(number),8,True)

def frame(x,y,w,h,code,qty):
    C.setStrokeColor(LINE); C.setLineWidth(.7); C.roundRect(x,y,w,h,6,stroke=1,fill=0)
    C.setFillColor(LIGHT); C.roundRect(x+10,y+h-34,44,23,4,stroke=0,fill=1)
    text(x+17,y+h-26,code,10,True)
    tw=pdfmetrics.stringWidth(qty,'DVB',9)
    text(x+w-12-tw,y+h-25,qty,9,True)

def screwcard(x,y,code,d,L,kind,buy,needed,usage):
    w=(W-80)/2; h=190
    frame(x,y,w,h,code,f'COMPRAR {buy}')
    wrap(x+12,y+h-53,f'M{d} × {L} mm',w-24,12,15,True)
    title={'pan':'Cabeça panela • Phillips','flat':'Cabeça chata escareada • Phillips','allen':'Cabeça cilíndrica • Allen'}[kind]
    wrap(x+12,y+h-70,title,w-24,8,11)
    s=min(2.7,(w-84)/L)
    screw(x+20,y+82,L,d,kind,s)
    text(x+12,y+33,needed,8,True)
    wrap(x+12,y+18,usage,w-24,7.5,10)

page(1,'Parafusos principais','Identifique cada ferragem pelo código. “Comprar” inclui reservas; “usar” indica a quantidade da montagem com base bipartida. Parafusos da célula: página 4.')
items=[
 ('P01',4,20,'pan',30,'USAR 17','12 nos pés + 4 na base do sensor + 1 no regulador.'),
 ('P02',4,55,'pan',8,'USAR 4; conferir montagem','Ventoinha entre parte 5 e parte 1.'),
 ('P03',3,40,'pan',10,'USAR 4','Grade, espaçador e parte 2; também reserva.'),
 ('P04',3,35,'pan',10,'USAR 1','Eixo da asa; também reserva para a janela.'),
 ('P05',3,25,'pan',10,'USAR 6, após conferir','Presilhas da janela; testar a pilha real.'),
 ('P06',3,12,'flat',6,'USAR 2','Alavanca e disco; cabeça nivelada com o disco.')]
purchase_screws=sum(item[4] for item in items)
for i,item in enumerate(items): screwcard(34+(i%2)*((W-80)/2+12),H-322-(i//2)*202,*item)
C.showPage()

page(2,'Base bipartida e reservas','A base bipartida faz parte desta montagem. As demais linhas são reservas para ajustes nas fixações indicadas; não são fixações adicionais.')
items=[
 ('P07',4,20,'flat',8,'USAR 4','Talas inferiores da base bipartida de MDF.'),
 ('P08',4,25,'flat',8,'RESERVA do P07','Para pilha mais espessa; conferir folga inferior.'),
 ('P09',4,25,'pan',10,'RESERVA do P01','Ajuste de espessura e arruelas na base.'),
 ('P10',4,30,'pan',10,'RESERVA do P01','Ajuste de espessura; conferir pontas e porcas.'),
 ('P11',4,60,'pan',8,'RESERVA do P02','Pode exigir corte; não deixar tocar pás ou disco.'),
 ('P12',3,30,'pan',10,'RESERVA do P05','Alternativa mais longa para a janela.')]
purchase_screws+=sum(item[4] for item in items)
for i,item in enumerate(items): screwcard(34+(i%2)*((W-80)/2+12),H-322-(i//2)*202,*item)
C.showPage()

page(3,'Porcas e arruelas','Quantidades para a montagem com base bipartida. A compra inclui sobras. O uso por conjunto está detalhado na página 4.')
parts=[
 ('N03',3,30,13,'nut','Porca sextavada M3','Passo 0,5 mm','4 na grade + 1 na asa + 6 na janela + 2 na alavanca.'),
 ('N04',4,50,25,'nut','Porca sextavada M4','Passo 0,7 mm','16 nos pés/base do sensor + 4 ventoinha + 1 eixo + 4 talas.'),
 ('A03',3,60,24,'washer','Arruela lisa para M3','Para parafuso de 3 mm','8 na grade + 2 na asa + 12 na janela + 2 na alavanca.'),
 ('A04',4,100,49,'washer','Arruela lisa para M4','Para parafuso de 4 mm','32 nos pés/base + 8 ventoinha + 1 eixo + 4 talas + 4 célula.'),
 ('A12',4,4,1,'wide','Arruela larga para M4','Furo ≈ 4,3 / externo ≈ 12 mm','Retenção do eixo do regulador.')]
cw=(W-80)/2; ch=190
for i,(code,d,buy,used,kind,title,note,usage) in enumerate(parts):
    x=34+(i%2)*(cw+12); y=H-322-(i//2)*202
    frame(x,y,cw,ch,code,f'COMPRAR {buy}')
    wrap(x+12,y+ch-53,title,cw-24,12,15,True)
    if kind=='nut': nut(x+cw/2,y+90,d,4.5)
    else: washer(x+cw/2,y+(98 if kind=='wide' else 90),d,kind=='wide')
    text(x+12,y+51,note,8)
    text(x+12,y+33,f'USAR {used}',8,True)
    wrap(x+12,y+18,usage,cw-24,7.5,10)
purchase_nuts=sum(part[2] for part in parts if part[4]=='nut')
purchase_washers=sum(part[2] for part in parts if part[4]!='nut')
used_nuts=sum(part[3] for part in parts if part[4]=='nut')
used_washers=sum(part[3] for part in parts if part[4]!='nut')
wrap(34,99,'A12 deve apoiar no ressalto sem prender o disco. Nas fixações escareadas, usar arruela somente do lado da porca. A célula recebe uma arruela sob cada cabeça Allen e não usa porcas.',W-68,9,13)
C.showPage()

page(4,'Fixação da célula de carga','Comprar somente os quatro parafusos abaixo. Referência adotada: rosca M4, passo 0,7 mm. Uma arruela A04 sob cada cabeça; sem porcas na célula.')
cell_screws=[
 ('C4-30',4,30,'allen',2,'USAR 2','Extremidade fixa da célula, pela base 14.'),
 ('C4-20',4,20,'allen',2,'USAR 2','Extremidade móvel, pelas peças 15 e 16.')]
purchase_screws+=sum(item[4] for item in cell_screws)
for i,item in enumerate(cell_screws):
    screwcard(34+i*((W-80)/2+12),H-322,*item)
text(34,485,'Uso de porcas e arruelas por conjunto',12,True)
consumption=[
 ['Pés e base do sensor','0','16','0','32','0'],
 ['Ventoinha','0','4','0','8','0'],
 ['Eixo do regulador','0','1','0','1','1'],
 ['Grade e espaçador','4','0','8','0','0'],
 ['Eixo da asa','1','0','2','0','0'],
 ['Presilhas da janela','6','0','12','0','0'],
 ['Alavanca / disco','2','0','2','0','0'],
 ['Talas da base bipartida','0','4','0','4','0'],
 ['Célula de carga','0','0','0','4','0']]
consumption.append(['TOTAL','13','25','24','49','1'])
measurement_table(467,[197,66,66,66,66,66],
    ['Conjunto','N03','N04','A03','A04','A12'],consumption,row_h=27)
wrap(34,150,'N03/N04 = porcas M3/M4; A03/A04 = arruelas lisas M3/M4; A12 = arruela larga M4. Considerada a retenção da alavanca por duas porcas M3, com uma arruela por parafuso no lado da porca.',W-68,9,13)
wrap(34,96,'A montagem usa 38 porcas e 74 arruelas. As quantidades de compra da página 3 já incluem todas as linhas desta tabela; não somar novamente.',W-68,9,13)
C.showPage()

page(5,'Como reconhecer e medir','Guia visual para conferir os saquinhos de ferragens antes da montagem. As cabeças e os contornos são ilustrativos; prevalecem as medidas indicadas.')
text(34,704,'1  Cabeças comuns e cabeças escareadas',12,True)
screw(50,651,25,4,'pan',3.1)
text(50,595,'PANELA PHILLIPS',9,True)
wrap(50,579,'Medir da face de baixo da cabeça até a ponta.',220,9,13)
screw(328,651,25,4,'flat',3.1)
text(328,595,'CHATA ESCAREADA',9,True)
wrap(328,579,'Medir incluindo a cabeça, até a ponta.',220,9,13)
text(34,527,'2  Se a loja oferecer Allen',12,True)
screw(55,475,25,4,'allen',3.1)
wrap(285,490,'Allen de cabeça cilíndrica pode substituir o comum se houver espaço para a cabeça. Nos escareados, a alternativa deve continuar com cabeça chata cônica.',270,9,14)
text(34,407,'3  Parafuso passante com porca',12,True)
xs,xe=screw(56,354,55,4,'pan',3.5,False,False)
for wx in [92,204]:
    C.setFillColor(white); C.setStrokeColor(INK); C.rect(wx,337,3,34,stroke=1,fill=1)
C.setFillColor(LIGHT); C.rect(101,328,97,52,stroke=1,fill=1)
for yy in range(332,380,7): C.line(103,yy,111,yy+5)
C.setFillColor(white); poly([(214,344),(220,339),(231,339),(237,344),(237,364),(231,369),(220,369),(214,364)],1)
text(51,309,'cabeça',8); text(91,292,'arruela',8); text(121,309,'peças fixadas',8); text(194,309,'arruela',8); text(220,292,'porca',8)
wrap(320,367,'As porcas ficam sob o painel de suporte. O túnel pode ser montado em uma base independente, apoiada sobre a bancada. Prever 20 mm livres sob o painel.',235,9,14)
text(34,252,'4  Quantidade para montar × quantidade para comprar',12,True)
y=wrap(34,230,f'Montagem com base bipartida: USAR 42 parafusos, {used_nuts} porcas e {used_washers} arruelas. Compra deste catálogo, incluindo reservas: {purchase_screws} parafusos, {purchase_nuts} porcas e {purchase_washers} arruelas.',W-68,9,14)
y=wrap(34,y-8,'Célula: 2 Allen M4 × 30 no lado fixo e 2 Allen M4 × 20 no móvel; rosca adotada M4, passo 0,7. A04: uma arruela sob cada cabeça. Os quatro parafusos rosqueiam diretamente na célula, sem porcas.',W-68,9,14)
wrap(34,y-8,'Quantidades de uso calculadas por fixação conforme a tabela da página 4. A retenção da alavanca foi considerada com porcas M3. Conferir assentamento, engate e movimento livre na montagem.',W-68,8,12)
C.showPage()

C.save()
print(OUT)
