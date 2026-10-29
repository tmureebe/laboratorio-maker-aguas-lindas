#!/usr/bin/python3
"""Manual formal de pré-compra, revisão 03. Requer ReportLab.
Ilustrações CAD: /usr/bin/python3 manual_medicoes_v7/renderizar_ilustracoes.py
"""
from pathlib import Path
import math,json
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor,white
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parent
ASSET=ROOT/'manual_medicoes_v7/ilustracoes'
OUT=ROOT/'Guia_Ilustrado_Medicoes_Parafusos_V7.pdf'
for name,file in [('D','DejaVuSans.ttf'),('B','DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name,'/usr/share/fonts/truetype/dejavu/'+file))
W,H=A4
INK=HexColor('#1e2a30');TEAL=HexColor('#1d5768');GREY=HexColor('#54636a');LINE=HexColor('#b9c5ca')
PALE=HexColor('#eef3f5');METAL=HexColor('#e1e5e7');PLASTIC=HexColor('#b7cbd2');GLASS=HexColor('#e2f1f4')
C=canvas.Canvas(str(OUT),pagesize=A4,pageCompression=1)
C.setTitle('Manual de medições complementares — compra de ferragens V7 — revisão 03')
C.setAuthor('Laboratório MAKER')

def text(x,y,s,size=10,bold=False,color=INK):
    C.setFont('B' if bold else 'D',size);C.setFillColor(color);C.drawString(x,y,s)

def paragraph(x,y,s,width,size=10.5,leading=15,bold=False,color=INK):
    font='B' if bold else 'D';buf=''
    for word in s.split():
        candidate=(buf+' '+word).strip()
        if buf and pdfmetrics.stringWidth(candidate,font,size)>width:
            text(x,y,buf,size,bold,color);y-=leading;buf=word
        else:buf=candidate
    if buf:text(x,y,buf,size,bold,color);y-=leading
    return y

def line(x1,y1,x2,y2,color=INK,width=.8,dashed=False):
    C.setStrokeColor(color);C.setLineWidth(width);C.setDash(4,3) if dashed else C.setDash()
    C.line(x1,y1,x2,y2);C.setDash()

def rect(x,y,w,h,fill=white,stroke=INK,r=0):
    C.setStrokeColor(stroke);C.setFillColor(fill);C.setLineWidth(.8)
    if r:C.roundRect(x,y,w,h,r,stroke=1,fill=1)
    else:C.rect(x,y,w,h,stroke=1,fill=1)

def poly(points,fill=white,stroke=INK):
    p=C.beginPath();p.moveTo(*points[0])
    for v in points[1:]:p.lineTo(*v)
    p.close();C.setStrokeColor(stroke);C.setFillColor(fill);C.drawPath(p,stroke=1,fill=1)

def circle(x,y,r,fill=white,stroke=INK):
    C.setFillColor(fill);C.setStrokeColor(stroke);C.circle(x,y,r,stroke=1,fill=1)

def tip(x,y,a,size=4):
    a=math.radians(a);poly([(x,y),(x-size*math.cos(a-.4),y-size*math.sin(a-.4)),(x-size*math.cos(a+.4),y-size*math.sin(a+.4))],TEAL,TEAL)

def arrow(x1,y1,x2,y2):
    line(x1,y1,x2,y2,TEAL);tip(x2,y2,math.degrees(math.atan2(y2-y1,x2-x1)))

def dim(x1,y1,x2,y2,label,vertical=False):
    line(x1,y1,x2,y2,TEAL,.6)
    a=math.degrees(math.atan2(y2-y1,x2-x1));tip(x1,y1,a+180);tip(x2,y2,a)
    if vertical:
        C.saveState();C.translate(x1+11,(y1+y2)/2);C.rotate(90)
        tw=pdfmetrics.stringWidth(label,'B',9);rect(-tw/2-3,-3,tw+6,13,white,white);text(-tw/2,0,label,9,True,TEAL);C.restoreState()
    else:
        tw=pdfmetrics.stringWidth(label,'B',9);rect((x1+x2-tw)/2-3,y1-3,tw+6,13,white,white);text((x1+x2-tw)/2,y1,label,9,True,TEAL)

def tag(x,y,s):
    circle(x,y,10,white,TEAL);tw=pdfmetrics.stringWidth(s,'B',8);text(x-tw/2,y-3,s,8,True,TEAL)

def section(y,s):
    text(48,y,s,11.5,True,TEAL)

def caption(y,s):
    paragraph(48,y,s,W-96,8.5,12,color=GREY)

def begin(n,title,sub):
    C.bookmarkPage('p'+str(n));C.addOutlineEntry(f'{n}. {title}','p'+str(n),0)
    text(48,807,'LABORATÓRIO MAKER  |  TÚNEL DE VENTO V7',8,True,TEAL)
    text(405,807,'MM-V7  •  REV. 03',8,True,TEAL)
    line(48,794,W-48,794,TEAL,1.2)
    text(48,756,title,23,True)
    paragraph(48,732,sub,W-96,10.5,15,color=GREY)
    line(48,45,W-48,45,LINE,.6)
    text(48,29,'13/10/2026  •  Medidas em mm  •  Ilustrações sem escala',7.5,color=GREY)
    text(490,29,f'{n} / 5',8,True,TEAL)

def end():C.showPage()

def note(y,title,body):
    rect(48,y-51,W-96,69,PALE,LINE)
    text(60,y,title,10,True,TEAL)
    paragraph(60,y-18,body,W-120,9.5,14)

def table(y,widths,headers,rows,rowh=30,size=9,headh=33):
    x=48;total=sum(widths);rect(x,y-headh,total,headh,PALE,LINE)
    xx=x
    for width,s in zip(widths,headers):
        paragraph(xx+7,y-13,s,width-14,size,12,True);xx+=width
    y-=headh
    for row in rows:
        rect(x,y-rowh,total,rowh,white,LINE);xx=x
        for width,s in zip(widths,row):
            paragraph(xx+7,y-13,s,width-14,size,12);xx+=width
            if xx<x+total-.1:line(xx,y,xx,y-rowh,LINE,.5)
        y-=rowh
    return y

def field(x,y,label,width=499):
    text(x,y,label,9.5);lw=pdfmetrics.stringWidth(label,'D',9.5);line(x+lw+7,y-1,x+width,y-1,LINE,.6)

def tick(x,y,label):
    rect(x,y-1,8,8);text(x+15,y,label,9.5)

# Página 1: objetivo, escopo e medidas já conhecidas.
begin(1,'Manual de medições complementares','Procedimento para definir as ferragens antes da compra.')
section(691,'1. Objetivo e preparação')
paragraph(48,669,'Levantar apenas os dados que o modelo digital não confirma: os furos da célula de carga e as características da ventoinha real.',279,11,16)
paragraph(48,605,'Material: paquímetro de 200 mm, célula, ventoinha e identificação dos componentes. Não é necessário ter ferragens.',279,10.5,15)
C.drawImage(str(ASSET/'conjunto_sensor.png'),338,471,width=210,height=210,mask='auto')
text(360,458,'Conjunto de medição V7',8.5,color=GREY)
section(538,'Sequência de trabalho')
for yy,label,page in [(515,'01  Célula de carga: quatro furos',2),(491,'02  Ventoinha: dados não documentados',3),(467,'03  Registrar e fechar a compra',5)]:
    text(48,yy,label,10)
    C.linkRect('',f'p{page}',(48,yy-4,326,yy+13),relative=0,thickness=0)
section(417,'2. Cotas já definidas no modelo digital')
table(397,[299,200],['Local','Cota nominal — usar na conta'],[
    ['Célula — fixação inferior, base 14','17 mm antes da rosca'],
    ['Célula — fixação superior, peças 15 + 16','8 mm antes da rosca'],
    ['Janela — câmara + moldura + espaçador + presilha','20,5 mm, sem ferragens'],
    ['Grade — parte 1 + grade + espaçador + parte 2','31,2 mm, sem ferragens'],
],37,9.4)
paragraph(48,193,'Essas cotas foram extraídas das malhas montadas da V7. Não é preciso medi-las novamente para este levantamento. Quantidades e parafusos de referência estão na página 4.',499,10.5,15)
paragraph(48,127,'Aplicação: peças conforme a V7. Se alguma peça, painel ou montagem foi alterada, identifique somente essa alteração na ficha da página 5.',499,10,15)
caption(76,'Fonte das cotas: STL de montagem e documentos V7. Roscas e componentes comerciais dependem da peça real.')
end()

# Página 2: célula com furos identificados sobre a própria malha.
begin(2,'Célula de carga','Procedimento 01  |  Identificar os quatro furos e seus limites de entrada.')
section(691,'2.1  Identifique a rosca')
paragraph(48,669,'Marque F1/F2 no lado fixo e M1/M2 no lado móvel. Consulte o modelo/manual da célula; se não houver informação, leve-a à loja para identificar a rosca e o passo.',499,10.5,15)
x0,y0,ww,hh=80,420,435,217.5
C.drawImage(str(ASSET/'celula_identificacao.png'),x0,y0,width=ww,height=hh,mask='auto')
points=json.loads((ASSET/'celula_pontos.json').read_text())
for label,(px,py) in points.items():
    x=x0+px/2000*ww;y=y0+(1000-py)/1000*hh
    tag(x,y+53,label);arrow(x,y+42,x,y+4)
caption(427,'Figura 1 — Identificação dos furos. Forma de referência do CAD; os furos desenhados não especificam a rosca real.')
section(389,'2.2  Observe o fundo e consulte o limite de entrada')
# Corte do furo cego, com apoio do paquímetro na boca e haste de profundidade.
rect(76,200,161,138,METAL)
poly([(130,338),(130,226),(157,216),(184,226),(184,338)],white)
for yy in range(244,332,9):
    line(130,yy,137,yy+4,GREY,.5);line(177,yy+4,184,yy,GREY,.5)
# Instrumento ilustrado em detalhe, apoiado na entrada.
rect(119,338,76,38,METAL)
rect(155,216,3,122,PLASTIC,TEAL)
line(119,338,130,338,TEAL,1.5);line(184,338,195,338,TEAL,1.5)
for yy in range(344,372,7):line(123,yy,135,yy,GREY,.5)
dim(61,338,61,216,'profundidade física',True)
arrow(258,354,188,339);text(245,369,'Apoiar na entrada',8.5,True,TEAL)
arrow(252,251,159,267);text(246,266,'Haste',8.5,True,TEAL)
paragraph(301,353,'1. Registre se o furo tem fundo ou atravessa a célula.',245,10.5,15)
paragraph(301,309,'2. Se houver fundo, meça da entrada até o primeiro fundo, sem pressionar a haste.',245,10.5,15)
paragraph(301,249,'3. Obtenha a entrada mínima e máxima permitidas no manual da célula ou por avaliação apropriada.',245,10.5,15)
caption(183,'Figura 2 — Medição da profundidade física de um furo cego. Em furo passante, registre essa condição e a restrição de saída.')
note(126,'Registro na ficha: página 5','Profundidade física não é comprimento de rosca útil. Se os limites permitidos forem desconhecidos, deixe o comprimento do parafuso pendente.')
end()

# Página 3: ventoinha, instrumentação e dados que não são confirmados pelo CAD.
begin(3,'Ventoinha','Procedimento 02  |  Confirmar espessura e furação do componente real.')
paragraph(48,688,'Se a documentação da ventoinha confirma 30 mm de espessura nos furos e passo de 105 × 105 mm, registre a fonte e pule a medição. Caso contrário, siga abaixo.',499,10.5,15)
# Vista frontal.
fx,fy,side=77,443,190
rect(fx,fy,side,side,METAL,INK,9)
circle(fx+95,fy+95,77,white)
for angle in range(0,360,60):
    C.saveState();C.translate(fx+95,fy+95);C.rotate(angle)
    p=C.beginPath();p.moveTo(12,8);p.curveTo(31,57,61,66,58,29);p.curveTo(47,14,27,1,12,8);p.close()
    C.setFillColor(PLASTIC);C.setStrokeColor(GREY);C.drawPath(p,stroke=1,fill=1);C.restoreState()
circle(fx+95,fy+95,23,METAL)
for lab,x,y in [('C1',fx+13,fy+177),('C2',fx+177,fy+177),('C3',fx+13,fy+13),('C4',fx+177,fy+13)]:
    circle(x,y,5,white)
    text(x-7,y-22 if '3' in lab or '4' in lab else y+12,lab,8,True,TEAL)
line(fx+13,fy+177,fx+13,646,LINE);line(fx+177,fy+177,fx+177,646,LINE)
dim(fx+13,646,fx+177,646,'105 mm no CAD')
line(fx+177,fy+13,291,fy+13,LINE);line(fx+177,fy+177,291,fy+177,LINE)
dim(290,fy+13,290,fy+177,'105 mm no CAD',True)
# Vista lateral e paquímetro com bicos nas faces do flange.
rect(391,459,54,155,METAL)
line(391,480,445,480,GREY);line(391,593,445,593,GREY)
rect(357,643,174,12,METAL)
for xx in range(365,527,7):line(xx,649,xx,655,GREY,.4)
poly([(383,643),(391,643),(391,588),(386,584),(383,599)],METAL)
rect(445,635,43,29,METAL,INK,2)
rect(450,644,31,13,white,GREY);text(457,647,'mm',7)
poly([(445,635),(453,635),(453,599),(450,584),(445,588)],METAL)
line(391,459,391,433,LINE);line(445,459,445,433,LINE)
dim(391,434,445,434,'espessura')
# O paquímetro é identificado pelo desenho e pela legenda da figura.
arrow(494,572,445,601);paragraph(478,561,'Contato no ponto de fixação',69,8.5,11,color=GREY)
caption(412,'Figura 3 — À esquerda: furação de referência. À direita: medir a espessura entre as faces de apoio no canto da ventoinha.')
section(370,'3.1  Meça a espessura nos quatro cantos')
paragraph(48,348,'Encoste os bicos externos do paquímetro nas duas faces do canto, como na figura. Repita em C1 a C4 e anote os valores. A ventoinha deve estar desconectada.',499,10.5,15)
section(292,'3.2  Confira a distância entre os furos')
paragraph(48,270,'Registre a distância entre centros na horizontal e na vertical. Para dois furos iguais: distância externa entre os furos menos o diâmetro de um furo.',499,10.5,15)
paragraph(48,220,'Compare com 105 × 105 mm. Se a furação for diferente, registre a diferença: trocar o comprimento do parafuso não corrige o alinhamento.',499,10.5,15)
note(141,'Resultado esperado','Espessuras nos cantos + distância horizontal e vertical, ou documentação que confirme esses dados. Somente este grupo precisa ser revisto se a ventoinha diferir da referência.')
end()

# Página 4: corte dimensional coerente com as peças da janela.
begin(4,'Referências para a compra','Usar as cotas digitais e completar apenas os dados que faltam.')
section(692,'4.1  Janela: pilha nominal de 20,5 mm')
# Coordenadas y-z da montagem; recorte técnico na linha x=240.
ox,oy,scale=70,486,5.5
X=lambda y: ox+(y-45)*scale
Y=lambda z: oy+(z-170.8)*scale
# Orelha, moldura, espaçador e presilha com seção do furo mostrada.
for lo,hi,z,h,fill in [(60,77,170.8,10,PLASTIC),(54,77,180.8,4,PLASTIC),(65,73,184.8,3.5,METAL),(53,73,188.3,3,PLASTIC)]:
    rect(X(lo),Y(z),X(hi)-X(lo),h*scale,fill)
    rect(X(67.3),Y(z),3.4*scale,h*scale,white,white)
    line(X(67.3),Y(z),X(67.3),Y(z+h),GREY,.6);line(X(70.7),Y(z),X(70.7),Y(z+h),GREY,.6)
rect(X(45),Y(185.3),X(60)-X(45),3*scale,GLASS)
rect(X(54),Y(184.8),X(60)-X(54),.5*scale,METAL)
line(X(69),Y(170.8)-8,X(69),Y(191.3)+13,TEAL,.8,True)
line(X(77)+5,Y(170.8),285,Y(170.8),LINE)
line(X(73)+5,Y(191.3),285,Y(191.3),LINE)
dim(281,Y(170.8),281,Y(191.3),'20,5 mm',True)
for i,z in [(1,189.8),(2,186.55),(3,182.8),(4,175.8)]:
    tx=X(73)+25 if i==1 else (X(73)+17 if i==2 else X(77)+14)
    tag(tx,Y(z),str(i))
arrow(83,624,X(58),Y(186.5));text(56,637,'Acrílico sem furo',9,True,TEAL)
for yy,label in [(657,'1  Presilha: 3 mm'),(637,'2  Espaçador: 3,5 mm'),(617,'3  Moldura no furo: 4 mm'),(597,'4  Orelha da câmara: 10 mm')]:
    text(332,yy,label,9.5)
paragraph(332,564,'O fornecedor soma a esta pilha as arruelas, a porca e a sobra necessária.',213,10,14)
paragraph(332,518,'M3 × 25 é a referência inicial. Defina o comprimento com a ferragem oferecida, sem medir a janela novamente.',213,9.5,13)
caption(465,'Figura 4 — Corte da fixação da janela V7, sem ferragens. A tampa fica ao lado do eixo do parafuso.')
section(434,'4.2  Parafusos do projeto')
table(416,[33,155,158,153],['Qtd.','Uso','Referência V7','Complemento'],[
    ['2','Célula — lado fixo','A definir (p. 2)','Pilha CAD: 17 mm'],
    ['2','Célula — lado móvel','A definir (p. 2)','Pilha CAD: 8 mm'],
    ['6','Janela','M3; comprimento a definir','Pilha CAD: 20,5 mm'],
    ['16','Pés + base do sensor','M4 × 20','Painel conforme V7'],
    ['4','Ventoinha','M4 × 55','Confirmar página 3'],
    ['4','Grade e espaçador','M3 × 40','Pilha CAD: 31,2 mm'],
    ['1','Eixo da asa','M3 × 35','Conforme V7'],
    ['1','Eixo do regulador','M4 × 20','Arruela: Ø externo ≈ 12'],
    ['2','Disco e alavanca','M3 escareado × 12','Definir retenção*'],
    ['4','Talas — opcionais','M4 escareado × 20','Só base bipartida'],
],23,8.5,29)
paragraph(48,142,'Célula: o comprimento deve atravessar a pilha CAD + arruela e entrar na célula dentro dos limites confirmados. Peça à loja para selecionar o parafuso com esses dados.',499,9.5,13)
paragraph(48,103,'* A retenção da alavanca (porca ou rosca receptora) precisa ser definida. Não exige repetir as dimensões do disco. Total: 38 parafusos; 42 com talas.',499,9,13)
text(48,67,'Parafusos de máquina; cabeça comum, salvo indicação de cabeça escareada.',8.5,color=GREY)
end()

# Página 5: ficha única com apenas as pendências da peça comercial.
begin(5,'Ficha de levantamento','Preencher nas páginas 2 e 3 e levar ao fornecedor para fechar o pedido.')
field(48,688,'Responsável / data:')
field(48,661,'Identificação da célula:')
section(626,'5.1  Célula de carga')
table(607,[34,123,72,90,90,90],['Furo','Rosca e passo','Cego / passante','Profundidade física','Entrada mínima','Entrada máxima'],[
    ['F1','','','','',''],['F2','','','','',''],['M1','','','','',''],['M2','','','','',''],
],35,8.5,38)
field(48,407,'Fonte dos limites de entrada (manual / avaliação):')
paragraph(48,385,'Rosca não identificada ou limite desconhecido: registrar “pendente”. O paquímetro mede a profundidade física, mas não confirma a rosca nem o engate permitido.',499,9,13)
section(334,'5.2  Ventoinha')
field(48,310,'Modelo / documentação utilizada:')
text(48,283,'Espessuras: C1 ________   C2 ________   C3 ________   C4 ________',9.5)
text(48,256,'Distância entre centros: horizontal __________   vertical __________',9.5)
section(219,'5.3  Alterações em relação ao projeto')
tick(48,195,'Peças e painel conforme V7.');tick(279,195,'Há alteração: informar abaixo.')
field(48,170,'Alteração de painel, vedação, peça ou montagem:')
section(132,'5.4  Preenchimento com o fornecedor')
text(48,109,'Comprimentos definidos: célula fixa ______  móvel ______  janela ______',9.5)
text(48,88,'Anexar especificação das arruelas/porcas usadas na escolha dos comprimentos.',9,color=GREY)
end()
C.save()
print(OUT)
def exportar_roteiro():
    import html
    import re
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    pdfmetrics.registerFontFamily('D', normal='D', bold='B', italic='D', boldItalic='B')
    styles = getSampleStyleSheet()
    for name in ('Normal', 'Heading1', 'Heading2'):
        styles[name].fontName = 'D' if name == 'Normal' else 'B'
    styles['Normal'].fontSize = 9.5
    styles['Normal'].leading = 14
    styles['Normal'].spaceAfter = 8
    styles['Heading1'].fontSize = 21
    styles['Heading1'].leading = 27
    styles['Heading1'].textColor = TEAL
    styles['Heading2'].fontSize = 14
    styles['Heading2'].leading = 19
    styles['Heading2'].textColor = TEAL
    styles.add(ParagraphStyle('Cell', parent=styles['Normal'], fontSize=8, leading=11, spaceAfter=0))

    def inline(value):
        value = html.escape(value)
        value = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', value)
        return re.sub(r'\[([^]]+)\]\(([^)]+)\)', r'\1', value)

    story, rows = [], []

    def flush():
        if not rows:
            return
        n = len(rows[0])
        widths = [525/n]*n if n != 3 else [118, 97, 310]
        obj = Table([[Paragraph(inline(v), styles['Cell']) for v in row] for row in rows],
                    colWidths=widths, repeatRows=1)
        obj.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), PALE),
            ('GRID', (0, 0), (-1, -1), .5, LINE),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.extend([obj, Spacer(1, 10)])
        rows.clear()

    for value in (ROOT/'Passo_a_Passo_Medicoes_Parafusos_V7.md').read_text().splitlines():
        if value.startswith('|'):
            cells = [v.strip() for v in value.strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+', v) for v in cells):
                rows.append(cells)
            continue
        flush()
        if not value.strip():
            continue
        if value.startswith('#'):
            level = len(value)-len(value.lstrip('#'))
            style = styles['Heading1' if level == 1 else 'Heading2']
            value = value[level:].strip()
        else:
            style = styles['Normal']
        story.append(Paragraph(inline(value), style))
    flush()

    def footer(c, doc):
        c.setFont('D', 7)
        c.setFillColor(GREY)
        c.drawString(35, 23, 'Túnel V7 · medições antes da compra · revisão 13/10/2026 · mm')
        c.drawRightString(W-35, 23, str(doc.page))

    out = ROOT/'Passo_a_Passo_Medicoes_Parafusos_V7.pdf'
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=35, rightMargin=35,
                      topMargin=35, bottomMargin=47,
                      title='Medições antes da compra das ferragens — Túnel V7',
                      author='Laboratório MAKER').build(story, onFirstPage=footer, onLaterPages=footer)
    print(out)

exportar_roteiro()
