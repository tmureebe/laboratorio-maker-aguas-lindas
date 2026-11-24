"""Exporta a malha tátil e suas cores para visualização no F3D. Requer NumPy."""

from pathlib import Path

import numpy as np


def exportar_ply(origem: Path, destino: Path) -> None:
    with np.load(origem) as malha:
        coordenadas = malha["vertices"]
        triangulos = malha["faces"]
        cores_topo = malha["colors"].reshape(-1, 4)[:, :3]

    # A base usa o mesmo castanho do atributo CorClinica no Blender.
    cores_lineares = np.empty((len(coordenadas), 3), dtype=np.float32)
    cores_lineares[:len(cores_topo)] = cores_topo
    cores_lineares[len(cores_topo):] = (0.35, 0.19, 0.09)
    cores_lineares = np.clip(cores_lineares, 0, 1)
    cores_srgb = np.where(
        cores_lineares <= 0.0031308,
        12.92 * cores_lineares,
        1.055 * cores_lineares ** (1 / 2.4) - 0.055,
    )

    vertices = np.empty(
        len(coordenadas), dtype=[("xyz", "<f4", 3), ("rgb", "u1", 3)]
    )
    vertices["xyz"] = coordenadas
    vertices["rgb"] = np.rint(cores_srgb * 255).astype(np.uint8)
    faces = np.empty(len(triangulos), dtype=[("contagem", "u1"), ("indices", "<i4", 3)])
    faces["contagem"] = 3
    faces["indices"] = triangulos

    cabecalho = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {len(vertices)}\n"
        "property float x\nproperty float y\nproperty float z\n"
        "property uchar red\nproperty uchar green\nproperty uchar blue\n"
        f"element face {len(faces)}\n"
        "property list uchar int vertex_indices\nend_header\n"
    )
    with destino.open("wb") as arquivo:
        arquivo.write(cabecalho.encode("ascii"))
        vertices.tofile(arquivo)
        faces.tofile(arquivo)


if __name__ == "__main__":
    saida = Path(__file__).resolve().parents[1] / "saida"
    exportar_ply(
        saida / "validacao" / "geometria_tatil.npz",
        saida / "ulcera_venosa_tatil_colorida.ply",
    )
