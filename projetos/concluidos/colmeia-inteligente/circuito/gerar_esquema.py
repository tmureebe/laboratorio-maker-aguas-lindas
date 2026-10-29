from pathlib import Path
from html import escape
import csv

OUT = Path(__file__).resolve().parent
parts = []
INK = '#162431'
WIRE = '#235c50'
ACCENT = '#234f74'

def line(x1, y1, x2, y2, color=WIRE, width=1.8, dash=False):
    parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' stroke-dasharray="5 4"' if dash else '')+'/>')

def path(points, color=WIRE, width=1.8):
    parts.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}"/>')

def text(x, y, value, size=15, anchor='start', weight='normal', color=INK):
    parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{color}">{escape(value)}</text>')

def rect(x,y,w,h,color=INK,fill='white',width=1.7):
    parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" stroke="{color}" fill="{fill}" stroke-width="{width}"/>')

def dot(x,y):
    parts.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="{WIRE}"/>')

def ground(x,y):
    line(x,y,x,y+12)
    for dy,half in [(12,12),(17,8),(22,4)]:
        line(x-half,y+dy,x+half,y+dy,INK)

def power(x,y,name):
    line(x,y,x,y-15)
    path([(x-6,y-9),(x,y-15),(x+6,y-9)],INK)
    text(x,y-23,name,15,'middle','bold',ACCENT)

def net(x,y,name,side='right'):
    # Label anchored directly at an electrical wire endpoint.
    text(x+5 if side=='right' else x-5,y-7,name,14,'start' if side=='right' else 'end',color=ACCENT)

def resistor(x,y1,y2,ref,val,mark=False):
    mid=(y1+y2)/2
    line(x,y1,x,mid-20)
    rect(x-7,mid-20,14,40)
    line(x,mid+20,x,y2)
    text(x+16,mid-4,ref+(' *' if mark else ''),14,weight='bold')
    text(x+16,mid+15,val,14)

def capacitor(x,y1,y2,ref,val):
    mid=(y1+y2)/2
    line(x,y1,x,mid-5)
    line(x-14,mid-5,x+14,mid-5,INK,2)
    line(x-14,mid+5,x+14,mid+5,INK,2)
    line(x,mid+5,x,y2)
    text(x+21,mid-5,ref,14,weight='bold')
    text(x+21,mid+15,val,14)

def pin(x,y,name,side,length=28):
    end=x-length if side=='left' else x+length
    line(x,y,end,y)
    text(x+9 if side=='left' else x-9,y+5,name,14,'start' if side=='left' else 'end')
    return end

def section(x,y,w,title):
    text(x,y,title,17,weight='bold',color=ACCENT)
    line(x,y+12,x+w,y+12,'#b1bec8',1)

parts.append('<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 1680 1188">')
parts.append('<title>Colmeia inteligente — esquema elétrico de interligação</title>')
parts.append('<desc>Reconstrução documental do circuito com ESP32 DevKit V1, dois DHT11, INMP441, MC-38, proteção 1S, conversor boost e duas células 18650 em paralelo. Componentes com asterisco dependem de confirmação na montagem.</desc>')
rect(0,0,1680,1188,'white','white',0)
rect(25,25,1630,1138,width=2)
text(55,70,'COLMEIA INTELIGENTE',29,weight='bold')
text(55,99,'Esquema elétrico de interligação • versão descrita no relatório final / firmware v2.8',16)
text(1625,65,'PIBIC · IFG',18,'end','bold',ACCENT)
text(1625,94,'RECONSTRUÇÃO DOCUMENTAL · REV. A',13,'end')
line(25,115,1655,115,INK,1.4)

section(55,150,1040,'01  ALIMENTAÇÃO — BATERIA 1S2P / SAÍDA REGULADA DE 5 V')
for x,ref in [(105,'BT1'),(215,'BT2')]:
    line(x,220,x,258)
    line(x-20,258,x+20,258,INK,2)
    line(x-10,269,x+10,269,INK,3)
    line(x,269,x,310)
    text(x+27,258,'+',15)
    text(x,348,ref,15,'middle','bold')
    text(x,370,'18650',14,'middle')
line(105,220,300,220)
path([(300,220),(300,230),(370,230)])
line(105,310,330,310)
path([(330,310),(330,300),(370,300)])
dot(215,220);dot(215,310)
text(280,207,'BAT+',13)
text(280,335,'BAT−',13)
text(160,398,'3,7 V nom. · 4,2 V máx.',13,'middle')

