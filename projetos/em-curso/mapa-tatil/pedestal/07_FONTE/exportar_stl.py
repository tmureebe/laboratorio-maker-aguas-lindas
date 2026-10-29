#!/usr/bin/env python3
"""Exporta sólidos fechados das peças planas; exige OpenSCAD no PATH.

Peças de colagem com faces coincidentes são visualizadas juntas pelo SCAD.
Os STL individuais servem para visualizar, não são arquivos de corte.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import subprocess

root=Path(__file__).resolve().parents[1]
scad=root/'04_MODELOS_3D'/'Pedestal_MDF.scad'
dest=root/'04_MODELOS_3D'/'PECAS_STL'
dest.mkdir(exist_ok=True)
for line in scad.read_text().splitlines():
    if line.startswith('nomes='):
        names=json.loads(line[len('nomes='):-1])

def export(item):
    i,name=item
    output=dest/f'{name}.stl'
    proc=subprocess.run(['openscad','-o',str(output),'-D','modo="peca3d"',
                         '-D',f'numero_peca={i}',str(scad)],
                        text=True,capture_output=True)
    if proc.returncode or 'WARNING' in proc.stderr or 'ERROR' in proc.stderr:
        raise RuntimeError(f'{name}: {proc.stderr}')
    return name

with ThreadPoolExecutor(max_workers=4) as pool:
    exported=list(pool.map(export,enumerate(names,1)))
print(f'{len(exported)} STL individuais exportados pelo OpenSCAD.')
