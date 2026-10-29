#!/usr/bin/python3
"""Gera listas rastreáveis e PDFs dos Markdown do pacote independente."""
from pathlib import Path
import csv,html,json,re
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,Preformatted,Image,PageBreak
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1];DOC=ROOT/'04_DOCUMENTOS';CAD=ROOT/'06_CAD_VALIDACAO'
records=json.loads((CAD/'inventario_impressao.json').read_text())
cuts=json.loads((CAD/'cortes.json').read_text());report=json.loads((CAD/'relatorio_verificacao.json').read_text())
standard=[q for q in records if '/01_pecas_finais/' in q['arquivo']]
alternatives=[q for q in records if '/02_alternativas_' in q['arquivo']]
tests=[q for q in records if '/03_testes_' in q['arquivo']]
assert len(standard)==19 and sum(q['quantidade'] for q in standard)==29
roles={'parte_1.stl':'Placa traseira da ventoinha','parte_2.stl':'Base fixa do regulador',
       'parte_3.stl':'Disco móvel do regulador','parte_4.stl':'Alavanca do disco','parte_5.stl':'Transição para ventoinha'}
md=['# Lista de fabricação · V7','',
    'Unidades em mm · escala 100% · padrão: 19 arquivos STL / 29 peças físicas, incluindo cinco peças recebidas reaproveitáveis.',
    '', '## Impressão 3D padrão — 01_pecas_finais','', '| Arquivo | Qtd. | Função |','|---|---:|---|']
for q in sorted(standard,key=lambda q:Path(q['arquivo']).name):
    name=Path(q['arquivo']).name;role=roles.get(name,q['funcao'])
    if name.startswith('parte_'):role+='; reaproveitar se pronta'
    md.append(f'| {name} | {q["quantidade"]} | {role} |')
md+=['','---','','## Alternativas — escolher em lugar da peça padrão','',
     '| Arquivo | Usar |','|---|---|']
for q in alternatives:md.append(f'| {Path(q["arquivo"]).name} | No lugar da asa A ou da ligação 126,2 correspondente |')
md+=['','## Testes impressos — antes do lote','',
     'Uma unidade de cada teste escolhido; imprimir a variante de macho necessária, não todas obrigatoriamente. Para testar janela, acrescentar uma presilha 11 e um espaçador 12 da pasta padrão.',
     '', '| Arquivo | Função |','|---|---|']
for q in sorted(tests,key=lambda q:Path(q['arquivo']).name):md.append(f'| {Path(q["arquivo"]).name} | {q["funcao"]} |')
md+=['','---','','## Corte MDF — quantidades físicas','',
     '| ID | Material | Qtd. | Envelope nominal | Função |','|---|---|---:|---|---|']
for q in cuts['pecas']:
    w,h=q['dimensoes_mm'];md.append(f'| {q["id"]} | MDF {q["espessura_mm"]:g} mm | {q["quantidade"]} | {w:g} × {h:g} | {q["titulo"]} |')
md+=['','M13/M23/M19 são lâminas: quatro por apoio. Quantidade final: seis apoios, 24 lâminas. B01/B02/B03 formam a base opcional. G13/G19 são ferramentas; T01/T02/T03 são cupons.',
     '', '## Chapas MDF 600 × 400','', '| Grupo | Material | Chapas |','|---|---|---:|']
groups={}
for q in cuts['chapas']:groups[(q['grupo'],q['espessura_mm'])]=groups.get((q['grupo'],q['espessura_mm']),0)+1
for (group,t),qty in groups.items():md.append(f'| {group} | MDF {t:g} mm | {qty} |')
md+=['','As chapas já incluem todas as quantidades. Use chapas ou arquivos individuais, SVG ou DXF. Não duplicar os cortes. Margem mínima 5 mm e contornos sem compensação de kerf.',
     '', '## Acrílico separado','', 'Uma tampa 172 × 120 × 3 mm, sem furos; SVG/DXF em 02_CORTE_LASER/ACRILICO_3mm. Reaproveitar se já cortada.',
     '', '## Comprar e reaproveitar','', 'Consulte 03_COMPRADOS_NAO_FABRICAR/LEIA_PRIMEIRO.md e 03_LISTA_COMPRAS.pdf. Ventoinha, célula e ferragens não são peças impressas.']
