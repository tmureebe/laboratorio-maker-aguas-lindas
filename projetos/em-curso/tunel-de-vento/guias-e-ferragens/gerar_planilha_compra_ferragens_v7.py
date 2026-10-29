"""Gera XLSX e CSV com links de compra, usando as quantidades do manual V7."""
import ast
import csv
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / 'links_compra_ferragens_v7.json').read_text())
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'


def manual_items():
    result = []
    tree = ast.parse((ROOT / 'gerar_manual_ferragens_v7.py').read_text())
    for node in tree.body:
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        names = [target.id for target in node.targets if isinstance(target, ast.Name)]
        if any(name in names for name in ['items', 'cell_screws']):
            for code, d, length, kind, buy, needed, usage in ast.literal_eval(node.value):
                found = re.search(r'USAR (\d+)', needed)
                used = int(found.group(1)) if found else 0
                head = {'pan': 'panela Phillips', 'flat': 'chata escareada Phillips',
                        'allen': 'cilíndrica Allen'}[kind]
                result.append((code, 'Parafuso', f'Parafuso M{d} × {length} mm, cabeça {head}',
                               buy, used, usage))
        elif 'parts' in names:
            for code, d, buy, used, kind, title, note, usage in ast.literal_eval(node.value):
                result.append((code, 'Porca' if kind == 'nut' else 'Arruela',
                               title + ' — ' + note, buy, used, usage))
    order = list(DATA['itens'])
    assert set(order) == {item[0] for item in result}
    return sorted(result, key=lambda item: order.index(item[0]))


ITEMS = manual_items()
assert len(ITEMS) == 19
assert {kind: (sum(x[3] for x in ITEMS if x[1] == kind),
               sum(x[4] for x in ITEMS if x[1] == kind))
        for kind in ['Parafuso', 'Porca', 'Arruela']} == {
            'Parafuso': (132, 42), 'Porca': (80, 38), 'Arruela': (164, 74)}


def colname(n):
    name = ''
    while n:
        n, digit = divmod(n - 1, 26)
        name = chr(65 + digit) + name
    return name


def cell(ref, value, style=0):
    if isinstance(value, (float, int)):
        return f'<c r="{ref}" s="{style}"><v>{value}</v></c>'
    return (f'<c r="{ref}" s="{style}" t="inlineStr"><is>'
            f'<t xml:space="preserve">{escape(str(value))}</t></is></c>')


def worksheet(rows, widths, links=None, title=None, subtitle=None, filtered=False):
    links = links or {}
    count = len(widths)
    lastcol = colname(count)
    first = 4 if title else 1
    lastrow = first + len(rows) - 1
    content = []
    if title:
        content.extend([
            '<row r="1" ht="32" customHeight="1">' + cell('A1', title, 1) + '</row>',
            '<row r="2" ht="34" customHeight="1">' + cell('A2', subtitle, 5) + '</row>'])
    for offset, values in enumerate(rows):
        number = first + offset
        is_header = offset == 0
        height = 30 if is_header else (98 if filtered else 64)
        cells = []
        for c, value in enumerate(values, 1):
            ref = f'{colname(c)}{number}'
            style = 2 if is_header else (4 if ref in links else (6 if isinstance(value, int) else 3))
            cells.append(cell(ref, value, style))
        content.append(f'<row r="{number}" ht="{height}" customHeight="1">' + ''.join(cells) + '</row>')
    columns = ''.join(f'<col min="{n}" max="{n}" width="{width}" customWidth="1"/>'
                      for n, width in enumerate(widths, 1))
    frozen = first if title else 1
    views = (f'<sheetViews><sheetView workbookViewId="0" zoomScale="85">'
             f'<pane xSplit="2" ySplit="{frozen}" topLeftCell="C{frozen + 1}" '
             'activePane="bottomRight" state="frozen"/>'
             '<selection pane="bottomRight"/></sheetView></sheetViews>')
    merged = (f'<mergeCells count="2"><mergeCell ref="A1:{lastcol}1"/>'
              f'<mergeCell ref="A2:{lastcol}2"/></mergeCells>') if title else ''
    autofilter = f'<autoFilter ref="A{first}:{lastcol}{lastrow}"/>' if filtered else ''
    hyperlinks = ''
    rels = []
    for i, (ref, url) in enumerate(links.items(), 1):
        hyperlinks += f'<hyperlink ref="{ref}" r:id="rId{i}" tooltip={quoteattr(url)}/>'
        rels.append(f'<Relationship Id="rId{i}" Type="{REL}/hyperlink" '
                    f'Target={quoteattr(url)} TargetMode="External"/>')
    if hyperlinks:
        hyperlinks = '<hyperlinks>' + hyperlinks + '</hyperlinks>'
    xml = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<worksheet xmlns="{NS}" xmlns:r="{REL}">'
           f'<dimension ref="A1:{lastcol}{lastrow}"/>' + views +
           '<sheetFormatPr defaultRowHeight="18"/><cols>' + columns + '</cols>'
           '<sheetData>' + ''.join(content) + '</sheetData>' + autofilter + merged + hyperlinks +
           '<pageMargins left="0.3" right="0.3" top="0.4" bottom="0.4" header="0.2" footer="0.2"/>'
           '<pageSetup orientation="landscape" paperSize="9" fitToWidth="1" fitToHeight="0"/>'
           '</worksheet>')
    relxml = ('<?xml version="1.0" encoding="UTF-8"?>'
              '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
              + ''.join(rels) + '</Relationships>')
    return xml, relxml


