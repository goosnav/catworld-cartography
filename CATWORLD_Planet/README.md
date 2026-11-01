# Catworld / Terra - Revision 8

Start with **guide/CATWORLD_Creator_Guide.pdf**, the illustrated creator/showrunner guide. Use **OPEN_ATLAS.html** to browse full-resolution drawing references offline.

The eastern continent swings eight degrees south around its mountain junction. The independent southern mainland has a new asymmetric coastline, sits farther southeast and closer to Panterra, and has a sparse eastward chain of five islands: two large fragments, one middle island and two small remnants toward Panterra. Open ocean still separates it from the eastern continent. The north is a wide mountain province, with steppe foothills below; Seattle has broad western forest country, and southern settled districts have fertile rolling agricultural land.

The northern mountain river crosses the upper plateau and falls into the reservoir valley. **The lake drains west through Seattle to the sea**, across a natural high bedrock sill. The eastern megadam controls a separate lower outlet toward the downstream city. This supersedes the old Seattle-into-lake arrangement.

## Contents

- `guide/CATWORLD_Creator_Guide.pdf`: illustrated world guide, sources, 36-landmark catalogue, model specifications and sixteen reference plates.
- `guide/Creator_Guide.md`: editable guide text.
- `guide/Geography_and_Design.md`: technical companion.
- `guide/Revision_Comparison.jpg`: R7/R8 terrain and polar comparison.
- `guide/Tectonic_Framework.png`, `Seasonal_Epoch.png`, `Migration_Lowstand.png`: world-scale explanation plates.
- `guide/Waterway_Logic.png`, `Plateau_Valley_Section.png`, `Mountain_Section.png`, `Rainshadow_Section.png`, `Long_Seasons.png`, `Story_Geography.png`: process diagrams.
- `guide/Seasonal_Reference.csv`: geometric daylight at the stated epoch.
- `guide/Landmark_Catalogue.csv`: names, descriptions and coordinates.
- `renders/`: sixteen clean PNGs: thirteen globe views, two dam views and one waterfall study.
- `annotated/`: matching numbered plates; regional hydrology plates include flow arrows.
- `model/CATWORLD_Terra.blend`: editable globe, four packed maps, thirteen cameras and 36 anchors.
- `model/CATWORLD_Dam_Study.blend`: local gorge, dam, terraces and two saved cameras.
- `model/CATWORLD_Waterfall_Study.blend`: local plateau river and cascade study.
- `textures/`: 8K albedo plus 4K working albedo, 16-bit surface height, roughness and land mask.
- `source/`: build scripts, physical terrain fields, metadata, verification records and terrain attribution.
- `CATWORLD_Contact_Sheet.jpg`: index of all views.

## Blender and drawing

Built with Blender 5.2.1. Globe frames 1-13 select atlas cameras and matching lighting. Dam frames 1-2 select context/detail. The waterfall file has one camera. Numpad 0 toggles camera view. Textures are packed for offline use.

The globe uses **10x radial relief exaggeration**, and rivers are widened for readability. Physical elevations remain in metres. The globe radius is ten Blender units for a physical radius of 6,100 km. Its physical terrain grid is 4096 x 2048 (about 9.4 km per texel at the equator). The 8192 x 4096 colour map refines river edges; it does not add elevation resolution. The local dam and waterfall models use one unit per kilometre with true relief. They are separate landform/engineering concepts, not exact high-resolution extracts from the globe.

Clean globe PNGs have transparent backgrounds. Clouds are omitted and each reference has useful daylight for drawing, even where the seasonal epoch implies polar night. Use full PNGs for close study; the PDF embeds compressed copies.

Radius: 6,100 km. Tilt: **35 degrees**. Orbit: 4,000 Earth years. Proposed epoch: Ls 255 degrees, north late autumn / south late spring. The exact epoch, former 65 m lowstand, crossing date, heat source, ice mass, discharge and engineering remain design hypotheses. No global climate, plate-motion, erosion or hydraulic simulation has been run.

## Rebuild on macOS

Install `numpy`, `scipy`, `pillow`, `reportlab` and `pymupdf`. Run from the package directory:

```sh
BLENDER="/Applications/Blender.app/Contents/MacOS/Blender"
# Optional full terrain reconstruction; delivered terrain already contains R8.
# python source/build_terrain.py
"$BLENDER" -b -t 8 --python source/build_blender.py
"$BLENDER" -b -t 8 --python source/build_dam.py
"$BLENDER" -b -t 8 --python source/build_waterfall.py
"$BLENDER" -b --python source/finalize_model.py
"$BLENDER" -b --python source/finalize_dam.py
"$BLENDER" -b --python source/verify_waterfall.py
python source/make_epoch_figures.py
python source/make_explanatory_figures.py
python source/make_revision_comparison.py
python source/package_atlas.py
python source/build_creator_guide.py
python source/verify_delivery.py
```

Add `-- --draft` to the globe build command for fast previews. The full terrain pipeline rebuilds its predecessor stages before R6, R7 and R8; do not apply `revise_r6.py` `revise_r7.py` or `revise_r8.py` repeatedly to already revised fields. The bundled terrain analogue avoids a download. Document scripts use macOS Arial. Regenerate checksums after any rebuild.

Original private sketches, message screenshots and the pitch deck are excluded from the handoff. Earlier Git commits preserve earlier iterations. The stable repository directory `CATWORLD_Planet/` contains the current release.

## R8 terrain revision

The approved continent layout and five-island crossing are preserved. This pass removes folded elevation-sampling artefacts, develops broader dissected relief, varies river widths and bends, reshapes the small lakes, and rebuilds the land-cover and snow transitions. Spherical polar fields remove the meridian pinching. Mineral water and coastal staining vary through the impact basin; the local waterfall has broken lips, near-vertical drops and rock debris.

Read `guide/Terrain_Design_Review_R8.md` for the feature-by-feature reasoning and remaining limits. These are process-informed art decisions, not numerical erosion or climate results.