rect(370,200,200,130)
pin(370,230,'B+','left',0);pin(370,300,'B−','left',0)
pin(570,230,'P+','right',0);pin(570,300,'P−','right',0)
text(470,250,'U2',16,'middle','bold')
text(470,274,'PROTEÇÃO 1S',15,'middle')
text(470,355,'Módulo BMS / PCM',14,'middle')
text(470,377,'Modelo não identificado',12,'middle')
line(570,230,650,230)
for x in (650,710):
    parts.append(f'<circle cx="{x}" cy="230" r="3" fill="white" stroke="{INK}" stroke-width="1.8"/>')
line(653,228,702,207,INK,2)
line(713,230,850,230)
text(680,185,'SW1',15,'middle','bold')
text(680,268,'SPST',13,'middle')
text(790,215,'+SYS',14,'middle','bold',ACCENT)
path([(570,300),(650,300),(650,330)])
ground(650,330)
text(650,383,'GND = P−',14,'middle')

rect(850,200,200,130)
for x,y,name,side in [(850,230,'IN+','left'),(850,300,'IN−','left'),(1050,230,'OUT+','right'),(1050,300,'OUT−','right')]:pin(x,y,name,side,0)
text(950,253,'U3',16,'middle','bold')
text(950,278,'BOOST DC–DC',14,'middle')
path([(850,300),(820,300),(820,330)]);ground(820,330)
path([(1050,300),(1080,300),(1080,330)]);ground(1080,330)
line(1050,230,1090,230);power(1090,230,'+5V')
text(950,377,'Saída ajustada: 5,0 V',14,'middle')
text(950,398,'Modelo não identificado',12,'middle')

section(1150,150,455,'02  MEDIÇÃO DA BATERIA')
power(1225,225,'+SYS')
resistor(1225,225,310,'R1','100 kΩ')
line(1225,310,1225,330)
dot(1225,330)
line(1225,330,1560,330)
net(1440,330,'BAT_SENSE')
resistor(1225,330,415,'R2','100 kΩ')
line(1225,415,1445,415)
dot(1445,330)
capacitor(1445,330,415,'C1 *','100 nF')
ground(1225,415)
text(1150,467,'V(BAT_SENSE) = V(+SYS) / 2',14,weight='bold')
text(1150,488,'4,2 V na bateria → 2,1 V no GPIO34',13)

section(55,455,495,'03  CONTROLE E AQUISIÇÃO')
rect(180,540,235,375)
text(297,570,'U1',17,'middle','bold')
text(297,592,'ESP32 DevKit V1',17,'middle','bold')
line(180,612,415,612,INK,1)
pin(180,650,'VIN / 5V','left',55);power(125,650,'+5V')
pin(180,870,'GND','left',55);ground(125,870)
for y,name,label in [(650,'3V3','+3V3'),(690,'GPIO4','DHT_EXT'),(720,'GPIO21','DHT_INT'),(755,'GPIO25','I2S_WS'),(785,'GPIO26','I2S_BCLK'),(815,'GPIO33','I2S_SD'),(850,'GPIO27','LID_SW'),(885,'GPIO34','BAT_SENSE')]:
    pin(415,y,name,'right',40)
    if name=='3V3':power(455,y,label)
    else:net(455,y,label)
text(65,945,'Terminais identificados pela serigrafia do DevKit.',13)
text(65,966,'GPIO34: entrada ADC · GPIO27: pull-up interno.',13)

section(590,455,490,'04  TEMPERATURA E UMIDADE')

def dht(y,ref,place,signal,rref):
    # Equivalent external three-wire sensor/module interface; no fabricated header numbers.
    x=855
    rect(x,y,205,145)
    text(x+102,y+30,ref+' · DHT11',16,'middle','bold')
    text(x+102,y+52,place,13,'middle')
    for yy,name in [(y+75,'VCC'),(y+105,'DATA'),(y+130,'GND')]:pin(x,yy,name,'left',0)
    path([(855,y+75),(800,y+75),(800,y-15),(720,y-15)])
    power(720,y-15,'+3V3 †')
    resistor(720,y-15,y+105,rref,'4,7 kΩ',True)
    line(610,y+105,855,y+105);dot(720,y+105)
    net(610,y+105,signal)
    path([(855,y+130),(810,y+130),(810,y+155)]);ground(810,y+155)

dht(540,'U4','Sensor externo','DHT_EXT','R3')
dht(785,'U5','Sensor interno','DHT_INT','R4')

section(1130,535,475,'05  ÁUDIO DIGITAL I²S')
rect(1370,610,225,170)
text(1482,640,'U6 · INMP441',16,'middle','bold')
pin(1482,610,'','left',0)
line(1482,610,1482,590);power(1482,590,'+3V3')
text(1482,627,'VDD',11,'middle')
for y,name,label in [(675,'WS','I2S_WS'),(710,'SCK','I2S_BCLK'),(745,'SD','I2S_SD')]:
    pin(1370,y,name,'left',0)
    line(1190,y,1370,y);net(1190,y,label)