HEADERS = ['Código', 'Ferragem do manual', 'Comprar (un.)', 'Usar (un.)', 'Loja',
           'Link para compra', 'Embalagem / seleção', 'Produto anunciado', 'Observações', 'Uso no projeto']
rows = [HEADERS]
hyperlinks = {}
source_rows = [['Código', 'Loja', 'URL do produto', 'URL do catálogo, quando usado',
                'Conferência', 'Evidência da venda por unidade', 'Estoque / limitações']]
source_links = {}
for code, kind, description, buy, used, usage in ITEMS:
    found = DATA['itens'][code]
    rows.append([code, description, buy, used, found['loja'], 'Abrir produto',
                 found['embalagem'], found['produto'], found['situacao'] + '. ' + found['observacao'], usage])
    hyperlinks[f'F{len(rows) + 3}'] = found['link']
    source_rows.append([code, found['loja'], found['link'], found.get('fonte_catalogo', ''),
                        DATA['consulta'], found.get('evidencia_unitaria', ''), found.get('estoque', '')])
    source_links[f'C{len(source_rows)}'] = found['link']
    if found.get('fonte_catalogo'):
        source_links[f'D{len(source_rows)}'] = found['fonte_catalogo']

notes = [
    ['Assunto', 'Informação'],
    ['Base da planilha', DATA['manual'] + '. Base bipartida incluída; sem medidas externas da célula ou ventoinha.'],
    ['Lojas', '14 itens na Mixpar, 2 no Mega Lojista, 1 na Aki Tem Online, 1 na Jofepar e 1 na Bassotto. P07 está indisponível e A12 tem embalagem pendente de confirmação.'],
    ['Parafusos', 'Comprar 132 unidades, incluindo reservas; usar 42 na montagem. As reservas P08 a P12 têm uso nominal zero.'],
    ['Porcas', 'Comprar 80 unidades (30 M3 + 50 M4); usar 38 (13 M3 + 25 M4).'],
    ['Arruelas', 'Comprar 164 unidades (60 M3 + 100 M4 comuns + 4 M4 largas); usar 74 (24 + 49 + 1).'],
    ['Célula', 'Somente 2 Allen M4 × 30 e 2 Allen M4 × 20. Uma arruela A04 sob cada cabeça; sem porcas. Rosca M4 × 0,7 adotada para planejamento.'],
    ['Base bipartida', 'Incluída: 4 P07, 4 N04 e 4 A04. Essas quantidades já constam dos totais de uso.'],
    ['Alternativas Allen', 'P03, P04 e P11: cabeça cilíndrica Allen em lugar da panela Phillips; conferir encaixes. P02 agora indica panela Phillips; P06, P07 e P08 agora indicam chata Phillips.'],
    ['Como comprar por unidade', 'Na Mixpar, selecionar Unitário no seletor Quantidade; só depois informar a contagem de peças. As opções de 50, 100 ou 500 são embalagens alternativas, quando o Unitário está listado.'],
    ['Atenção: P02', 'Link de lote de 100 substituído pela Aki Tem Online. Selecionar 4x55 (unidade) - cabeça panela. A página exibe última peça e estados de estoque inconsistentes entre variações; a venda avulsa está anunciada, mas o saldo para 8 não está confirmado.'],
    ['P06 e P08', 'Mega Lojista: páginas identificadas como UNIDADE e anunciadas Em estoque. Informar 6 P06 e 8 P08. Não escolher a oferta separada de caixa com 500 peças. Saldo integral não testado no carrinho.'],
    ['P07 — compra pendente', 'Jofepar anuncia a faixa de 1 até 99 unidades, comprovando venda avulsa, mas informa produto indisponível. Não contar com compra imediata. Manter M4 × 20; P08 M4 × 25 é reserva, não substituição automática.'],
    ['A12 — embalagem pendente', 'Arruela larga M4: dimensões confirmadas, mas não foi possível comprovar venda por unidade. Link mantido com pendência explícita. Preço por peça não comprova embalagem unitária.'],
    ['Quantidades', 'Comprar e Usar são contagens de peças. Há evidência de venda unitária para os 18 itens de parafusos, porcas e arruelas comuns; isso não confirma estoque. A embalagem da arruela larga A12 continua pendente.'],
    ['Alavanca', 'A contagem do manual considera duas porcas M3 na retenção da alavanca e duas arruelas M3, do lado das porcas.'],
    ['Consulta', DATA['consulta'] + '. Links e descrições consultados publicamente; a planilha não é uma cotação nem um pedido enviado às lojas.'],
]

