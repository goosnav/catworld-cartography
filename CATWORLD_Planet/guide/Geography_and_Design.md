# R9 update: ocean geography and rectangular maps

The primary rectangular maps are in `world_maps/`: one centered at 180 degrees and one at zero degrees. These are exact longitude rolls of one 8K globe colour texture. The tectonic sheets use those same coordinates. Equirectangular projection is useful for the entire world but stretches polar shapes; the orthographic globe views remain the drawing references for local proportions.

The eastern block has an additional 13-degree southward inclination. The latest green outline supersedes earlier concavity wording: the land bridge and mountain belt sweep south into the lower western side. Five distinct islands form the curved peninsula-to-southern-mainland crossing. Pelagic Crown, three northern fore-islands and scattered volcanic islands/atolls populate selected ocean settings. The tectonic map is a geological proposal, not a solved plate-motion reconstruction. Read `Ocean_and_Tectonics_R9.md` for details.

# Terra / R9 technical companion

The illustrated creator guide explains the world and its design reasoning. R8 preserves the shortened Panterra/eastern mountain connection and the independent southern continent, while revising landforms, hydrology, vegetation and seasons.

## Geography and tectonics

The eastern block rotates eight degrees clockwise around the connection. Its mountain belt rotates with it and broadens into supporting uplands. Northern Panterra becomes a broad orogenic province: folded ranges, high massifs and intermontane valleys. The old impact basin remains embedded within northern crust. The impact is not proposed as the cause of the entire mountain system.

The southern mainland covers approximately 9 million km2, with a new asymmetric outline, dry old interior, wetter eastern margin, southern inlets and an oblique escarpment. It sits southwest of Panterra; the R7 adjustment moves it another 10 degrees east and 1 degree south, shortening the crossing. Five retained island shapes form a sparse chain toward Panterra only. Large, irregular continental fragments sit nearest the southern mainland. The chain tapers into smaller arc remnants with staggered spacing and wider water gaps toward Panterra, using Oceania and the Aleutians as morphological analogues. A continental ribbon supports the proposed lowstand crossing; isolated peaks can represent later arc volcanism. This is a proposed geological history, not a plate reconstruction. Deep ocean separates this southern land from the eastern continent; no linking island arc is added there.

A submerged continental shelf provides a possible former migration route. At the proposed 65 m lower ocean level, that designed shelf becomes connected. Present sea level leaves the southern mainland separate. The connectivity test accounts for the longitude seam. It verifies geometry, not ice volume, chronology or local travel conditions.

## Plateau valley and directed drainage

The northern mountain feeder follows the creator's winding route northwest of the lake, crossing higher plateau terrain before descending about 400 m through a waterfall system into a drowned valley arm. The reservoir surface is about 690 m above sea level. The surrounding plateau is higher: the lake occupies an incised valley within it, not a uniform flat upland.

The natural western overflow crosses a high bedrock saddle near 685 m. It then descends west through Seattle forest country to the ocean. The eastern dam blocks the deeper original valley exit and maintains a separate controlled outlet toward the downstream metropolis. Its foundation and tailwater are lower than the plateau; its crest still has to stand above reservoir level. There is no second western dam.

The local waterfall study uses a 250 m main drop, an 80 m cascade and a 70 m cascade: upper river 1,090 m, intermediate pools 840/760 m, reservoir 690 m. It is a proposed landform, not a fluid simulation. The dam study has an approximately 4.8 km crest and 470 m structural height. The guide distinguishes these design dimensions from engineering feasibility.

Three small outlying lakes sit in separate basins. River paths store directed coordinates and designed water profiles. The final validation samples actual delivered surface elevations to check for uphill segments. Widths and delta branches are exaggerated for drawing clarity.

## Regional environments and season

The most extensive forest is on Panterra's west, around Seattle and its watershed. Northern lower foothills and drier plateau interiors are steppe. Two marked southern mountain groups form older uplifts and a rugged peninsula spine. Their lower slopes feed tributaries. Southern settled districts are fertile rolling agricultural country, with green-and-gold regional variation rather than forests everywhere. Geographic anchors identify regions and working names; they do not define municipal boundaries.

Tilt is 35 degrees. A 4,000-Earth-year near-circular orbit places the proposed Ls 255-degree epoch about 833 years after northern autumn equinox and 167 before northern winter solstice. The north is in late autumn, with wintry highlands and polar darkness; the south is in late spring. The Blood Lake district has no geometric daylight at that snapshot. Reference renders use useful lighting regardless of this darkness.

Stronger tilt intensifies summer as well as winter sunlight contrasts. Snow, sea ice and vegetation are proposed seasonal appearances, not the output of an atmospheric or ice-sheet model. Southern winter could lower sea level only if net grounded-ice storage increased globally. Floating sea ice alone cannot explain the proposed old land crossing. The habitable heat source for the very long orbit remains unresolved.

## Model, data and reproducibility

Globe physical radius is 6,100 km; Blender radius is ten units, with tenfold displayed relief. One 8192 x 4096 colour map and three 4096 x 2048 physical/material maps are packed into the globe. The high-resolution colour layer smooths vector waterways; the physical terrain detail remains 4K. Physical height and visible surface elevation are separately stored in `terrain_fields.npz`; lake and river water surfaces differ from their beds. Local models use kilometre units and true vertical scale, so convert scales before combining them.

`build_terrain.py` reconstructs the initial traced geography, then its R4 transformation, R6 southern rewrite and R6 terrain/hydrology pass followed by R7 and R8 terrain passes and the R9 ocean revision. Run the full pipeline for terrain edits; repeated application of the last pass would accumulate rotation. Previous-stage scripts remain because they are inputs to this reconstruction.

`build_blender.py` renders thirteen cameras; `finalize_model.py` saves their timeline/light bindings and verifies packed textures. The dam and waterfall have separate build scripts. `make_epoch_figures.py` and `make_explanatory_figures.py` generate the world/process diagrams. `package_atlas.py` creates annotations, gallery, CSV and statistics. `build_creator_guide.py` creates the PDF and editable guide. `verify_delivery.py` checks topology, hydrology, metadata and delivered files.

The globe is a satellite-style drawing reference with deliberately readable relief and waterways. Sub-texel roads, houses, individual giant trees and engineering are not resolved globally. Use the regional and local studies for closer design work. The guide's 39 feature anchors are proposals unless explicitly identified as creator direction.

## R8 basin and surface treatment

The new pass retains the geography and replaces the repeated relief patterns with bounded terrain sampling. Northern highlands remain broad, with smaller incised massifs and altitude-controlled snow. Three small lakes have distinct elongated, hooked and irregular basin shapes. Variable-width rivers and tributaries follow their approved corridors. The impact basin has uneven staining and suspended-sediment colours. Polar relief is evaluated in spherical coordinates, avoiding seams and pinching.

See `Terrain_Design_Review_R8.md` for the full feature audit. These are constructed landforms, not an erosion simulation.
