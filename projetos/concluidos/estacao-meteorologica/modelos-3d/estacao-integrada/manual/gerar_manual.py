from pathlib import Path
from math import atan2, cos, sin, pi
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle

D=Path(__file__).resolve().parent
OUT=D.parent/'manual_testes_encaixes.pdf'
for n,f in [('Regular','DejaVuSans.ttf'),('Bold','DejaVuSans-Bold.ttf')]:
 pdfmetrics.registerFont(TTFont(n,'/usr/share/fonts/truetype/dejavu/'+f))
pdfmetrics.registerFontFamily('Regular',normal='Regular',bold='Bold',italic='Regular',boldItalic='Bold')
W,H=A4
NAVY=HexColor('#213E50');TEAL=HexColor('#468E99');ORANGE=HexColor('#D58C3E');GRAY=HexColor('#44535C');PALE=HexColor('#EEF5F6')
c=canvas.Canvas(str(OUT),pagesize=A4)
c.setTitle('Manual ilustrado — testes dos encaixes da estação meteorológica')
c.setAuthor('Laboratório Maker — estação meteorológica')
styles={}
for size in [9,9.5,10,10.5,11,12,14]:
 styles[size]=ParagraphStyle(str(size),fontName='Regular',fontSize=size,leading=size*1.42,textColor=GRAY,spaceAfter=0)

def text(txt,x,y,w=511,size=10.5):
 p=Paragraph(txt,styles[size]);_,h=p.wrap(w,900);p.drawOn(c,x,y-h)
 assert y-h>45, f'Texto fora da página: {txt[:60]}'
 return y-h

def title(txt,x,y,size=14):
 c.setFillColor(NAVY);c.setFont('Bold',size);c.drawString(x,y,txt)

def page(num,titulo,sub):
 c.setFillColor(TEAL);c.rect(0,H-14,W,14,fill=1,stroke=0)
 c.setFillColor(NAVY);c.setFont('Bold',10);c.drawString(42,H-45,'ESTAÇÃO METEOROLÓGICA  /  MANUAL DE BANCADA')
 fs=22
 while pdfmetrics.stringWidth(titulo,'Bold',fs)>511: fs-=.5
 title(titulo,42,H-80,fs)
 text(sub,42,H-94,size=10)
 c.setStrokeColor(HexColor('#CFDDE0'));c.line(42,42,W-42,42)
 c.setFont('Regular',8);c.setFillColor(GRAY);c.drawString(42,28,'Modelo integrado • revisão dimensional R2 • 04/11/2026')
 c.drawRightString(W-42,28,f'{num} / 6')

def box(txt,x,y,w,h,color=PALE,size=10.5):
 c.setFillColor(color);c.roundRect(x,y-h,w,h,7,fill=1,stroke=0)
 text(txt,x+12,y-10,w-24,size)

def image(nome,x,y,w,h):
 c.drawImage(str(D/'figuras'/nome),x,y-h,w,h,preserveAspectRatio=True,anchor='c',mask='auto')

def arrow(x1,y1,x2,y2,color=ORANGE):
 c.setStrokeColor(color);c.setFillColor(color);c.setLineWidth(2)
 c.line(x1,y1,x2,y2);a=atan2(y2-y1,x2-x1)
 p=c.beginPath();p.moveTo(x2,y2);p.lineTo(x2-8*cos(a-.4),y2-8*sin(a-.4));p.lineTo(x2-8*cos(a+.4),y2-8*sin(a+.4));p.close();c.drawPath(p,stroke=0,fill=1)

def step(n,txt,y,w=475):
 c.setFillColor(TEAL);c.circle(53,y-8,10,fill=1,stroke=0);c.setFillColor(white);c.setFont('Bold',10);c.drawCentredString(53,y-11,str(n))
 return text(txt,73,y+1,w-31,10.5)-12

page(1,'Antes de começar','Três arquivos de teste; duas peças separadas em cada arquivo.')
y=text('Use as amostras para verificar <b>entrada, retenção e desmontagem</b> dos encaixes. Faça os testes à mão, sobre uma mesa, com as peças sem eletrônica e sem carga adicional.',42,711)
box('<b>Prepare as peças</b><br/>Use o mesmo material, orientação e perfil previstos para as peças finais. Retire suportes e fios de impressão; confira se canais, janelas e fendas estão livres. Remova apenas rebarbas: lixar superfícies de encaixe altera o resultado.',42,655,511,83)
for yy,nome,rot,desc in [
 (548,'teste_baioneta','01 • Baioneta','Azul: soquete com canais internos. Laranja: tubo com três pinos.'),
 (412,'teste_tampa','02 • Tampa da caixa','Azul: plaqueta com janela. Laranja: lingueta com gancho e aba.'),
 (276,'teste_aletas','03 • Aletas do abrigo','Azul: receptor com furo. Laranja: pino bipartido com apoios.')]:
 title(rot,42,yy,12);text(nome+'.stl',330,yy+10,220,9)
 image(nome+'.png',80,yy-10,430,82)
 text(desc,42,yy-96,511,10)
