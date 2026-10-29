#!/usr/bin/python3
"""Regenera os modelos padrão dentro do próprio pacote; requer OpenSCAD."""
from pathlib import Path
import json,subprocess
ROOT=Path(__file__).resolve().parents[1]
CAD=ROOT/'06_CAD_VALIDACAO';P=ROOT/'01_IMPRESSAO_3D'
def export(dest,source,defs=()):
    args=['openscad','-o',str(dest)]
    for d in defs:args+=['-D',d]
    subprocess.run(args+[str(source)],check=True)
for name,peca in [('U01_uniao_entrada_MDF_camara.stl','entrada'),('U02_uniao_camara_saida_MDF.stl','saida'),
                  ('08_ligacao_MDF_parte5_126p2.stl','ligacao')]:
    export(P/'01_pecas_finais'/name,CAD/'conexoes.scad',[f'peca="{peca}"'])
for tag,val in [('126p0',126.0),('125p8',125.8)]:
    export(P/'02_alternativas_escolher_uma'/f'08_ligacao_MDF_parte5_{tag}_ALTERNATIVA.stl',
           CAD/'conexoes.scad',['peca="ligacao"',f'macho_final={val}'])
export(P/'03_testes_antes_do_lote/T08_cupom_luva_MDF.stl',CAD/'conexoes.scad',['peca="cupom"'])
export(P/'01_pecas_finais/04_moldura_V7_passagem_120mm.stl',CAD/'moldura_corrigida.scad')
cuts=json.loads((CAD/'cortes.json').read_text())
for pt in cuts['pecas']:
    if pt['id'].startswith(('G','T')):continue
    code=f'linear_extrude({pt["espessura_mm"]}) difference(){{ polygon('+json.dumps(pt['contorno'])+');'
    for h in pt['furos']:
        code+=('polygon('+json.dumps(h)+');' if isinstance(h[0],list)
               else f'translate([{h[0]},{h[1]}]) circle(r={h[2]},$fn=48);')
    src=CAD/'malhas_MDF_REFERENCIA'/(pt['id']+'.scad');src.write_text(code+'}')
    export(src.with_suffix('.stl'),src)
print('Modelos padrão regenerados dentro do pacote.')
