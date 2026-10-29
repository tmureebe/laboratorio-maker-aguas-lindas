"""Confere as redes emitidas pelo SCAD e gera uma projeção da fiação real.

Uso: python objetos3d/conferir_montagem_v2.py
Sem simulação elétrica: verifica conectividade documental e proximidade dos fios.
"""
from pathlib import Path
import ast
import csv
import hashlib
import itertools
import json
import re
import subprocess
import tempfile
from html import escape
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MODEL = HERE / 'montagem_circuito_colmeia_v2.scad'
OLD_HASH = 'e2859099b93cf882885cd9f0eced58259a7e4c1e852127414914606cc7aedca0'

def collect(*defines):
    with tempfile.TemporaryDirectory(prefix='colmeia_v2_') as temp:
        cmd = ['openscad', '-D', 'auditar_conexoes=true']
        for d in defines:
            cmd += ['-D', d]
        cmd += ['-o', str(Path(temp) / 'modelo.csg'), str(MODEL)]
        p = subprocess.run(cmd, capture_output=True, text=True, check=True)
        errors = [s for s in p.stderr.splitlines() if 'ERROR:' in s or 'WARNING:' in s and '$vp*' not in s]
        assert not errors, errors
        return [ast.literal_eval(s[6:]) for s in p.stderr.splitlines() if s.startswith('ECHO: [')]

