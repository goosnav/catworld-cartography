# Catworld / Terra - Revision 4

Start with **guide/CATWORLD_Creator_Guide.pdf**: the 43-page creator/showrunner guide explains the complete model, its story geography, design reasoning, assumptions and open decisions. Use **OPEN_ATLAS.html** to browse full-resolution drawing references offline.

This revision shortens the marked mountain bridge from 60 to 25 degrees of longitude (about 58%). The far-side maritime continent is rebuilt northward, with a substantial interior, an old shield, river basins and a southern collision range. Its long southern tail is removed. The eastern dry core gains dune fields and salt basins. The archipelago, polar regions and main Panterran geography remain connected to the same world model.

The primary waterway is **Seattle -> super-lake -> dam -> downstream city**. London and Rome sit near the lake; Amsterdam is the downstream city shorthand. These names and most exact placements remain proposals.

## Contents

- `guide/CATWORLD_Creator_Guide.pdf`: 43-page illustrated guide, sources, 30-landmark catalogue, model specifications and 14 reference plates with readable vector labels.
- `guide/Creator_Guide.md`: editable guide text.
- `guide/Geography_and_Design.md`: technical companion and file index.
- `guide/Revision_Comparison.jpg`: same-angle R2/R4 comparison.
- `guide/Tectonic_Framework.png`: proposed collision history, rifts, shelf bridge and moisture routes.
- `guide/Mountain_Section.png`, `Waterway_Logic.png`, `Rainshadow_Section.png`, `Long_Seasons.png`, `Story_Geography.png`: explanatory diagrams.
- `guide/Landmark_Catalogue.csv`: feature names, descriptions and coordinates.
- `renders/`: 14 clean PNGs: six whole-globe views, six regional globe studies, two dam studies.
- `annotated/`: 14 matching annotated PNGs. Seattle/Panterra plates include flow arrows.
- `model/CATWORLD_Terra.blend`: packed editable globe, 30 landmark anchors and 12 saved cameras.
- `model/CATWORLD_Dam_Study.blend`: local dam, gorge, village, access roads and two saved cameras.
- `textures/`: 4K albedo, 16-bit height, roughness and land mask.
- `source/`: reproducible build scripts, physical terrain data, camera metadata, verification records and terrain attribution.
- `CATWORLD_Contact_Sheet.jpg`: visual index of every rendered view.

## Blender and drawing

Built with Blender 5.2.1. Globe frames 1-12 select the saved atlas cameras and matching lights: front, east, west, far side, north pole, south pole, Panterra close, impact basin, maritime continent, eastern continent, Seattle waterway and archipelago. Dam frames 1-2 select valley context and structural detail. Numpad 0 toggles the camera view. Textures are packed for offline use.

The globe uses **10x radial relief exaggeration**. Physical elevations remain in metres, with a peak near 10.8 km. River widths are exaggerated for visibility. Global texture resolution is roughly 9.4 km per texel at the equator. The dam model uses 1 unit = 1 km; its structures are below global texture resolution. Convert scales before combining these models.

Clean globe PNGs have transparent backgrounds. Each view has drawing-friendly lighting, and clouds are omitted. These are satellite-style worldbuilding references, not simultaneous astronomical photographs. The PDF uses compressed image copies; use the full PNGs for close drawing work.

Radius: 6,100 km. Tilt: 23.4 degrees. Orbit: 4,000 Earth years. The guide preserves that orbit and explains the unresolved heat source. Tectonics, climate, ice extent, engineering and most names remain proposals; no global climate, plate-motion or hydraulic simulation has been run.

## Rebuild on macOS

Install `numpy`, `scipy`, `pillow`, `reportlab` and `pymupdf` in a Python environment. From this package folder:

```sh
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
python source/build_terrain.py
"$BLENDER" -b -t 8 --python source/build_blender.py
"$BLENDER" -b -t 8 --python source/build_dam.py
"$BLENDER" -b --python source/finalize_model.py
"$BLENDER" -b --python source/finalize_dam.py
python source/make_tectonics.py
python source/make_comparison.py
python source/make_explanatory_figures.py
python source/package_atlas.py
python source/build_creator_guide.py
python source/verify_delivery.py
```

For fast drafts, add `-- --draft` to the `build_blender.py` command. The bundled Himalayan analogue avoids a network download. Document scripts use Arial from macOS. Rebuilding regenerates files; regenerate the SHA256 manifest after changes.

The original pitch deck and private message screenshots are not included. Terrain attribution is in `source/TERRAIN_ATTRIBUTION.md`. Earlier commits preserve previous iterations; the repository's stable `CATWORLD_Planet/` folder contains the current delivery.