box('<b>Use os arquivos da revisão R2.</b> A plaqueta da tampa tem <b>16 mm de altura</b>; a peça laranja possui uma guia externa para reproduzir a folga de 0,3 mm. O canal da baioneta também foi corrigido. Reimprima <b>teste_tampa.stl</b> e <b>teste_baioneta.stl</b> anteriores; os testes das aletas permanecem iguais.',42,139,511,82,size=9.5)
c.showPage()

page(2,'Teste 01 • Baioneta','Arquivo: STL/teste_baioneta.stl • reproduz os três pinos da união caixa–abrigo.')
text('<b>Posição de uso:</b> vire as duas peças em relação à impressão. No soquete azul, a aba larga fica para cima e o cilindro para baixo. No tubo laranja, o colar fica para cima e os pinos entram por baixo dele no soquete.',42,711)
for x,fig,label in [(42,'alinhar','A • Alinhar e inserir'),(216,'girar','B • Girar 30°'),(390,'travado','C • Deixar assentar')]:
 image('baioneta_'+fig+'.png',x,640,163,145)
 text('<b>'+label+'</b>',x,488,163,10)
y=455
y=step(1,'Segure a aba do soquete. Alinhe os <b>três pinos</b> do tubo às três entradas. Desça o tubo reto até alcançar o caminho de giro.',y)
y=step(2,'Gire aproximadamente <b>30° no sentido anti-horário, visto de cima</b>, olhando para o colar do tubo. Siga o canal; não tente atravessar um batente.',y)
y=step(3,'Ao chegar ao fim do giro, deixe o tubo <b>descer 1,2 mm</b>. O colar deve apoiar na aba do soquete. Confira com uma tentativa suave de retorno: ele deve ficar bloqueado enquanto está assentado.',y)
y=step(4,'Para soltar: <b>levante cerca de 1,2 mm</b>, gire 30° no sentido horário, alinhe às entradas e retire. Segure o soquete durante todo o movimento.',y)
box('<b>Aprovado:</b> entra e gira com esforço manual moderado, assenta, resiste à retirada direta suave e libera pela sequência levantar → girar → retirar.<br/><b>Rever:</b> pinos raspam muito, não chega ao assento, sai ao puxar sem girar ou volta de giro sem levantar.',42,203,511,85)
text('<b>Repita 5 ciclos como triagem inicial.</b> Marque o ponto alinhado com lápis para perceber os 30° e observar se o encaixe piora. Esses ciclos são uma verificação de bancada, sem certificar a vida útil ou a carga suportada.',42,100,511,10)
c.showPage()

page(3,'Teste 02 • Trava da tampa','Arquivo: STL/teste_tampa.stl • a plaqueta receptora revisada tem 16 mm de altura.')
image('teste_tampa.png',42,713,270,120)
text('Peças como saem da impressão.',58,584,270,9)
image('tampa_montada.png',340,713,185,150)
text('Aba apoiada no topo da plaqueta.',326,557,220,9)
# Corte esquemático da trava, ampliado.
title('Como a trava trabalha • corte esquemático, sem escala',42,526,11)
c.setFillColor(TEAL);c.rect(339,436,18,65,fill=1,stroke=0);c.rect(339,407,18,9,fill=1,stroke=0)
c.setFillColor(ORANGE);c.rect(296,501,85,10,fill=1,stroke=0);c.rect(316,417,9,84,fill=1,stroke=0)
p=c.beginPath();p.moveTo(325,419);p.lineTo(347,432);p.lineTo(347,436);p.lineTo(325,436);p.close();c.drawPath(p,stroke=0,fill=1)
arrow(379,426,333,426)
text('Janela: pressione o gancho para dentro para soltar.',42,492,225,10)
text('Azul = parede da caixa<br/>Laranja = tampa e lingueta',42,449,220,9.5)
y=385
y=step(1,'Mantenha a <b>plaqueta em pé</b>, com a janela perto de baixo. Vire a amostra laranja: aba horizontal em cima, lingueta apontando para baixo.',y)
y=step(2,'Encaixe a plaqueta <b>entre a lingueta e a guia externa</b> da peça laranja. O gancho fica voltado para a janela. A guia encosta na face externa e reproduz a folga interna de <b>0,3 mm</b>.',y)
y=step(3,'Desça a aba devagar. A rampa do gancho encosta na parede e a lingueta flexiona. Continue até o gancho alcançar a janela e voltar para fora. O clique pode ser discreto.',y)
y=step(4,'Puxe a aba suavemente para conferir retenção. Para abrir, <b>aperte o gancho pela janela</b> e levante a aba ao mesmo tempo. Uma pinça pode ajudar a apertar, sem torcer a lingueta.',y)
box('<b>Aprovado:</b> aba assenta no topo, gancho aparece na janela, prende e solta ao apertar. Repita 5 ciclos.<br/><b>Rever:</b> aba não assenta, gancho não retorna, a lingueta fica deformada ou aparece uma trinca. Esta amostra testa <b>uma trava</b>; não testa a folga de todo o contorno da tampa.',42,140,511,82,size=10)
c.showPage()

