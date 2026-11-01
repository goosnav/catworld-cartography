# Terra / R5 technical companion

The illustrated creator guide is the main explanation. R5 supersedes the former three-connected-core layout and the former northern maritime mainland.

## Current geography

Panterra and the eastern dry continent retain their shortened, broad mountain connection. The separate southern mainland covers approximately 10.38 million km2 and spans roughly 15-51 degrees south. It has an old dry shield, salt basins, an eastern escarpment, a cooler southern coast and a substantial eastern archipelago. A small northern remnant survives; the former northern maritime core is open ocean. Deep water separates the southern and eastern continents. The residual island arc off the eastern continent is removed. The southern continent's only candidate former crossing runs east through its archipelago toward Panterra.

The eastern island region contains large angular continental fragments, drowned sounds and a shallow ribbon toward Panterra. At present sea level it is not a continuous land connection. In the stored height field it becomes connected at the proposed -65 m lowstand. The lowstand geometry is checked with periodic longitude connectivity. Ice mass, relative sea level, chronology and local crossing safety have not been simulated.

## One specified epoch

The creator's seasonal direction is northern late autumn / southern late spring, with northern winter approaching. The proposed exact epoch is solar longitude 255 degrees. For a circular 4,000-year orbit this is 833 years after the northern autumn equinox and 167 years before the northern winter solstice. High northern latitudes can already have winter conditions; lower Panterra remains milder. Southern spring does not remove the desert or instantly melt grounded polar ice.

Northern snow and pack ice are advancing. The Blood Lake has broken shore ice and an open red centre. Southern ocean pack has retreated while grounded polar ice and high mountain glaciers persist. Southern coastal woodland, wet eastern slopes, dry subtropical interior and cooler southern valleys coexist in this snapshot. No global circulation, vegetation or ice-sheet simulation has been run.

The proposed crossing 1,100 years before the present falls in the previous southern winter / northern summer. Southern grounded-ice storage must have outweighed northern ice loss to lower global sea level; later net land-ice loss must have flooded the route. Floating sea ice alone cannot provide this mechanism. These are explicit conditions of the scenario, not automatic consequences of opposite seasons. The habitable heat source for a 4,000-year orbit remains unresolved.

## Water and model scales

Seattle -> Great Reservoir -> Great Dam -> downstream metropolis. London/Rome sit near the lake. The graded primary river and outlet remain downhill. Lake surface: 690 m. Globe relief is exaggerated 10x and rivers are widened for drawing clarity. Physical elevations are stored in metres. The globe radius is 10 Blender units for a physical radius of 6,100 km. Textures are 4096 x 2048, about 9.4 km per texel at the equator.

The local dam study remains unchanged: 1 unit = 1 km, 4.8 km crest, approximately 470 m structural height. Local structures, village terraces and abrupt hydraulic drops are below planetary texture resolution. The globe and dam models must be converted to a common scale before combination.

## Build and inspection

`build_terrain.py` reconstructs the sketch and original terrain, then calls the intermediate R4 `reshape_geography.py` and final R5 `revise_southern.py`. The R5 stage must run once on R4 fields, not repeatedly on itself. Delivered fields already contain R5 and can directly rebuild the globe. Full base reconstruction uses the traced sketch coordinates and Himalayan analogue already bundled in the source directory; the original private sketches are not needed to execute the scripts.

`build_blender.py` constructs the textured globe and renders twelve cameras. `finalize_model.py` binds camera lighting to frames 1-12 and verifies packed textures. Frames 1-2 in the separate dam file select context/detail. Rendering uses 16 Cycles samples and denoising. Cameras use useful daylight for drawing; they do not show the actual darkness of the seasonal epoch.

`make_epoch_figures.py` builds the current seasonal map, tectonic schematic, historical lowstand comparison and R4/R5 comparison. `make_explanatory_figures.py` builds the physical-process diagrams. `package_atlas.py` makes annotations, the gallery, catalogue and statistics. `build_creator_guide.py` makes the comprehensive PDF and editable Markdown. `verify_delivery.py` checks image dimensions, packed maps, primary grades, city sites and gallery links.

The guide distinguishes confirmed creator direction, development-deck context, cartographic proposals and open science/engineering decisions. No political borders or final city names are implied by a biome. Terrain attribution remains in `source/TERRAIN_ATTRIBUTION.md`.
