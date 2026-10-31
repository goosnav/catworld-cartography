# Catworld / Terra — revision 2

Open **OPEN_ATLAS.html** for the complete offline gallery. Start with **CATWORLD_Contact_Sheet.jpg** to choose a drawing angle.

This revision connects three continental cores with a broad collision belt, corrects the far-side desert and wet regions, develops both poles, integrates the impact basin and adds a long drowned island bridge. The primary waterway runs **Seattle → super-lake → dam → downstream city**. London and Rome sit near the lake.

## Contents

- `renders/`: 14 clean PNGs — six whole-globe views, six regional globe studies, two local dam studies.
- `annotated/`: 14 matching reference plates, including flow arrows on the Seattle and Panterra studies.
- `model/CATWORLD_Terra.blend`: editable globe with packed textures, 30 named geographic anchors and 12 atlas cameras.
- `model/CATWORLD_Dam_Study.blend`: separate valley-scale dam and settlement study, retained from the previous iteration.
- `guide/CATWORLD_Geography_Atlas.pdf`: illustrated geography guide and all annotated plates.
- `guide/Geography_and_Design.md`: editable explanation, assumptions, proposed history and sources.
- `guide/Tectonic_Framework.png`: three-core collision system, rifts, drowned shelf and moisture routes.
- `guide/Landmark_Catalogue.csv`: 30 proposed feature locations and descriptions.
- `textures/`: 4K albedo, 16-bit height, roughness and land mask.
- `source/`: build scripts, physical elevation data, hydrology and camera metadata, verification records and terrain attribution.

## Blender and drawing

Built with Blender 5.2.1. Frames 1–12 select the globe cameras and matching illumination. The views are front, east, west, far side, north pole, south pole, Panterra close, impact basin, southern continent, eastern continent, Seattle waterway and archipelago. Numpad 0 toggles camera view. Orbit normally to choose another angle. Textures are packed, so the model works offline.

The globe uses **10× radial relief exaggeration** to make the enormous ranges legible from orbit. The numerical height field remains in physical metres and peaks at 10.8 km. River widths are exaggerated for visibility. The separate dam model uses kilometre units without vertical exaggeration; its structures are too small to resolve on the global mesh.

Clean PNGs have transparent backgrounds. Each camera has its own drawing-friendly illumination. These are cloud-free satellite-style references, not simultaneous photographs. Use the full PNGs for drawing rather than the smaller PDF plates.

Radius: 6,100 km. Tilt: 23.4°. Orbital period: 4,000 Earth years. The guide preserves that orbit while explaining the unresolved heating premise and the implications of thousand-year seasons. Climate, plate history and ice extent are reasoned worldbuilding proposals, not simulations. New labels and city placements are proposals.

## Rebuild

Install Python packages `numpy`, `scipy`, `pillow`, `reportlab` and `pymupdf` in a virtual environment. From this package folder:

```sh
python source/build_terrain.py
blender -b -t 8 --python source/build_blender.py
blender -b --python source/build_dam.py
blender -b --python source/finalize_model.py
python source/make_tectonics.py
python source/package_atlas.py
python source/verify_delivery.py
```

Use `blender -b -t 8 --python source/build_blender.py -- --draft` for six fast review views. The bundled analogue elevation sample avoids a network download. The annotation/PDF scripts use Arial fonts bundled with macOS. Rebuilding regenerates files in this package. The SHA256 manifest describes the delivered files and must be regenerated after edits.

Terrain attribution is in `source/TERRAIN_ATTRIBUTION.md`. The original pitch deck and private message screenshots are not included. The repository's first commit preserves the previous iteration; the stable `CATWORLD_Planet/` directory contains the current revision.