page(4,'Teste 03 • Pinos das aletas','Arquivo: STL/teste_aletas.stl • reproduz uma das três uniões de cada nível.')
image('teste_aletas.png',42,715,265,110)
text('Azul: furo receptor. Laranja: cabeça dividida em duas metades.',42,594,265,9)
image('aletas_alinhar.png',337,715,190,166)
text('Peças na posição de montagem.',320,545,230,9)
title('Comprima as duas metades para liberar • esquema sem escala',42,511,11)
c.setFillColor(ORANGE);c.rect(298,470,100,9,fill=1,stroke=0)
c.rect(329,415,7,55,fill=1,stroke=0);c.rect(342,415,7,55,fill=1,stroke=0)
c.setFillColor(TEAL);c.rect(287,435,41,10,fill=1,stroke=0);c.rect(350,435,42,10,fill=1,stroke=0)
c.setFillColor(ORANGE);c.rect(324,413,12,7,fill=1,stroke=0);c.rect(342,413,12,7,fill=1,stroke=0)
arrow(302,417,323,417);arrow(377,417,355,417)
text('A cabeça fica abaixo do prato receptor. A fenda permite que as metades se aproximem.',42,484,220,10)
y=389
y=step(1,'Identifique a peça com <b>pino bipartido</b> e a peça com <b>furo</b>. A peça do furo também tem apoios e uma ponte: esses elementos são parte do receptor.',y)
y=step(2,'Vire as duas peças em relação à impressão. Mantenha o <b>pino apontando para baixo</b>, sobre o furo da peça receptora. Alinhe antes de pressionar.',y)
y=step(3,'Pressione junto ao eixo do pino. As metades da cabeça devem se aproximar, atravessar o furo e expandir abaixo dele. Pare quando os <b>apoios encostarem</b>. Não force além desse ponto.',y)
y=step(4,'Para soltar, alcance a cabeça pelas janelas laterais do receptor. <b>Comprima as duas metades para o centro da fenda</b> e levante a peça de cima. Não puxe apenas pela placa.',y)
box('<b>Aprovado:</b> apoios encostam, cabeça atravessa e expande, peças ficam retidas e desmontam ao comprimir. Repita 5 ciclos.<br/><b>Rever:</b> a cabeça para no meio, fenda está unida por material, pino fica torto ou não volta a abrir. Na peça final, confira depois os <b>três encaixes simultâneos</b>.',42,141,511,83,size=10)
c.showPage()

