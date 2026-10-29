#!/usr/bin/python3
"""Esquemas dimensionais de fabricação, derivados das cotas do projeto."""
from pathlib import Path
import json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'05_VISUALIZACAO'
FONT='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
def font(n):return ImageFont.truetype(FONT,n)
def begin(title,sub,size=(1800,1050)):
    im=Image.new('RGB',size,'#f7f9f9');d=ImageDraw.Draw(im)
    d.text((65,35),title,font=font(38),fill='#164956');d.text((65,98),sub,font=font(22),fill='#526d78')
    return im,d
def arrow(d,a,b,label,pos):
    d.line([a,b],fill='#42606a',width=3)
    if a[1]==b[1]:
        d.polygon([a,(a[0]+10,a[1]-5),(a[0]+10,a[1]+5)],fill='#42606a')
        d.polygon([b,(b[0]-10,b[1]-5),(b[0]-10,b[1]+5)],fill='#42606a')
    else:
        d.polygon([a,(a[0]-5,a[1]+10),(a[0]+5,a[1]+10)],fill='#42606a')
        d.polygon([b,(b[0]-5,b[1]-10),(b[0]+5,b[1]-10)],fill='#42606a')
    d.text(pos,label,font=font(24),fill='#244b59')

im,d=begin('Dutos de MDF 3 mm','Um conjunto de quatro painéis por módulo. Todas as cotas em mm.')
for y,label,w,h in [(210,'PISO / TETO: 2 × 200 × 126',560,190),(520,'LATERAIS: 2 × 200 × 120',560,180)]:
    d.rectangle((95,y,95+w,y+h),fill='#d3ae7d',outline='#7c5e3b',width=4)
    d.text((110,y+25),label,font=font(26),fill='#463322')
    d.text((110,y+78),'M01 + M02 = entrada',font=font(22),fill='#463322')
    d.text((110,y+115),'M03 + M04 = saída',font=font(22),fill='#463322')
    arrow(d,(95,y+h+35),(655,y+h+35),'200',(342,y+h+43))
x,y,s=1060,295,3
E=126*s;t=3*s
d.rectangle((x,y,x+E,y+E),fill='#bd9361',outline='#694d30',width=3)
d.rectangle((x+t,y+t,x+E-t,y+E-t),fill='white',outline='#42606a',width=2)
d.line((x,y+t,x+E,y+t),fill='#694d30',width=3);d.line((x,y+E-t,x+E,y+E-t),fill='#694d30',width=3)
arrow(d,(x,y-60),(x+E,y-60),'126 externo',(x+95,y-100))
arrow(d,(x+t,y+E/2),(x+E-t,y+E/2),'120 interno',(x+95,y+E/2+12))
arrow(d,(x+E+70,y+t),(x+E+70,y+E-t),'120',(x+E+85,y+E/2))
d.text((1010,770),'Laterais entre piso e teto.',font=font(27),fill='#164956')
d.text((1010,820),'126 − 3 − 3 = 120',font=font(25),fill='#42606a')
d.text((65,955),'Montar com esquadro, colar e conferir as duas extremidades antes de selar.',font=font(23),fill='#526d78')
im.save(OUT/'05_duto_paineis.png')

im,d=begin('Base e seis apoios','Vista superior · X medido a partir da entrada · painel 750 × 220 mm')
ox,oy,s=140,265,1.9
d.rectangle((ox,oy,ox+750*s,oy+220*s),fill='#e7d2ae',outline='#896640',width=3)
cuts=json.loads((ROOT/'06_CAD_VALIDACAO/cortes.json').read_text());p={q['id']:q for q in cuts['pecas']}
for id,shift in [('B01',0),('B02',375)]:
    for x,y,r in p[id]['furos']:
        x=ox+(x+shift)*s;y=oy+y*s;rr=r*s;d.ellipse((x-rr,y-rr,x+rr,y+rr),fill='#f7f9f9',outline='#69533a',width=2)
for x,kind in [(25,'M13'),(150,'M13'),(350,'M23'),(450,'M13'),(550,'M13'),(695,'M19')]:
    w=180 if kind=='M19' else 160;xx=ox+x*s
    d.rectangle((xx-12*s,oy+(110-w/2)*s,xx+12*s,oy+(110+w/2)*s),outline='#1d8097' if kind=='M23' else '#9b6c32',width=4)
    d.text((xx-32,oy+220*s+28),str(x),font=font(24),fill='#244b59')
    d.text((xx-36,oy-60),kind,font=font(23),fill='#244b59')
for yy in range(int(oy),int(oy+220*s),18):d.line((ox+375*s,yy,ox+375*s,yy+9),fill='#536d75',width=3)
d.text((ox+375*s-60,oy+220*s+76),'junta 375',font=font(21),fill='#536d75')
d.rectangle((ox+215*s,oy+82*s,ox+267*s,oy+138*s),fill='#7fb6c3',outline='#245b6b',width=3)
d.text((ox+215*s-25,oy+220*s+125),'base da célula',font=font(23),fill='#245b6b')
d.text((130,870),'M13: 16 lâminas → 4 pés   |   M23: 4 lâminas → 1 pé   |   M19: 4 lâminas → 1 pé',font=font(25),fill='#164956')
d.text((130,920),'Cada pé: 4 × 6 = 24 mm. Colar e só depois furar verticalmente com G13/G19.',font=font(24),fill='#526d78')
im.save(OUT/'06_base_apoios.png')

im,d=begin('Interfaces do corpo','Piso interno contínuo Z=62,4 · teto interno Z=182,4 · centro Z=122,4')
ox,oy,s=160,300,2.2
for x,label,mat in [(0,'ENTRADA MDF','#d2ad7b'),(200,'CÂMARA IMPRESSA','#7fb6c3'),(400,'SAÍDA MDF','#d2ad7b')]:
    d.rectangle((ox+x*s,oy,ox+(x+200)*s,oy+265),fill=mat,outline='#385966',width=3)
    d.text((ox+x*s+35,oy+95),label,font=font(25),fill='#193f4a')
    d.text((ox+x*s+150,oy+150),'200 mm',font=font(25),fill='#193f4a')
for x,label in [(188,'U01'),(388,'U02'),(588,'08 MDF')]:
    d.rectangle((ox+x*s,oy-20,ox+(x+24)*s,oy+285),outline='#df793c',width=8)
    d.text((ox+x*s-5,oy-65),label,font=font(26),fill='#aa5321')
for x in (0,200,400,600):d.text((ox+x*s-15,oy+330),str(x),font=font(24),fill='#365661')
d.text((125,800),'U01: MDF 126,4 → câmara 125,2',font=font(30),fill='#164956')
d.text((125,857),'U02: câmara 125,2 → MDF 126,4',font=font(30),fill='#164956')
d.text((125,928),'Inserção de 12 mm por lado. Encostar os módulos e reter/vedar por fora.',font=font(25),fill='#526d78')
im.save(OUT/'07_interfaces.png')
print('Três diagramas dimensionais criados.')
