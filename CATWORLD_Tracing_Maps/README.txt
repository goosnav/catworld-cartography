CATWORLD / FOUR TRACING MAPS / LETTER EDITION 3

Print 01_CLEAN_TRACING_LETTER.pdf for your own lettering, or 02_LABELLED_MAPS_LETTER.pdf for named maps.
Four sheets: birds, cats, reptiles, whole world. ALL LANDSCAPE, US Letter 11 x 8.5 inches. Print at 100% / Actual size.
Only need the world? Print individual/world_trace_Letter.pdf.
Read 00_READ_FIRST.pdf for the printing and interpretation guide.

BIRDS: broad northern homeland and southern plateau fringe; partial islands of legend.
CATS: Panterra and roughly one third of the eastern continent; no Australia.
REPTILES: one gently rotated view with eastern Panterra; most eastern coastline is unexplored and omitted.
WORLD: complete equirectangular world centered on Panterra, preserving the 2:1 satellite map proportions.

Black vector lines on white. No grey fills. SVG and 300-dpi PNG exports included.
The 16-page tiled PDF is optional: four Letter sheets per map at 180%, with 10 mm overlaps. Do not print it unless you want an enlarged drawing.
03_CLEAN_TRACING_A4.pdf is an optional A4 alternative.

Geography is derived from the accepted R10 planet, which is unchanged. Cultural knowledge boundaries are proposed interpretations, not territorial claims. Names are working labels.

Source: source/build_tracing_maps.py and source/finish_print_pack.py.
Dependencies: Python, numpy, scipy, contourpy, shapely, reportlab, pymupdf, Pillow.
Source data: ../CATWORLD_Planet/source/terrain_fields.npz, hydrology_paths.json, features.json.
The build script currently uses the canonical Mac project path and Times New Roman from macOS; change MODEL/font paths on other systems.
