"""Exporta pecas, confere malhas e verifica interferencias no OpenSCAD.

Uso: python validar_modelo.py (requer openscad e numpy).
As verificacoes sao geometricas; nao substituem testes das pecas impressas.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json
import hashlib
import struct
import subprocess
import tempfile

import numpy as np

PASTA = Path(__file__).resolve().parent
SCAD = PASTA / "estacao_integrada.scad"
STL = PASTA / "STL"
STL.mkdir(exist_ok=True)
PECAS = ("caixa", "tampa_caixa", "portinha", "base_abrigo", "aleta", "teto",
         "teste_baioneta", "teste_tampa", "teste_aletas")


def ler_stl(path):
    b = Path(path).read_bytes()
    n = struct.unpack("<I", b[80:84])[0]
    assert len(b) == 84 + 50*n, f"STL binario inesperado: {path}"
    dt = np.dtype([("normal", "<f4", (3,)), ("vertices", "<f4", (3,3)), ("attr", "<u2")])
    return np.frombuffer(b, dt, count=n, offset=84)["vertices"].astype(float)


def verificar_malha(path, quantidade):
    t = ler_stl(path)
    v, inv = np.unique(np.round(t.reshape(-1,3), 5), axis=0, return_inverse=True)
    f = inv.reshape(-1,3)
    e = np.concatenate([f[:,[0,1]], f[:,[1,2]], f[:,[2,0]]])
    es = np.sort(e, axis=1)
    _, ei, cont = np.unique(es, axis=0, return_inverse=True, return_counts=True)
    assert (cont == 2).all(), f"Aresta aberta ou nao manifold: {path}"
    sinais = np.where(e[:,0] < e[:,1], 1, -1)
    assert (np.bincount(ei, weights=sinais) == 0).all(), f"Faces inconsistentes: {path}"
    volume = np.einsum("ij,ij->i", t[:,0], np.cross(t[:,1],t[:,2])).sum()/6
    assert volume > 0, f"Volume negativo: {path}"
    pais = np.arange(len(v))
    def raiz(x):
        while pais[x] != x:
            pais[x] = pais[pais[x]]
            x = pais[x]
        return x
    for a,b in e:
        pais[raiz(a)] = raiz(b)
    componentes = len({raiz(i) for i in range(len(v))})
    assert componentes == quantidade, f"{path}: {componentes} solidos, esperado {quantidade}"
    lo, hi = t.min(axis=(0,1)), t.max(axis=(0,1))
    assert abs(lo[2]) < .001, f"Peca fora da mesa Z=0: {path}: {lo}"
    return {"triangulos": len(t), "solidos": componentes, "malha_fechada": True,
            "faces_consistentes": True, "volume_mm3": round(float(volume),3),
            "limites_mm": [lo.round(4).tolist(),hi.round(4).tolist()],
            "dimensoes_mm": (hi-lo).round(4).tolist()}


def exportar(peca):
    out = STL/f"{peca}.stl"
    r = subprocess.run(["openscad", "--hardwarnings", "--export-format", "binstl",
                        "-o", str(out), "-D", f'visualizacao="{peca}"', str(SCAD)],
                       capture_output=True, text=True)
    assert r.returncode == 0, f"{peca}: {r.stderr}"
    return peca, verificar_malha(out, 2 if peca.startswith("teste_") else 1)


def interferencia(nome, a, b, esperar_bloqueio=False, resolucao=96):
    # Usa as definicoes e parametros sem executar o seletor de visualizacao.
    fonte = SCAD.read_text().split("validar() {\n    if (visualizacao")[0]
    codigo = fonte + f"\nintersection() {{ {a} {b} }}\n"
    with tempfile.TemporaryDirectory(prefix="estacao_", dir="/tmp") as td:
        inp, out = Path(td)/"teste.scad", Path(td)/"teste.stl"
        inp.write_text(codigo)
        r = subprocess.run(["openscad", "--export-format", "binstl", "-o", str(out),
                            "-D", f"resolucao={resolucao}", str(inp)], capture_output=True, text=True)
        vazio = not out.exists() and "Current top level object is empty" in r.stderr
        volume, plano = 0., False
        if out.exists():
            t = ler_stl(out)
            volume = abs(np.einsum("ij,ij->i",t[:,0],np.cross(t[:,1],t[:,2])).sum()/6)
            plano = (t.max(axis=(0,1))-t.min(axis=(0,1))).min() < 1e-4
        if esperar_bloqueio:
            assert volume > .01, f"Trava sem bloqueio geometrico: {nome}"
            return nome, {"bloqueio_confirmado": True, "volume_interferencia_mm3": round(volume,4)}
        # Contatos em planos diferentes (ex.: guia e aba da amostra) tambem
        # podem gerar superficies sem volume; CGAL informa apenas 1 volume
        # ambiente quando nao ha regiao solida fechada.
        sem_solido = volume < 1e-5 and 'Volumes:         1' in r.stderr
        # STL binario armazena float32; ao remontar uma face de contato,
        # o arredondamento pode produzir laminas de poucos micrometros.
        tolerancia_volume = 1e-4
        residuo_stl = out.exists() and volume <= tolerancia_volume
        if not (vazio or (plano and volume < 1e-5) or sem_solido or residuo_stl):
            if out.exists():
                destino = PASTA/f"FALHA_{nome}.stl"
                destino.write_bytes(out.read_bytes())
            raise AssertionError(f"Interferencia {nome}: {r.stderr}")
    return nome, ({"estado":"contato dentro da tolerancia numerica",
                   "volume_residual_mm3":round(volume,9),
                   "tolerancia_mm3":tolerancia_volume} if not vazio else "intersecao vazia")


if __name__ == "__main__":
    with ThreadPoolExecutor(max_workers=3) as executor:
        malhas = dict(executor.map(exportar, PECAS))
    # Mesma resolucao dos STL, incluindo a verificacao do percurso.
    casos = [
        ("caixa_tampa", "caixa();", "translate([0,0,altura_caixa]) tampa_caixa();"),
        ("tampa_abrigo_travado", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa]) rotate([0,0,giro_baioneta]) base_abrigo();"),
        ("entrada_baioneta", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa+queda_baioneta]) base_abrigo();"),
        ("meio_giro_baioneta", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa+queda_baioneta]) rotate([0,0,giro_baioneta/2]) base_abrigo();"),
        ("fim_giro_baioneta", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa+queda_baioneta]) rotate([0,0,giro_baioneta]) base_abrigo();"),
        ("base_aleta", "base_abrigo();", "translate([0,0,passo]) aleta();"),
        ("aleta_aleta", "aleta();", "translate([0,0,passo]) aleta();"),
        ("aleta_teto", "aleta();", "translate([0,0,passo]) teto();"),
        ("caixa_abrigo", "caixa();",
         "translate([0,0,z_base_montada]) rotate([0,0,giro_baioneta]) base_abrigo();"),
        ("bloqueio_retorno_sem_levantar", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa]) rotate([0,0,giro_baioneta-5]) base_abrigo();",True),
        ("bloqueio_extracao_sem_girar", "tampa_caixa();",
         "translate([0,0,z_base_montada-altura_caixa+3]) rotate([0,0,giro_baioneta]) base_abrigo();",True),
    ]
    casos.append(("portinha_interferencia_de_pressao", "caixa();", "porta_montada();", True))
    cortes_portinha = '''
    translate([-comprimento_caixa/2-1,0,altura_inicio_porta+porta_altura/2])
    rotate([90,0,90]) difference() {
      portinha();
      for (s=[-1,1]) {
        translate([s*(porta_largura/2+0.075)-0.09,-3.01,1.4]) cube([0.18,6.02,1.4]);
        translate([-3.01,s*(porta_altura/2+0.075)-0.09,1.4]) cube([6.02,0.18,1.4]);
      }
    }'''
    casos.append(("portinha_sem_sobreposicao_fora_ressaltos", "caixa();", cortes_portinha))
    for ang in [5,10,20,25]:
        casos.append((f"giro_{ang}_graus", "tampa_caixa();",
            f"translate([0,0,z_base_montada-altura_caixa+queda_baioneta]) rotate([0,0,{ang}]) base_abrigo();"))
    for subida in [4,8,12,18,25]:
        casos.append((f"entrada_subida_{subida}_mm", "tampa_caixa();",
            f"translate([0,0,z_base_montada-altura_caixa+{subida}]) base_abrigo();"))
    for subida in [.3,.6,.9,1.2]:
        casos.append((f"desassentar_{subida}_mm", "tampa_caixa();",
            f"translate([0,0,z_base_montada-altura_caixa+{subida}]) rotate([0,0,giro_baioneta]) base_abrigo();"))
    f=STL/'teste_tampa.stl'
    casos.append(("amostra_tampa_guiada",
        f'translate([20,0,0]) intersection() {{ import("{f}"); translate([-31,-10,-1]) cube([22,20,23]); }}',
        f'translate([-20,-0.3,19]) rotate([180,0,0]) intersection() {{ import("{f}"); translate([9,-10,-1]) cube([22,20,23]); }}'))
    f=STL/'teste_baioneta.stl'
    for ang,subida in [(0,1.2),(15,1.2),(30,1.2),(30,0)]:
        casos.append((f"amostra_baioneta_{ang}_{subida}",
            f'translate([0,0,3]) rotate([180,0,0]) translate([40,0,0]) intersection() {{ import("{f}"); translate([-75,-40,-1]) cube([75,80,25]); }}',
            f'translate([0,0,{6+subida}]) rotate([0,0,{ang}]) rotate([180,0,0]) translate([-40,0,0]) intersection() {{ import("{f}"); translate([0,-40,-1]) cube([75,80,25]); }}'))
    f=STL/'teste_aletas.stl'
    casos.append(("amostra_aletas_montada",
        f'translate([0,0,22.4]) rotate([180,0,0]) intersection() {{ import("{f}"); translate([-11,-11,-1]) cube([22,22,25]); }}',
        f'translate([0,0,40.4]) rotate([180,0,0]) translate([-28,0,0]) intersection() {{ import("{f}"); translate([17,-11,-1]) cube([22,22,25]); }}'))
    with ThreadPoolExecutor(max_workers=3) as executor:
        contatos = dict(executor.map(lambda c: interferencia(*c), casos))
    relatorio = {"openscad": subprocess.check_output(["openscad", "--version"],
                 stderr=subprocess.STDOUT,text=True).strip(),
                 "sha256_scad": hashlib.sha256(SCAD.read_bytes()).hexdigest(),
                 "resolucao_stl": 96, "resolucao_interferencias": 96,
                 "pecas": malhas, "interferencias": contatos,
                 "nota": "Portinha: interferencia de 0,15 mm nos ressaltos e intencional. Travas flexionam durante a montagem. Validacao apenas digital."}
    (PASTA/"validacao.json").write_text(json.dumps(relatorio,ensure_ascii=False,indent=2)+"\n")
    print(json.dumps(relatorio,ensure_ascii=False,indent=2))