(DOC/'02_LISTA_FABRICACAO.md').write_text('\n'.join(md)+'\n')
with (DOC/'02_LISTA_FABRICACAO.csv').open('w',encoding='utf-8-sig',newline='') as out:
    w=csv.writer(out,delimiter=';');w.writerow(['tipo','arquivo_ou_id','quantidade','material','observacao'])
    for q in standard+alternatives+tests:w.writerow(['impressao_padrao' if q in standard else 'alternativa' if q in alternatives else 'teste',q['arquivo'],q['quantidade'],'PLA',q['funcao']])
    for q in cuts['pecas']:w.writerow(['corte_MDF',q['id'],q['quantidade'],f'MDF {q["espessura_mm"]:g} mm',q['titulo']])
    w.writerow(['corte_acrilico','Tampa_172x120x3mm',1,'acrilico 3 mm','usar SVG ou DXF'])
(DOC/'03_LISTA_COMPRAS.md').write_text((ROOT/'03_COMPRADOS_NAO_FABRICAR/LEIA_PRIMEIRO.md').read_text())
summary=f'''# Verificação do modelo · V7

Resultado: **{report['resultado']}**. Conferência digital, sem ensaio físico.

| Conferência | Resultado |
|---|---|
| STL de fabricação, incluindo alternativas/testes | {len(report['malhas_fabricacao'])} malhas fechadas, sem triângulos degenerados, volume positivo |
| Chapas MDF | {report['cortes']['chapas']} chapas; limites 600 × 400; margens e quantidades conferidas |
| Novo apoio da câmara M23 | X=350, patamar 60, furos compatíveis com B01 |
| Moldura corrigida | Altura livre de 120 em X=210 e 390, na região fechada sobre o canal |
| Interfaces alteradas versus vizinhos | {len(report['intersecoes_geometricas'])} interseções booleanas; nenhuma acima de 0,01 mm³ |
| Asas A e B | Envelopes nos cinco ângulos e {len(report['intersecoes_asas_por_angulo'])} interseções contra câmara, moldura, suporte e acrílico |
| Cinco partes recebidas | Hashes originais preservados |

## Alterações feitas após a revisão

1. O teto da moldura V5 ficava em Z=180,8, acima do piso interno Z=62,4: a altura local era 118,4. O rebaixo V7 eleva o teto interno a Z=182,4 sem alterar furos ou apoios externos. O canal nominal passa a ter 120 mm também nos trechos cobertos da janela.
2. A câmara passou a ter seu próprio apoio M23, em X=350, evitando sustentar seu peso somente pelas luvas. O patamar é 60 mm; os apoios dos dutos têm 59,4 mm. O painel e os mapas incluem os dois furos adicionais.
3. Os parafusos do painel foram revistos de M4 × 16 para M4 × 20 para acomodar pilha nominal de 12 mm, porca e arruelas. Conferir ferragens reais.
4. A montagem foi reconstruída com todas as peças finais e referências comerciais, em uma pasta independente. As peças substituídas V5 não estão na pasta de impressão padrão.

## Alcance da verificação

Os testes booleanos examinam pares com sobreposição de envelopes nas interfaces alteradas: MDF, novas conexões, moldura e componentes vizinhos. Contatos coplanares de apoio não são tratados como colisões. Foram acrescentadas 40 interseções das duas asas nos cinco ângulos contra câmara, moldura, suporte e acrílico: total de 130 testes booleanos. Ventoinha/célula são referências simplificadas; ferragens não foram modeladas.

Ainda dependem de teste físico: tolerâncias de corte/impressão, acabamento, encaixe após selagem, rigidez da base de 6 mm, vedação, vibração e medição. Não houve CFD nem cálculo estrutural.

O relatório detalhado, com nomes dos pares, volumes, dimensões e hashes, está em 06_CAD_VALIDACAO/relatorio_verificacao.json.
'''
(DOC/'04_VERIFICACAO_MODELO.md').write_text(summary)

