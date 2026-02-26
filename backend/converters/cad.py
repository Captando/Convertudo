"""Conversor CAD: STEP / IGES → STL / OBJ via gmsh."""
from pathlib import Path


def convert(input_path: str, output_path: str, target_format: str) -> None:
    try:
        import gmsh
    except ImportError:
        raise RuntimeError(
            "Instale: pip install gmsh\n"
            "Em alguns sistemas também é necessário: brew install gmsh"
        )

    target_format = target_format.lower()
    if target_format not in ("stl", "obj"):
        raise ValueError(f"CAD não suporta saída: {target_format}")

    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 0)

    try:
        gmsh.model.add("cad_model")
        gmsh.model.occ.importShapes(input_path)
        gmsh.model.occ.synchronize()

        # Gerar malha de superfície (2D)
        gmsh.option.setNumber("Mesh.Algorithm", 6)   # Frontal-Delaunay
        gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 1)
        gmsh.option.setNumber("Mesh.MinimumCirclePoints", 20)
        gmsh.model.mesh.generate(2)

        if target_format == "stl":
            gmsh.option.setNumber("Mesh.Binary", 0)

        gmsh.write(output_path)

    finally:
        gmsh.finalize()

    if not Path(output_path).exists():
        raise RuntimeError("gmsh não gerou o arquivo de saída")
