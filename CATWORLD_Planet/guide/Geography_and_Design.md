# Catworld / Terra - technical companion, revision 4

The complete current explanation is in `Creator_Guide.md` and `CATWORLD_Creator_Guide.pdf`. This replaces the earlier revision narrative. The PDF is the creator-facing handoff; the PNGs remain the full-resolution drawing references.

## Geographic construction

The original map-5 silhouette is fitted interpretively to a sphere; the sketch has no defined graticule. `build_terrain.py` constructs that base. `reshape_geography.py` compresses the marked eastern connection, rebuilds the maritime continent north of its collision belt, creates its new drainage, updates the island chain and preserves the polar latitude bands. Main Panterran geography and the Seattle-to-reservoir route retain their prior positions.

Three cores remain land-connected. The east-facing bridge endpoint span changes from 60 to 25 degrees of longitude. The maritime continent now has a broad northern interior, an older shield, a southern high range and a short irregular southern foreland. Its new river network uses a reduced elevation grid and smoothed paths; it is not a complete hydrologic simulation. The eastern desert includes proposed erg fields and pale salt pans. The modern island geometry does not establish a complete former dry crossing without a bathymetric reconstruction.

## Physical and display data

Radius: 6,100 km. Tilt: 23.4 degrees. Orbital period: 4,000 Earth years. A 24-hour rotation and northern late-autumn epoch are assumptions. The physical `height` and `surface` arrays are in metres. The globe radius is 10 Blender units, with 10x radial relief. The separate dam study uses kilometre units and a local vertical datum consistent with the proposed reservoir level; its detailed gorge is not extracted from the coarse planetary grid.

`terrain_fields.npz` contains height, water/display surface, land mask, reservoir mask and moisture heuristic. The land mask includes inland reservoir footprint, so its raw area is a continental footprint rather than exposed dry land. The reservoir mask refers to the super-lake. The peak and measured reservoir area are recorded in `statistics.json`.

## Hydrology

The confirmed order is Seattle -> super-lake -> dam -> downstream city. The primary channel has an explicitly graded surface ending at 690 m. The local dam has a 4.8 km crest and about 470 m structural height. Its local tailwater drop is resolved in the inset; the global downstream river profile is smoothed. River width, local village placement and dam structures are below the literal resolution of the global texture. The village's approximate global anchor should be interpreted through the local inset, not as a surveyed site on a global lake pixel.

## Reproducibility and checks

`Geography_Verification.json` records the connected cores, shortened span and new geographic construction. `Hydrology_Verification.json` records the primary channel design. `Model_Verification.json` checks mesh, landmarks, cameras and packed images. `Dam_Model_Verification.json` records the two local camera frames. `Delivery_Verification.json` records image sizes/hashes, gallery links, sampled downhill profiles, city positions and PDF page count. `PDF_Layout_Verification.json` records page content bounds. These checks verify the artifact and key design constraints; they do not validate a physical climate or tectonic simulation.

The full source and model are editable. If terrain changes, rebuild camera metadata and all dependent renders, annotations, guide figures, PDF and manifests together. Keep the numbered feature catalogue synchronized with the model anchors.