styles = f'''<?xml version="1.0" encoding="UTF-8"?>
<styleSheet xmlns="{NS}">
<fonts count="4">
 <font><sz val="11"/><name val="Calibri"/><color rgb="FF19242C"/></font>
 <font><b/><sz val="18"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font>
 <font><b/><sz val="11"/><name val="Calibri"/><color rgb="FFFFFFFF"/></font>
 <font><u/><sz val="11"/><name val="Calibri"/><color rgb="FF0563C1"/></font>
</fonts>
<fills count="4"><fill><patternFill patternType="none"/></fill><fill><patternFill patternType="gray125"/></fill>
 <fill><patternFill patternType="solid"><fgColor rgb="FF244D64"/><bgColor indexed="64"/></patternFill></fill>
 <fill><patternFill patternType="solid"><fgColor rgb="FFE9EFF2"/><bgColor indexed="64"/></patternFill></fill></fills>
<borders count="2"><border/><border><left style="thin"><color rgb="FFD4DFE5"/></left><right style="thin"><color rgb="FFD4DFE5"/></right><top style="thin"><color rgb="FFD4DFE5"/></top><bottom style="thin"><color rgb="FFD4DFE5"/></bottom></border></borders>
<cellStyleXfs count="1"><xf numFmtId="0" fontId="0" fillId="0" borderId="0"/></cellStyleXfs>
<cellXfs count="7">
 <xf numFmtId="0" fontId="0" fillId="0" borderId="0" xfId="0"/>
 <xf numFmtId="0" fontId="1" fillId="2" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center"/></xf>
 <xf numFmtId="0" fontId="2" fillId="2" borderId="1" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
 <xf numFmtId="0" fontId="0" fillId="0" borderId="1" xfId="0" applyAlignment="1"><alignment vertical="top" wrapText="1"/></xf>
 <xf numFmtId="0" fontId="3" fillId="0" borderId="1" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
 <xf numFmtId="0" fontId="0" fillId="3" borderId="0" xfId="0" applyAlignment="1"><alignment vertical="center" wrapText="1"/></xf>
 <xf numFmtId="1" fontId="0" fillId="3" borderId="1" xfId="0" applyAlignment="1"><alignment horizontal="center" vertical="center"/></xf>
</cellXfs><cellStyles count="1"><cellStyle name="Normal" xfId="0" builtinId="0"/></cellStyles>
</styleSheet>'''

sheets = [
    ('Comprar', *worksheet(rows, [12, 43, 12, 12, 16, 19, 38, 50, 76, 43], hyperlinks,
        'Ferragens V7 — links de compra',
        'Base bipartida incluída • 19 itens • Consulta em ' + DATA['consulta'] +
        ' • Venda por unidade: ver seleção; P07 sem estoque; A12 com embalagem pendente.', True)),
    ('Notas', *worksheet(notes, [29, 115])),
    ('Fontes', *worksheet(source_rows, [12, 19, 100, 100, 18, 85, 75], source_links, filtered=True))]
out = ROOT / 'Planilha_Compra_Ferragens_V7.xlsx'
with ZipFile(out, 'w', ZIP_DEFLATED) as z:
    overrides = ''.join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
                        'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                        for i in range(1, len(sheets) + 1))
    z.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.styles+xml"/>'
        + overrides + '</Types>')
    z.writestr('_rels/.rels', '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        f'<Relationship Id="rId1" Type="{REL}/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>')
    sheetnames = ''.join(f'<sheet name={quoteattr(name)} sheetId="{i}" r:id="rId{i}"/>'
                         for i, (name, _, _) in enumerate(sheets, 1))
    z.writestr('xl/workbook.xml', '<?xml version="1.0" encoding="UTF-8"?>'
        f'<workbook xmlns="{NS}" xmlns:r="{REL}"><bookViews><workbookView/></bookViews>'
        f'<sheets>{sheetnames}</sheets><calcPr calcId="191029"/></workbook>')
    relationships = ''.join(f'<Relationship Id="rId{i}" Type="{REL}/worksheet" '
                            f'Target="worksheets/sheet{i}.xml"/>' for i in range(1, len(sheets) + 1))
    z.writestr('xl/_rels/workbook.xml.rels', '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        + relationships + f'<Relationship Id="rId{len(sheets) + 1}" Type="{REL}/styles" Target="styles.xml"/>'
        '</Relationships>')
    z.writestr('xl/styles.xml', styles)
    for i, (_, xml, rels) in enumerate(sheets, 1):
        z.writestr(f'xl/worksheets/sheet{i}.xml', xml)
        z.writestr(f'xl/worksheets/_rels/sheet{i}.xml.rels', rels)

csvout = ROOT / 'Planilha_Compra_Ferragens_V7.csv'
with csvout.open('w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f, delimiter=';')
    writer.writerow(HEADERS)
    for row in rows[1:]:
        exported = row[:]
        exported[5] = DATA['itens'][row[0]]['link']
        writer.writerow(exported)
print(out)
print(csvout)
