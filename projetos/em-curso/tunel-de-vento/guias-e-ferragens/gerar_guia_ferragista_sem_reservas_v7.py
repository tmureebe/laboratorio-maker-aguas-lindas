"""Gera o pedido ilustrado ao ferragista. Executar com /usr/bin/python3."""
import ast
import math
import re
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'Guia_Ferragista_Sem_Reservas_V7.pdf'
source = ast.parse((ROOT / 'gerar_manual_ferragens_v7.py').read_text())

# Reaproveita os desenhos vetoriais sem executar o gerador do manual original.
helpers = {'text', 'wrap', 'poly', 'arrow', 'dim', 'screw', 'nut', 'washer'}
definitions = ast.Module(
    body=[node for node in source.body
          if isinstance(node, ast.FunctionDef) and node.name in helpers],
    type_ignores=[])

screws, parts = [], []
for node in source.body:
    if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
        continue
    names = {target.id for target in node.targets if isinstance(target, ast.Name)}
    if names & {'items', 'cell_screws'}:
        for code, diameter, length, kind, buy, needed, usage in ast.literal_eval(node.value):
            match = re.search(r'USAR (\d+)', needed)
            if match:
                screws.append((code, diameter, length, kind, int(match.group(1))))
    elif 'parts' in names:
        for code, diameter, buy, used, kind, title, note, usage in ast.literal_eval(node.value):
            if used:
                parts.append((code, diameter, used, kind, title, note))

assert len(screws) == 9 and sum(row[4] for row in screws) == 42
assert len(parts) == 5
assert sum(row[2] for row in parts if row[3] == 'nut') == 38
assert sum(row[2] for row in parts if row[3] != 'nut') == 74
assert not ({row[0] for row in screws} & {'P08', 'P09', 'P10', 'P11', 'P12'})

for name, filename in [('DV', 'DejaVuSans.ttf'), ('DVB', 'DejaVuSans-Bold.ttf')]:
    pdfmetrics.registerFont(TTFont(name, '/usr/share/fonts/truetype/dejavu/' + filename))

W, H = A4
INK = HexColor('#19242c')
BLUE = HexColor('#244d64')
LIGHT = HexColor('#e9eff2')
LINE = HexColor('#bac7ce')
C = canvas.Canvas(str(OUT), pagesize=A4)
C.setTitle('Pedido ilustrado de ferragens V7 — quantidades sem reservas')
C.setAuthor('Laboratório MAKER')
exec(compile(definitions, 'desenhos_ferragens_v7', 'exec'), globals())


def page(title, subtitle, number):
    C.setFillColor(BLUE)
    C.rect(0, H - 9, W, 9, stroke=0, fill=1)
    text(34, H - 42, 'PEDIDO DE FERRAGENS', 9, True, BLUE)
    text(34, H - 72, title, 22, True)
    text(34, H - 94, subtitle, 9)
    text(W - 64, 25, f'{number} / 2', 8)


def quantity(value, top, height):
    x, w, h = 520, 42, 45
    y = top - height / 2 - h / 2
    C.setFillColor(LIGHT)
    C.roundRect(x, y, w, h, 5, stroke=0, fill=1)
    C.setFillColor(INK)
    C.setFont('DVB', 16)
    C.drawCentredString(x + w / 2, y + 23, str(value))
    C.setFont('DV', 8)
    C.drawCentredString(x + w / 2, y + 10, 'unidade' if value == 1 else 'unidades')


def separator(y):
    C.setStrokeColor(LINE)
    C.setLineWidth(.5)
    C.line(34, y, W - 34, y)


page('Parafusos — 42 unidades', 'Rosca máquina métrica • Medidas em milímetros', 1)
heads = {'pan': 'Cabeça panela Phillips', 'flat': 'Cabeça chata escareada Phillips',
         'allen': 'Cabeça cilíndrica Allen'}
top = H - 119
for code, diameter, length, kind, count in screws:
    text(42, top - 20, f'M{diameter} × {length} mm', 12, True)
    text(42, top - 36, heads[kind], 9)
    text(42, top - 51, 'Passo ' + ('0,5' if diameter == 3 else '0,7') + ' mm', 8)
    scale = min(3.2, 125 / length)
    screw(295, top - 26, length, diameter, kind, scale)
    quantity(count, top, 69)
    separator(top - 69)
    top -= 69
text(34, 69, 'Comprimento: sob a cabeça nos comuns; incluindo a cabeça nos escareados.', 8)
C.showPage()

page('Porcas e arruelas', '38 porcas • 74 arruelas', 2)
top = H - 124
for code, diameter, count, kind, title, note in parts:
    text(42, top - 30, title, 12, True)
    if kind == 'nut':
        text(42, top - 49, 'Rosca métrica • Passo ' + ('0,5' if diameter == 3 else '0,7') + ' mm', 9)
        nut(413, top - 49, diameter, 5)
    elif kind == 'wide':
        text(42, top - 49, 'Furo ≈ 4,3 mm • Externo ≈ 12 mm', 9)
        text(42, top - 66, 'Espessura: 1 mm • DIN 9021', 9)
        washer(413, top - 42, diameter, True)
    else:
        text(42, top - 49, f'Para parafuso M{diameter} • DIN 125', 9)
        washer(413, top - 49, diameter)
    quantity(count, top, 110)
    separator(top - 110)
    top -= 110
C.showPage()
C.save()
print(OUT)
