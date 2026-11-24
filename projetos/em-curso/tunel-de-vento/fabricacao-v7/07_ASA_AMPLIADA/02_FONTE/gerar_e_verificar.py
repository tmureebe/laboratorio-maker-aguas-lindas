#!/usr/bin/python3
"""Gera a asa e verifica o STL real; não regenera nem altera a montagem V7.
Dependências locais: NumPy, Matplotlib e OpenSCAD. Executar com /usr/bin/python3.
"""
from pathlib import Path
import hashlib
import json
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ROOT = OUT.parent
sys.path.insert(0, str(ROOT / '06_CAD_VALIDACAO'))
from malhas import read, write, rotation, transform

SCAD = HERE / 'asa_ampliada.scad'
PRINT = OUT / '01_IMPRIMIR/21_asa_ampliada_190x114mm.stl'
CHECK = OUT / '03_VERIFICACAO'
VIEW = OUT / '04_VISUALIZACAO'
PIVOT = np.array([300., 0., 104.4])


def render(dest, mode, **params):
    cmd = ['openscad', '-o', str(dest), '-D', f'modo="{mode}"']
    for key, val in params.items():
        cmd += ['-D', f'{key}={val}']
    r = subprocess.run(cmd + [str(SCAD)], capture_output=True, text=True)
    assert r.returncode == 0 and dest.exists(), r.stderr
    assert 'WARNING' not in r.stderr and 'ERROR' not in r.stderr, r.stderr