def audit(records, optional=True):
    terminals = {r[1]: r[2] for r in records if r[0] == 'TERMINAL'}
    wires = [r for r in records if r[0] == 'FIO']
    edges = [r for r in records if r[0] in ('FIO', 'INTERNA')]
    parents = {k: k for k in terminals}
    def root(k):
        while parents[k] != k:
            k = parents[k]
        return k
    for e in edges:
        _, net, a, b, *_ = e
        assert a in terminals and b in terminals, (a, b)
        parents[root(a)] = root(b)
        if e[0] == 'FIO':
            assert np.allclose(e[4][0], terminals[a])
            assert np.allclose(e[4][-1], terminals[b])
            assert np.isfinite(e[4]).all()
    expected = {}
    with (ROOT / 'circuito/esquema_profissional/conexoes.csv').open(encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            expected[row['Rede']] = [t.strip() for t in row['Terminais lógicos'].split(';')
                if optional or not t.strip().startswith(('C1.', 'R3.', 'R4.'))]
    netroots = {}
    for net, nodes in expected.items():
        roots = {root(t) for t in nodes}
        assert len(roots) == 1, ('Rede interrompida', net, nodes)
        netroots[net] = roots.pop()
    assert len(set(netroots.values())) == len(netroots), 'Redes distintas unidas indevidamente'
    for e in edges:
        assert root(e[2]) == netroots[e[1]], ('Nome de rede incoerente', e[:4])
    # Os valores de GPIO são conferidos sem ler/exibir configurações de acesso.
    firmware = (ROOT / 'relatorio_final/codigo_circuito_colmeia_v2_8.ino').read_text()
    pins = dict(re.findall(r'^const int (PIN_\w+)\s*=\s*(\d+)\s*;', firmware, re.M))
    for k, v in {'PIN_DHT1':'4', 'PIN_DHT2':'21', 'PIN_MC38':'27', 'PIN_BATTERY':'34',
                 'PIN_I2S_WS':'25', 'PIN_I2S_BCLK':'26', 'PIN_I2S_DOUT':'33'}.items():
        assert pins[k] == v, (k, pins[k])
    return wires, {'redes_conferidas':len(expected), 'fios':len(wires), 'continuidade':'OK',
                   'isolamento_logico_entre_redes':'OK', 'GPIOs_vs_firmware':'OK'}

def sample(points, step=0.4):
    result = []
    for a, b in zip(points, points[1:]):
        a, b = np.array(a), np.array(b)
        n = max(2, int(np.ceil(np.linalg.norm(b-a)/step))+1)
        result.extend(np.linspace(a, b, n))
    return np.array(result)

def proximity(wires):
    # Inclui os barramentos de cobre expostos, além dos fios isolados.
    wires = wires + [
        ['FIO','+3V3','BARRA_3V3_INICIO','BARRA_3V3_FIM',[[193,45,9.5],[193,156,9.5]],[1,0.5,0],0.5],
        ['FIO','GND','BARRA_GND_INICIO','BARRA_GND_FIM',[[199,45,9.5],[199,156,9.5]],[0,0,0],0.5],
    ]
    samples = [sample(w[4]) for w in wires]
    issues=[]
    for i,j in itertools.combinations(range(len(wires)),2):
        a,b=wires[i],wires[j]
        if a[1]==b[1]:
            continue
        pa,pb=samples[i],samples[j]
        dd=np.sum((pa[:,None,:]-pb[None,:,:])**2,axis=2)
        k,l=np.unravel_index(np.argmin(dd),dd.shape)
        gap=float(np.sqrt(dd[k,l])-a[6]-b[6])
        if gap<0.20:
            issues.append({'a':f'{a[2]} → {a[3]}','b':f'{b[2]} → {b[3]}',
                           'folga_mm':round(gap,3),'ponto_a':pa[k].round(2).tolist(),
                           'ponto_b':pb[l].round(2).tolist()})
    return issues

def projection(records, wires):
    # Projeção superior dos mesmos pontos usados para construir os fios 3D.
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1480" height="1220" viewBox="0 0 296 244">',
         '<rect width="296" height="244" fill="#f8fafb"/>']
    def txt(x,y,t,size=2.8):
        svg.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans" font-size="{size}" fill="#213547">{escape(t)}</text>')
    txt(8,9,'V2 · PROJEÇÃO SUPERIOR DA FIAÇÃO',5)
    txt(8,15,'Trajetos extraídos do SCAD; cruzamentos podem estar em alturas diferentes.',2.8)
    # Espelhamento de Y em torno do centro, mantendo legendas legíveis.
    def xy(p):return p[0]+7,230-p[1]
    for x,y,w,h,title in [(68,39,140,123,'PLACA PERFURADA'),(8,47,45,75,'18650 × 2'),
                         (72,91,18,26,'BMS'),(75,132,13,20,'SW1'),(111,103,18,38,'BOOST'),
                         (158,80,28,52,'ESP32'),(238,55,19,30,'DHT EXT'),
                         (238,100,19,30,'DHT INT'),(240,146,16,22,'INMP441'),
                         (220,181,29,10,'MC-38'),(220,199,29,10,'ÍMÃ')]:
        xx,yy=xy([x,y+h])
        svg.append(f'<rect x="{xx}" y="{yy}" width="{w}" height="{h}" fill="#e7ecef" stroke="#8c9ca5" stroke-width="0.3"/>')
        txt(xx+1,yy+4,title,2.3)
    for x in (193,199):
        a,b=xy([x,45]),xy([x,156])
        svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="#9d8b64" stroke-width="1"/>')
    terminals={r[1]:r[2] for r in records if r[0]=='TERMINAL'}
    for ref in ('R1','R2','R3','R4'):
        a,b=terminals[ref+'.1'],terminals[ref+'.2']
        aa,bb=xy(a),xy(b)
        mx,my=(aa[0]+bb[0])/2,aa[1]
        svg.append(f'<path d="M {aa[0]} {aa[1]} L {bb[0]} {bb[1]}" stroke="#92989d" stroke-width="0.5"/>')
        svg.append(f'<rect x="{mx-3.2}" y="{my-1.1}" width="6.4" height="2.2" rx="0.7" fill="#b8a075" stroke="#75613d" stroke-width="0.2"/>')
        txt(mx-3,my-2.5,ref+(' *' if ref in ('R3','R4') else ''),1.8)
    cx,cy=xy([152,66])
    svg.append(f'<ellipse cx="{cx}" cy="{cy}" rx="3" ry="1" fill="#b04c19"/>')
    txt(cx-3,cy-2,'C1 *',1.8)
    for name,dest in [('R1.2',[150,66]),('R2.2',[154,66])]:
        a,b=xy(terminals[name]),xy(dest)
        svg.append(f'<path d="M {a[0]} {a[1]} L {b[0]} {b[1]}" stroke="#92989d" stroke-width="0.5"/>')
    for w in sorted(wires,key=lambda w:sum(p[2] for p in w[4])/len(w[4])):
        points=' '.join(f'{xy(p)[0]:.3f},{xy(p)[1]:.3f}' for p in w[4])
        color='#'+''.join(f'{round(c*255):02x}' for c in w[5])
        title=escape(f'{w[1]}: {w[2]} → {w[3]}')
        svg.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="{w[6]*2}" stroke-linecap="round"><title>{title}</title></polyline>')
        for p in (w[4][0],w[4][-1]):
            x,y=xy(p)
            svg.append(f'<circle cx="{x}" cy="{y}" r="0.65" fill="{color}" stroke="white" stroke-width="0.2"/>')
    txt(8,236,'Vermelho: bateria / 5 V · Laranja: +SYS / 3V3 · Preto: retornos · Demais cores: sinais',2.7)
    svg.append('</svg>')
    (HERE/'fiacao_montagem_v2.svg').write_text('\n'.join(svg))

if __name__=='__main__':
    records=collect()
    wires,result=audit(records)
    _,without=audit(collect('mostrar_componentes_a_confirmar=false'),False)
    _,exploded=audit(collect('vista_explodida=1'))
    assert hashlib.sha256((HERE/'montagem_circuito_colmeia.scad').read_bytes()).hexdigest()==OLD_HASH
    issues=proximity(wires)
    assert not issues, f'Proximidades que precisam de revisão: {issues}'
    report={'montagem':result,'sem_componentes_opcionais':without,'vista_explodida':exploded,
            'original_preservado_sha256':OLD_HASH,
            'proximidades_entre_fios_de_redes_distintas':issues,
            'limites':'Proximidade por amostragem de 0,4 mm; não testa colisão com corpos dos módulos, tolerâncias físicas ou comportamento elétrico.'}
    (HERE/'conferencia_montagem_v2.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    projection(records,wires)
    print(json.dumps(report,ensure_ascii=False,indent=2))
