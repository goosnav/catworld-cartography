# Catworld / Terra - planet reference package

Open **OPEN_ATLAS.html** for the local gallery, or start with **CATWORLD_Contact_Sheet.jpg**.

- `renders/`: 12 clean PNGs. Six whole-globe angles, four regional globe views, two dam views.
- `annotated/`: 12 matching callout plates. Numbers correspond to the landmark catalogue.
- `model/CATWORLD_Terra.blend`: editable globe, packed textures, named landmarks and ten atlas cameras.
- `model/CATWORLD_Dam_Study.blend`: separate valley-scale dam and settlement study.
- `guide/CATWORLD_Geography_Atlas.pdf`: illustrated guide and annotated reference plates.
- `guide/Geography_and_Design.md`: editable guide text, assumptions, reasoning and sources.
- `guide/Tectonic_Framework.png`: proposed collision belts, rifts and geographic history.
- `guide/Landmark_Catalogue.csv`: 23 named feature coordinates and descriptions.
- `textures/`: albedo, 16-bit height, roughness and land mask.
- `source/`: reproducible scripts, numerical terrain, camera metadata, checks and terrain-data attribution.

## Blender

Built with Blender 5.2.1. The globe opens on the Panterra-facing camera. Frames 1-10 select the ten globe cameras and matching illumination: front, east, west, far side, north pole, south pole, Panterra close, impact basin, southern continent and eastern continent. Numpad 0 toggles camera view. Orbit outside camera view to find another drawing angle.

The textures are packed; the model does not need an internet connection. Globe terrain uses fivefold radial height exaggeration for readability. The physical height field remains in metres. The dam uses its own local kilometre scale without vertical exaggeration. Its buildings and structural details cannot be resolved on the whole globe.

The clean globe PNGs have transparent backgrounds. They are separately lit, cloud-free satellite-style references, not simultaneous physical photographs. Use the full PNG for drawing, not the smaller PDF reproduction. The remaining limitations are documented in the guide.

## Key decisions

Map 5 controls the overall arrangement. The later revisions narrow central Panterra, sharpen capes, deepen gulfs, enlarge the iron-rich impact basin and give the southern and eastern continents distinct relief and coast types. The mountain system is a broad collision belt with warped real ridge-and-valley relief, not a line of isolated cones. Exact tectonic motions and climate are proposed, not simulated.

Radius: 6,100 km. Tilt: 23.4 degrees. Orbital period: 4,000 Earth years, as requested. The guide explicitly retains the unresolved requirement for Earth-like warmth on that long orbit. All new geographic labels are proposals; real city labels remain shorthand.

## Rebuild

From this folder, install Python dependencies in a local virtual environment: `numpy`, `scipy`, and `pillow`. Run `python source/build_terrain.py`, then `blender -b --python source/build_blender.py`. Run `blender -b --python source/build_dam.py` for the inset. Run `blender -b --python source/finalize_model.py` after the globe render pass to restore its opening view and animate the lights for each camera. The bundled analogue DEM avoids a network dependency. To rebuild the guide and callout plates, install `reportlab`, then run `python source/make_tectonics.py` and `python source/package_atlas.py`; the layout scripts use the Arial fonts bundled with macOS. These commands regenerate model and render files in this package.

Terrain data credit and modification details are in `source/TERRAIN_ATTRIBUTION.md` and the guide. The original pitch deck and private message screenshots are not included in this delivery.