pdfmetrics.registerFont(TTFont('DejaVu','/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('DejaVuBold','/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFontFamily('DejaVu',normal='DejaVu',bold='DejaVuBold',italic='DejaVu',boldItalic='DejaVuBold')
styles=getSampleStyleSheet()
for name in ['Normal','Heading1','Heading2']:styles[name].fontName='DejaVu'
styles['Normal'].fontSize=9;styles['Normal'].leading=12.6;styles['Normal'].spaceAfter=7
styles['Heading1'].fontName='DejaVuBold';styles['Heading1'].fontSize=24;styles['Heading1'].leading=30;styles['Heading1'].textColor=colors.HexColor('#164956')
styles['Heading2'].fontName='DejaVuBold';styles['Heading2'].fontSize=15;styles['Heading2'].leading=20;styles['Heading2'].textColor=colors.HexColor('#164956')
styles.add(ParagraphStyle('Cell',parent=styles['Normal'],fontSize=7.5,leading=10,spaceAfter=0))
def inline(s):
    s=html.escape(s);s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
    s=re.sub(r'`([^`]+)`',r'\1',s);s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1',s)
    return s
def footer(canvas,doc):
    canvas.saveState();canvas.setFont('DejaVu',7.5);canvas.setFillColor(colors.HexColor('#526d78'))
    canvas.drawString(16*mm,10*mm,'Túnel híbrido V7 · 06/10/2026 · mm · fabricação em escala 100%')
    canvas.drawRightString(A4[0]-16*mm,10*mm,str(doc.page));canvas.restoreState()
for name in ('01_GUIA_MONTAGEM','02_LISTA_FABRICACAO','03_LISTA_COMPRAS','04_VERIFICACAO_MODELO'):
    story=[];table=[]
    def flush():
        if not table:return
        n=len(table[0]);width=A4[0]-32*mm
        weights=[1]*n
        if n==3 and table[0][0]=='Arquivo':weights=[2.3,.3,1.4]
        elif n==5 and table[0][0]=='ID':weights=[.35,.7,.3,.8,2]
        elif n==5:weights=[1.5,1.4,1.2,1,.9]
        elif n==3 and table[0][0]=='Pasta':weights=[1.3,1.3,1.5]
        elif n==2:weights=[1.5,2]
        widths=[width*w/sum(weights) for w in weights]
        tb=Table([[Paragraph(inline(v),styles['Cell']) for v in row] for row in table],colWidths=widths,repeatRows=1,hAlign='LEFT')
        tb.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e4eef0')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#bdcfd4')),
          ('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
          ('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
        story.extend([tb,Spacer(1,8)]);table.clear()
    for line in (DOC/(name+'.md')).read_text().splitlines():
        if line.startswith('|'):
            cells=[c.strip() for c in line.strip('|').split('|')]
            if not all(re.fullmatch(r'[:\- ]+',c) for c in cells):table.append(cells)
            continue
        flush()
        if not line.strip():continue
        if line=='---':story.append(PageBreak());continue
        match=re.match(r'!\[([^]]*)\]\(([^)]+)\)',line)
        if match:
            path=(DOC/match.group(2)).resolve();assert path.is_file(),path
            img=Image(str(path));width=178*mm;h=width*img.imageHeight/img.imageWidth
            max_h=112*mm
            if h>max_h:width*=max_h/h;h=max_h
            img.drawWidth=width;img.drawHeight=h;story.extend([img,Spacer(1,9)]);continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));story.append(Paragraph(inline(line[level:].strip()),styles['Heading1' if level==1 else 'Heading2']))
        else:story.append(Paragraph(inline(line),styles['Normal']))
    flush()
    SimpleDocTemplate(str(DOC/(name+'.pdf')),pagesize=A4,rightMargin=16*mm,leftMargin=16*mm,
        topMargin=15*mm,bottomMargin=18*mm,title=name.replace('_',' '),author='Laboratório MAKER').build(story,onFirstPage=footer,onLaterPages=footer)
    print('PDF:',name,flush=True)
