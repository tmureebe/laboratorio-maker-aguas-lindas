#!/usr/bin/env python3
"""Confere fios/soldas, acesso inferior do ferro e assento nas 18 pecas reais."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile
import numpy as np

BASE = Path(__file__).resolve().parent
DETAIL = BASE / 'Detalhe_encaixe_botao_e_fios.scad'
MAP = BASE / 'construcoes_vista_aerea.scad'


def check(number, tmp):
    result = dict(botao=number)
    for mode in ('interferencias', 'acesso_ferro', 'assento'):
        output = tmp / f'botao_{number}_{mode}.stl'
        command = ['openscad', '--export-format', 'binstl', '-o', str(output),
                   '-D', f'numero_botao={number}', '-D', f'verificacao="{mode}"', str(DETAIL)]
        run = subprocess.run(command, capture_output=True, text=True)
        log = (run.stdout + run.stderr).replace('WARNING: Viewall and autocenter disabled in favor of $vp*\n', '')
        assert 'WARNING:' not in log and 'ERROR:' not in log, log
        if mode != 'assento':
            assert run.returncode == 1 and 'Current top level object is empty.' in log, (number, mode, log)
            result['interferencia_solda_fio_com_pecas' if mode == 'interferencias'
                   else 'interferencia_ferro_com_impresso'] = False
        else:
            assert run.returncode == 0, (number, mode, log)
            raw = output.read_bytes()
            count = struct.unpack('<I', raw[80:84])[0]
            dtype = np.dtype([('normal', '<f4', (3,)), ('v', '<f4', (3, 3)), ('attr', '<u2')])
            mesh = np.frombuffer(raw, dtype=dtype, offset=84, count=count)['v'].astype(float)
            volume = float(np.einsum('ij,ij->i', mesh[:, 0], np.cross(mesh[:, 1], mesh[:, 2])).sum()/6)
            area = volume / .025  # Espessura da secao real sob o corpo no detalhe.
            assert area > 12*12*.8, (number, 'assento insuficiente ou centro aberto', area)
            result['area_apoio_corpo_mm2'] = round(area, 3)
    print(f'Botão {number}: soldas/fios livres, acesso aos 4 terminais livre, assento preservado', flush=True)
    return result


def main():
    with tempfile.TemporaryDirectory(prefix='validar-encaixe-') as directory:
        tmp = Path(directory)
        with ThreadPoolExecutor(max_workers=2) as pool:
            rows = list(pool.map(lambda n: check(n, tmp), range(1, 19)))
    report = dict(cavidade_inferior_xy_mm=[15.3, 12.5], espessura_assento_mm=1.2,
                  parede_minima_mm=1.2, furo_central_impresso=False,
                  diametro_furo_mdf_mm=2.6, furos_mdf_por_botao=4,
                  fio_isolado_mm=1.4, solda_envelope_mm=[2, 2, 1.6],
                  ferro_envelope=dict(diametro_ponta_mm=3, inclinacao_graus=15,
                                      terminais_conferidos_por_botao=4, mdf_removido=True),
                  verificacao_cgal=rows,
                  resultado='18 alojamentos com acesso inferior aos quatro terminais, sem interferencias nos envelopes nominais e com assento preservado',
                  processo='soldar pela face inferior antes de fixar o relevo ao MDF, ou soldar fora antes de encaixar',
                  fontes_sha256={p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                 for p in (MAP, DETAIL, Path(__file__))})
    (BASE / 'VERIFICACAO_DETALHE_BOTAO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')


if __name__ == '__main__':
    main()