page(5,'Se o encaixe não funcionar','Mude um parâmetro por vez. Os exemplos abaixo são pequenos passos para uma nova tentativa.')
text('Antes de alterar o desenho, confira orientação, rebarbas e material preso nas fendas. Marque cada par de amostras com a revisão. Não misture peças produzidas com ajustes diferentes.',42,711)
rows=[['O que aconteceu','Ajuste a experimentar / observação'],
 ['Baioneta: corpo do tubo prende no soquete','folga_tubo: 0,30 → 0,35 mm radial. Verifique também a primeira camada alargada nas bordas.'],
 ['Baioneta: pinos não entram nas entradas ou raspam ao girar','Confira alinhamento e canais livres. Se o corpo passa bem, folga_angular_baioneta: 1 → 1,2°.'],
 ['Baioneta: pino prende na altura do canal','Confira o acabamento. folga_axial_baioneta: 0,30 → 0,35 mm. Confira novamente assento e retenção.'],
 ['Baioneta: não bloqueia o retorno','Confira se chegou ao fim e desceu 1,2 mm. Não aumente folgas para tratar falta de retenção.'],
 ['Tampa: gancho exige muita força para entrar','ressalto_tampa: 0,90 → 0,80 mm. Reavalie a retenção depois de imprimir o novo par.'],
 ['Tampa: amostra funciona, contorno da tampa final prende','A amostra não mede o contorno. No conjunto final, folga_tampa: 0,30 → 0,35 mm por lado.'],
 ['Aletas: corpo do pino prende no furo','folga_encaixe: 0,30 → 0,35 mm radial. A cabeça também cresce com esse parâmetro: reavalie a passagem dela.'],
 ['Aletas: cabeça não passa, mas o corpo tem folga','Confira se a fenda está livre. ressalto_trava: 0,50 → 0,40 mm reduz a retenção e a flexão necessária.'],
 ['Qualquer trava trinca ou fica deformada','Separe a peça. Confira impressão e orientação; reduza o esforço de encaixe antes de repetir. Não aprove um par com dano.']]
data=[[Paragraph(s,styles[9]) for s in row] for row in rows]
t=Table(data,colWidths=[179,332]);t.setStyle(TableStyle([
 ('BACKGROUND',(0,0),(-1,0),NAVY),('TEXTCOLOR',(0,0),(-1,0),white),
 ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),
 ('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),
 ('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,white]),('LINEBELOW',(0,0),(-1,0),1,TEAL)]))
# As células de cabeçalho usam um estilo próprio para manter o texto branco.
for j,s in enumerate(rows[0]):
 st=ParagraphStyle('cab',parent=styles[9],textColor=white,fontName='Bold');data[0][j]=Paragraph(s,st)
t=Table(data,colWidths=[179,332],style=t._cellStyles if False else None)
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),NAVY),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('ROWBACKGROUNDS',(0,1),(-1,-1),[PALE,white])]))
_,th=t.wrap(511,700);t.drawOn(c,42,653-th)
y=653-th-25
title('Como produzir a próxima revisão',42,y,12)
y-=13
y=text('1. Abra <b>estacao_integrada.scad</b> e altere o parâmetro escolhido.<br/>2. Em <b>visualizacao</b>, selecione o teste correspondente; renderize com <b>F6</b> e use Arquivo → Exportar → Exportar como STL.<br/>3. Reimprima o <b>par completo</b> do teste e repita o procedimento.<br/>4. Quando aprovado, exporte novamente as <b>duas peças finais da união afetada</b>. Mudar o SCAD não atualiza os STL antigos.',42,y,511,10)
assert y>55
c.showPage()

page(6,'Registre e decida o próximo passo','Ficha para preencher à mão • use uma ficha por material ou revisão.')
y=711
for s in ['Data: ____________________    Responsável: __________________________',
 'Impressora: ______________________________________________________',
 'Material / lote: ___________________________________________________',
 'Bico / camada: ___________________    Perfil do fatiador: _________________',
 'Revisão / parâmetros alterados: ______________________________________']:
 y=text(s,42,y,511,10.5)-13

title('Resultado da triagem manual • 5 ciclos por par',42,y-4,12)
y-=29
for label in ['BAIONETA','TAMPA DA CAIXA','ALETAS']:
 box('<b>'+label+'</b><br/>Entrada: ____   Retenção: ____   Desmontagem: ____   Sem dano: ____<br/>Resultado: (   ) aprovado   (   ) ajustar e repetir<br/>Observações: __________________________________________________',42,y,511,77,size=10)
 y-=90
text('Preencha os campos com OK ou REVER. Registre onde prende, quando solta e o que mudou entre os ciclos.',42,y+1,511,9.5)
y-=39
title('Depois de aprovar as três amostras',42,y,12)
y=text('Monte primeiro a tampa com a base do abrigo, ainda sem a eletrônica. Confira o contorno da tampa e as duas travas na caixa, depois os três pinos de cada aleta. A portinha precisa ser conferida na sua própria abertura; não há amostra específica dela neste pacote.',42,y-13,511,10)
y=text('<b>O que esta triagem demonstra:</b> ajuste e funcionamento manual das amostras na sua impressão. Ela não mede carga máxima, vida útil, vedação ou desempenho dos sensores. Guarde um par aprovado como referência e compare com as peças finais.',42,y-14,511,10)
c.showPage()
c.save()
print(OUT)