for x,name in [(1450,'GND'),(1540,'L/R')]:
    text(x,769,name,13,'middle')
    line(x,780,x,805)
line(1450,805,1540,805);dot(1450,805);ground(1450,805)
text(1135,805,'L/R = GND: canal esquerdo.',13)

section(1130,870,475,'06  DETECÇÃO DA TAMPA')
line(1160,935,1360,935);net(1160,935,'LID_SW')
for x in (1360,1430):
    parts.append(f'<circle cx="{x}" cy="935" r="3" fill="white" stroke="{INK}" stroke-width="1.8"/>')
line(1363,933,1422,912,INK,2)
line(1433,935,1500,935);ground(1500,935)
text(1395,902,'SW2 · MC-38',14,'middle','bold')
text(1135,980,'Ímã próximo: contato fechado → GPIO27 em LOW.',13)

line(45,1005,1635,1005,INK,1)
text(55,1029,'NOTAS DE RECONSTRUÇÃO',13,weight='bold',color=ACCENT)
text(55,1051,'1. Redes com o mesmo nome são eletricamente comuns; pontos indicam junções.',12)
text(55,1072,'2. BAT− termina em B−. O retorno do circuito é P− (GND), após a proteção.',12)
text(55,1093,'3. U1–U6 representam módulos; os circuitos internos não estão documentados.',12)
text(850,1029,'* R3, R4 e C1: presentes nos desenhos anteriores; montagem final a confirmar.',12)
text(850,1051,'† Alimentação dos DHT11 em 3,3 V herdada da documentação do circuito.',12)
text(850,1072,'   Confirmar tensão, pull-ups e ordem física dos terminais dos módulos instalados.',12)
text(850,1093,'   Pinagem de sinais e R1/R2 conferidos no relatório e no firmware v2.8.',12)

rect(25,1110,1630,53,width=1.5)
for x in (930,1230,1430):line(x,1110,x,1163,INK,1)
text(45,1132,'DOCUMENTO',10,color=ACCENT)
text(45,1153,'CI-EL-001 · Interligações elétricas do protótipo',16,weight='bold')
text(950,1132,'BASE DOCUMENTAL',10,color=ACCENT)
text(950,1153,'Relatório final + firmware v2.8',13)
text(1250,1132,'REVISÃO / DATA',10,color=ACCENT)
text(1250,1153,'A · 14/10/2026',14)
text(1450,1132,'FORMATO / FOLHA',10,color=ACCENT)
text(1450,1153,'A3 · 1/1 · sem escala',13)
parts.append('</svg>')
(OUT/'colmeia_esquema_profissional.svg').write_text('\n'.join(parts),encoding='utf-8')

rows = [
('BAT+','BT1.+; BT2.+; U2.B+','Relatório final e documentação do circuito'),
('BAT-','BT1.-; BT2.-; U2.B-','Negativo das células, distinto de GND'),
('P+','U2.P+; SW1.1','Documentação do circuito'),
('+SYS','SW1.2; U3.IN+; R1.1','Documentação e firmware v2.8'),
('+5V','U3.OUT+; U1.VIN/5V','Documentação do circuito'),
('+3V3','U1.3V3; U4.VCC; U5.VCC; U6.VDD; R3.1; R4.1','DHT11 e pull-ups: confirmar montagem'),
('GND','U2.P-; U3.IN-; U3.OUT-; U1.GND; U4.GND; U5.GND; U6.GND; U6.L/R; R2.2; C1.2; SW2.2','Retorno protegido'),
('BAT_SENSE','R1.2; R2.1; C1.1; U1.GPIO34','R1=R2=100 kΩ; C1=100 nF a confirmar'),
('DHT_EXT','U1.GPIO4; U4.DATA; R3.2','R3=4,7 kΩ a confirmar'),
('DHT_INT','U1.GPIO21; U5.DATA; R4.2','R4=4,7 kΩ a confirmar'),
('I2S_WS','U1.GPIO25; U6.WS','Firmware v2.8'),
('I2S_BCLK','U1.GPIO26; U6.SCK','Firmware v2.8'),
('I2S_SD','U1.GPIO33; U6.SD','Firmware v2.8'),
('LID_SW','U1.GPIO27; SW2.1','INPUT_PULLUP; MC-38 para GND'),
]
with (OUT/'conexoes.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f);w.writerow(['Rede','Terminais lógicos','Observação']);w.writerows(rows)
print(OUT/'colmeia_esquema_profissional.svg')