def mesh_check(path):
    t = read(path)
    v, inv = np.unique(t.reshape(-1, 3), axis=0, return_inverse=True)
    f = inv.reshape(-1, 3)
    edges = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    _, counts = np.unique(np.sort(edges, axis=1), axis=0, return_counts=True)
    volume = np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum()/6
    areas2 = np.linalg.norm(np.cross(t[:, 1]-t[:, 0], t[:, 2]-t[:, 0]), axis=1)
    # One connected component; each edge appears once in each direction.
    directed, dc = np.unique(edges, axis=0, return_counts=True)
    parent = np.arange(len(v))
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for a, b in edges:
        parent[find(a)] = find(b)
    components = len({find(i) for i in range(len(v))})
    assert (counts == 2).all() and (dc == 1).all()
    assert (areas2 > 1e-9).all() and volume > 0 and components == 1
    assert np.min(v[:, 2]) >= -1e-5
    return dict(fechada=True, componentes=components, orientacao_consistente=True,
                triangulos=len(t), volume_mm3=float(volume),
                dimensoes_mm=np.ptp(v, axis=0).tolist(),
                minimo_mm=v.min(0).tolist(), maximo_mm=v.max(0).tolist(),
                sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def continuous_bounds(vertices, max_angle=20):
    """Exact extrema of each vertex trajectory, including stationary angles.
    For triangles and rigid rotations, extrema occur at a mesh vertex.
    """
    theta = math.radians(max_angle)
    result = []
    for a, b in [(vertices[:, 0], vertices[:, 2]),
                 (vertices[:, 2], -vertices[:, 0])]:
        candidates = [a*math.cos(theta)+b*math.sin(theta),
                      a*math.cos(theta)-b*math.sin(theta)]
        base = np.arctan2(b, a)
        for k in range(-2, 3):
            angle = base + k*math.pi
            valid = np.abs(angle) <= theta
            values = a*np.cos(angle)+b*np.sin(angle)
            candidates.append(np.where(valid, values, np.nan))
        result.append([float(np.nanmin(candidates)), float(np.nanmax(candidates))])
    return np.array([[result[0][0], vertices[:, 1].min(), result[1][0]],
                     [result[0][1], vertices[:, 1].max(), result[1][1]]])


def boolean(a, b, label):
    src = CHECK / (label + '.scad')
    dest = CHECK / (label + '.stl')
    src.write_text('intersection(){import('+json.dumps(str(a))+');import('
                   +json.dumps(str(b))+');}\n')
    dest.unlink(missing_ok=True)
    r = subprocess.run(['openscad', '-o', str(dest), str(src)],
                       capture_output=True, text=True)
    assert 'ERROR' not in r.stderr and 'WARNING' not in r.stderr, r.stderr
    volume = 0.
    if dest.exists():
        t = read(dest)
        volume = abs(np.einsum('ij,ij->i', t[:, 0], np.cross(t[:, 1], t[:, 2])).sum()/6)
    else:
        assert r.returncode in (0, 1) and 'empty' in r.stderr.lower(), r.stderr
    assert volume < 0.001, (label, volume)
    src.unlink()
    dest.unlink(missing_ok=True)
    return dict(teste=label, volume_intersecao_mm3=float(volume))


def main():
    for p in (PRINT.parent, CHECK, VIEW):
        p.mkdir(exist_ok=True)
    render(PRINT, 'imprimir')
    mesh = mesh_check(PRINT)
    print('STL fechado, orientado e com um único sólido.', flush=True)
    mounted = CHECK / 'asa_montada_REFERENCIA.stl'
    render(mounted, 'montada')
    wing = read(mounted)
    local = wing.reshape(-1, 3)-PIVOT
    envelope = continuous_bounds(local)+PIVOT
    margins = dict(entrada=float(envelope[0, 0]-200),
                   saida=float(400-envelope[1, 0]),
                   lateral=float(60-np.abs(envelope[:, 1]).max()),
                   piso=float(envelope[0, 2]-62.4),
                   teto_conservador=float(180.8-envelope[1, 2]))
    assert min(margins.values()) >= 3-1e-4, margins

    # Demonstrate maximum WHOLE millimetre chord for this profile, centered
    # pivot, 3-mm margins and ±20 degrees (not an aerodynamic optimum).
    candidate = CHECK / 'candidato_191mm.stl'
    render(candidate, 'montada', corda=191)
    bounds191 = continuous_bounds(read(candidate).reshape(-1, 3)-PIVOT)+PIVOT
    assert bounds191[0, 0] < 203 or bounds191[1, 0] > 397
    candidate.unlink()

    # Use actual chamber/mount meshes, all original intended angle settings.
    reference = ROOT / '06_CAD_VALIDACAO/montagem_REFERENCIA'
    neighbors = ['camara', 'moldura', 'suporte_asa', 'acrilico', 'U01', 'U02']
    jobs = []
    angles = []
    for angle in (-20, -15, -10, -5, 0, 5, 10, 15, 20):
        w = transform(wing-PIVOT, rotation('y', angle), PIVOT)
        path = CHECK / f'asa_angulo_{angle}_REFERENCIA.stl'
        write(path, w)
        for n in neighbors:
            jobs.append((path, reference / (n+'.stl'), f'colisao_{angle}_{n}'))
        angles.append(dict(angulo_graus=angle, minimo_mm=w.reshape(-1, 3).min(0).tolist(),
                           maximo_mm=w.reshape(-1, 3).max(0).tolist()))
    with ThreadPoolExecutor(max_workers=2) as pool:
        collisions = list(pool.map(lambda args: boolean(*args), jobs))
    print(f'{len(collisions)} interseções sem colisões.', flush=True)

    # Sweep the actual aerofoil polygon past a conservative support envelope.
    # Between samples, displacement <= R*dtheta/2; expand X and subtract
    # the same bound in Z. The retained lug/neck stay between support ears.
    body_file = CHECK / 'corpo_REFERENCIA.stl'
    render(body_file, 'corpo')
    body = read(body_file).reshape(-1, 3)
    tip = np.unique(body[np.isclose(body[:, 1], body[:, 1].min())][:, [0, 2]], axis=0)
    # Order polygon around its interior point, including the blunt TE.
    center = tip.mean(0)
    tip = tip[np.argsort(np.arctan2(tip[:, 1]-center[1], tip[:, 0]-center[0]))]
    radius = np.linalg.norm(tip, axis=1).max()
    delta = float(radius*math.radians(0.05)/2)
    sup_tri = read(reference / 'suporte_asa.stl')-PIVOT
    sup = sup_tri.reshape(-1, 3)
    # Bound the support by 1-mm X strips; a single bounding box incorrectly
    # places the top of the round ears over the low base/poles as well.
    edge_a = sup_tri.reshape(-1, 3)[:, [0, 2]]
    edge_b = np.roll(sup_tri, -1, axis=1).reshape(-1, 3)[:, [0, 2]]
    def heights_in_strip(points, a, b, left, right):
        vals = [points[(points[:, 0] >= left) & (points[:, 0] <= right), 1]]
        for x in (left, right):
            mask = (np.minimum(a[:, 0], b[:, 0]) < x) & (np.maximum(a[:, 0], b[:, 0]) > x)
            aa, bb = a[mask], b[mask]
            vals.append(aa[:, 1]+(bb[:, 1]-aa[:, 1])*(x-aa[:, 0])/(bb[:, 0]-aa[:, 0]))
        return np.concatenate(vals)
    strips = []
    for left in np.arange(sup[:, 0].min(), sup[:, 0].max(), 1.):
        right = min(left+1, sup[:, 0].max())
        top = heights_in_strip(sup[:, [0, 2]], edge_a, edge_b, left, right).max()
        strips.append((left, right, top))
    min_clear = float('inf')
    for angle in np.linspace(-20, 20, 801):
        rad = math.radians(angle)
        rotated = tip @ np.array([[math.cos(rad), -math.sin(rad)],
                                  [math.sin(rad), math.cos(rad)]])
        next_points = np.roll(rotated, -1, axis=0)
        for left, right, top in strips:
            samples = heights_in_strip(rotated, rotated, next_points, left-delta, right+delta)
            min_clear = min(min_clear, samples.min()-top-delta)
    assert min_clear > 0, min_clear

    # Check original lug below Z=14 mm against the new wing: the source
    # geometry is imported without scaling and retains its original bore.
    render(CHECK / 'encaixe_preservado_REFERENCIA.stl', 'encaixe')
    lug = read(CHECK / 'encaixe_preservado_REFERENCIA.stl').reshape(-1, 3)
    bore_vertices = lug[np.abs(np.linalg.norm(lug[:, [0, 2]], axis=1)-1.7) < 0.0001]
    assert len(bore_vertices) > 50
    assert abs(np.ptp(lug[:, 1])-15) < 0.001
    # Every support triangle which reaches the rotating lug is outside
    # Y=±8; lug Y=±7.5 and neck Y=±5 are invariant under pitch rotation.
    high_support = sup_tri[sup_tri[:, :, 2].max(axis=1) >= -8.01]
    assert ((high_support[:, :, 1].min(axis=1) >= 7.9999) |
            (high_support[:, :, 1].max(axis=1) <= -7.9999)).all()

    frontal = []
    for angle in (0, 5, 10, 15, 20):
        b = transform(body, rotation('y', angle))
        projected = float(np.ptp(b[:, 2])*114)
        frontal.append(dict(angulo_graus=angle, area_projetada_corpo_mm2=projected,
                             fracao_secao=projected/(120*120)))

    report = dict(resultado='PASSOU', unidade='mm',
        criterios=dict(camara_comprimento=200, secao=[120, 120], folga_minima=3,
                       eixo_global=PIVOT.tolist(), faixa_angular=[-20, 20]),
        asa=dict(corda=190, envergadura=114, area_mm2=21660,
                 area_original_mm2=3600, razao_areas=21660/3600,
                 curvatura_maxima_mm=3.8, espessura_nominal_percentual=8,
                 bordo_fuga_mm=0.8, encaixe_largura_mm=15, furo_mm=3.4),
        malha_impressao=mesh, envelope_continuo_mm=envelope.tolist(),
        folgas_minimas_mm=margins,
        candidato_191mm_envelope=bounds191.tolist(),
        criterio_maximo='Maior corda inteira neste perfil e eixo central, com folga de 3 mm e rotação ±20°; envergadura = 120 - 2×3.',
        folga_conservadora_corpo_suporte_intervalo_completo_mm=min_clear,
        folga_lateral_encaixe_orelhas_mm=0.5,
        erro_interpolacao_sweep_mm=delta,
        intersecoes=collisions, envelopes_por_angulo=angles,
        projecao_frontal_corpo=frontal,
        limites=['Geometria digital; sem ensaio físico, CFD ou verificação estrutural.',
                 'Os modelos da célula/ventoinha V7 são anteriores às medidas reais registradas em outubro.',
                 'Ferragens reais não modeladas. Encaixe original preservado, conferir M3 × 35 na montagem.',
                 'Área ampliada não garante força mensurável: velocidade, calibração, ruído e bloqueio precisam ser medidos.'])
    (CHECK / 'relatorio.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n')
    write(VIEW / 'Asa_e_suporte_APENAS_VISUALIZAR.stl',
          np.concatenate([wing, read(reference / 'suporte_asa.stl')]))
    print(json.dumps({k: report[k] for k in ['resultado', 'malha_impressao', 'folgas_minimas_mm',
          'folga_conservadora_corpo_suporte_intervalo_completo_mm', 'projecao_frontal_corpo']},
          ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
