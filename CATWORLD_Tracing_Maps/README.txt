CATWORLD / FOUR TRACING MAPS / SKETCH EDITION 4

Print 01_CLEAN_TRACING_LETTER.pdf for your own lettering, or 02_LABELLED_MAPS_LETTER.pdf for named maps.
Four sheets: birds, cats, reptiles, whole world. ALL LANDSCAPE, US Letter 11 x 8.5 inches. Print at 100% / Actual size.
Only need the world? Print individual/world_trace_Letter.pdf.
Read 00_READ_FIRST.pdf for the printing and interpretation guide.

BIRDS: broad northern homeland and southern plateau fringe; partial islands of legend.
CATS: Panterra and roughly one third of the eastern continent; no Australia.
REPTILES: one gently rotated view with eastern Panterra; most eastern coastline is unexplored and omitted.
WORLD: complete equirectangular world centered on Panterra, preserving the 2:1 satellite map proportions.

START HERE FOR LARGE DIGITAL TRACING:
  png/cats_trace_artwork.png (Panterra, artwork only)
  png/birds_trace_artwork.png
  png/reptiles_trace_artwork.png
  png/world_trace_artwork.png
Each artwork canvas is 13,200 pixels wide, with its natural aspect ratio and a small margin.
No title, compass, corner frame or footer takes up the drawing canvas.

FULL SHEETS: png/*_trace_master.png are 13,200 x 10,200 pixels (134.6 megapixels).
These are rendered from the vector artwork at 1200 dpi, not enlarged from small PNGs.
The artwork-only PNGs have 300-dpi metadata for large-format use (44 inches wide).
PNG compression keeps these mostly white canvases relatively small in bytes.
The *_preview.png files are for browsing only; do not use them as drawing masters.
The *_300dpi.png files remain 3300 x 2550 Letter-size compatibility copies.
Editable SVGs and vector PDFs can be enlarged further without pixelation.
Artwork-only PDFs are in individual/*_trace_artwork.pdf.

The supplied CATWORLD_drawn_Maps/panterra_v1.PNG directs the visual style:
strong pen coasts, dotted offshore halos, dark mountain faces, rounded woodland clusters,
and open rolling hills. The same geographic woodland patches carry across the maps.
Black vector lines and black mountain facets on white. No grey terrain fills.
The 16-page tiled PDF is optional: four Letter sheets per map at 180%, with 10 mm overlaps. Do not print it unless you want an enlarged drawing.
03_CLEAN_TRACING_A4.pdf is an optional A4 alternative.

Geography is based on R10, plus the supplied sketch's small volcanic gulf islet at 28.4 E, 17.7 N.
The islet is a tracing-map addition; the R10 planet files are unchanged. Cultural knowledge boundaries are proposed interpretations, not territorial claims. Names are working labels.

Source: source/build_tracing_maps.py and source/finish_print_pack.py.
Dependencies: Python, numpy, scipy, contourpy, shapely, reportlab, pymupdf, Pillow.
Source data: ../CATWORLD_Planet/source/terrain_fields.npz, hydrology_paths.json, features.json.
Rebuild from the repository root (Python 3):
  python3 CATWORLD_Tracing_Maps/source/build_tracing_maps.py
  python3 CATWORLD_Tracing_Maps/source/finish_print_pack.py
  python3 -m unittest discover -s CATWORLD_Tracing_Maps/source
Paths are relative to the repository; built-in PDF Times fonts work on every platform.
Allow roughly 1 GB of free memory for a large canvas; exports are rendered one at a time.
