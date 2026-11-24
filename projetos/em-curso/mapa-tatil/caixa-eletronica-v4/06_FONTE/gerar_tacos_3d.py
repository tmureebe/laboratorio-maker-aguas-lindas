#!/usr/bin/env python3
"""Exporta os tacos e verifica as malhas, o furo cego e o alinhamento na caixa."""
from collections import Counter, defaultdict
from pathlib import Path
import hashlib
import json
import struct
import subprocess
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / '04_MODELO_3D/Taco_impressao_3D.scad'
OUT = ROOT / '07_IMPRESSAO_3D'


def export(path, mode):
    result = subprocess.run(
        ['openscad', '--export-format', 'binstl', '-o', str(path),
         '-D', f'modo="{mode}"', str(SOURCE)],
        capture_output=True, text=True, check=True)
    if 'WARNING:' in result.stderr or 'ERROR:' in result.stderr:
        raise RuntimeError(result.stderr)
    raw = path.read_bytes()
    count, = struct.unpack_from('<I', raw, 80)
    assert len(raw) == 84 + 50 * count
    dtype = np.dtype([('normal', '<f4', (3,)), ('v', '<f4', (3, 3)), ('attr', '<u2')])
    return np.frombuffer(raw, dtype=dtype, offset=84)['v'].astype(float)


def validate(mesh, dimensions, components):
    vertices, ids = np.unique(np.round(mesh.reshape(-1, 3), 5), axis=0,
                              return_inverse=True)
    faces = ids.reshape(-1, 3)
    edges = Counter()
    directed = Counter()
    adjacency = defaultdict(set)
    for face in faces:
        for a, b in zip(face, np.roll(face, -1)):
            a, b = int(a), int(b)
            edges[tuple(sorted((a, b)))] += 1
            directed[a, b] += 1
            adjacency[a].add(b)
            adjacency[b].add(a)
    assert all(count == 2 for count in edges.values()), 'Malha aberta ou não manifold'
    assert all(directed[a, b] == directed[b, a] for a, b in edges), 'Normais incoerentes'
    todo = set(range(len(vertices)))
    groups = []
    while todo:
        pending = [todo.pop()]
        group = []
        while pending:
            current = pending.pop()
            group.append(current)
            for neighbor in adjacency[current]:
                if neighbor in todo:
                    todo.remove(neighbor)
                    pending.append(neighbor)
        groups.append(group)
    assert len(groups) == components
    lo, hi = vertices.min(0), vertices.max(0)
    assert np.allclose(lo, [0, 0, 0], atol=1e-4)
    assert np.allclose(hi-lo, dimensions, atol=1e-4)
    unit_volume = 20*20*44 - 64/2*1.4**2*np.sin(2*np.pi/64)*18
    volumes = []
    for group in groups:
        selected = np.isin(faces[:, 0], group)
        tri = mesh[selected]
        area = np.linalg.norm(np.cross(tri[:, 1]-tri[:, 0],
                                       tri[:, 2]-tri[:, 0]), axis=1)/2
        assert np.all(area > 1e-8), 'Triângulo degenerado'
        volume = np.einsum('ij,ij->i', tri[:, 0],
                           np.cross(tri[:, 1], tri[:, 2])).sum()/6
        assert np.isclose(volume, unit_volume, atol=0.05)
        assert np.allclose(np.ptp(vertices[group], axis=0), [20, 44, 20])
        volumes.append(round(float(volume), 4))
    # Todos os vertices internos pertencem ao furo cego vertical do STL.
    for group in groups:
        pts = vertices[group] - vertices[group].min(0)
        hole = pts[(pts[:, 0] > .01) & (pts[:, 0] < 19.99)]
        assert np.allclose(np.unique(hole[:, 2]), [2, 20], atol=1e-4)
        assert np.allclose(np.linalg.norm(hole[:, :2]-[10, 32], axis=1),
                           1.4, atol=2e-5)
    return dict(triangulos=len(mesh), componentes=len(groups),
                dimensoes_na_impressao_mm=(hi-lo).tolist(),
                malha_fechada=True, orientacao_consistente=True,
                volumes_solidos_mm3=volumes,
                furo_cego_diametro_mm=2.8, profundidade_furo_mm=18)


def exportar_tacos(parts, centers):
    wall_axes = []
    for part in parts:
        if part['id'] in ('C2_FRENTE', 'C3_TRAS_USB'):
            for hole in part['furos']:
                if isinstance(hole, dict):
                    wall_axes.append((np.array(part['matriz']) @ [*hole['centro'], 0, 1])[:3])
    positions = []
    for x, y in centers:
        front = y < 190
        entry = y - 10 if front else y + 10
        assert entry == (3 if front else 377)
        assert any(np.allclose(p, [x, 0 if front else 377, 35]) for p in wall_axes)
        positions.append(dict(centro_x_s=[x, y], eixo_furo_caixa=[x, entry, 35], face_colagem_z=47))

    report = dict(unidade='mm', ensaio_fisico_realizado=False)
    outputs = [('1un', 'Taco_20x20x44_1un.stl', 'impressao', [20, 44, 20], 1),
               ('8un', 'Tacos_20x20x44_8un.stl', 'lote', [98, 94, 20], 8)]
    with tempfile.TemporaryDirectory(dir=OUT) as tmp:
        staged = Path(tmp)
        hashes = {str(SOURCE.relative_to(ROOT)): hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
        for key, name, mode, dimensions, count in outputs:
            path = staged / name
            report[key] = validate(export(path, mode), dimensions, count)
            hashes[str((OUT / name).relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
        report['posicoes_compativeis_com_as_paredes'] = positions
        report['sha256'] = hashes
        (staged / 'VALIDACAO_TACOS.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
        for path in staged.iterdir():
            path.replace(OUT / path.name)


if __name__ == '__main__':
    from integrar_caixa import main
    main()
