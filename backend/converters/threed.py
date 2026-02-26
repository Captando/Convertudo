"""Conversor de arquivos 3D via trimesh."""
from pathlib import Path


TRIMESH_EXPORT_MAP = {
    "stl":  "stl",
    "obj":  "obj",
    "ply":  "ply",
    "gltf": "gltf",
    "glb":  "glb",
    "3mf":  "3mf",
    "off":  "off",
}


def convert(input_path: str, output_path: str, target_format: str) -> None:
    import trimesh

    target_format = target_format.lower()
    input_ext = Path(input_path).suffix.lstrip(".").lower()

    # Carregar a malha 3D
    mesh = trimesh.load(input_path, force="mesh")

    if mesh is None or (hasattr(mesh, "is_empty") and mesh.is_empty):
        raise ValueError(f"Não foi possível carregar o arquivo 3D: {input_path}")

    fmt = TRIMESH_EXPORT_MAP.get(target_format)
    if fmt is None:
        raise ValueError(f"Formato 3D de saída não suportado: {target_format}")

    mesh.export(output_path, file_type=fmt)
