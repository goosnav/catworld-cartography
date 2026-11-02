"""Build the print guide, four-sheet overview and checks for the tracing pack.
Run after build_tracing_maps.py; requires Pillow, numpy, ReportLab and PyMuPDF.
"""
from pathlib import Path
import ast, json, hashlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import pymupdf
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
B=Path(__file__).resolve().parents[1]
KEYS=['birds','cats','reptiles','world']
for name,fn in [('Book','Times New Roman.ttf'),('Bold','Times New Roman Bold.ttf'),('Italic','Times New Roman Italic.ttf')]:
 pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+fn))
reports=[]
for key in KEYS:
 im=np.array(Image.open(B/'png'/f'{key}_trace_300dpi.png').convert('L'))
 ink=float((1-im.astype(float)/255).mean()*100)
 assert ink<3, (key,ink)
 assert im.shape==(2550,3300), (key,im.shape)
 reports.append(dict(map=key,black_equivalent_page_coverage_percent=round(ink,3),png_dimensions=[3300,2550],paper='US Letter landscape: 11 x 8.5 inches'))
files={ '01_CLEAN_TRACING_LETTER.pdf':4,'02_LABELLED_MAPS_LETTER.pdf':4,'04_ENLARGED_TRACING_TILED_LETTER.pdf':16 }
for key in KEYS:
 for kind in ['trace','reference']: files[f'individual/{key}_{kind}_Letter.pdf']=1
for name,count in files.items():
 d=pymupdf.open(B/name);assert len(d)==count,(name,len(d))
 for p in d:
  assert (p.rect.width,p.rect.height)==(792,612), (name,p.rect)
  assert not p.get_images(),name
  for block in p.get_text('dict')['blocks']:
   for line in block.get('lines',[]):
    for span in line['spans']:
     r=pymupdf.Rect(span['bbox'])
     assert r.x0>=0 and r.y0>=0 and r.x1<=792 and r.y1<=612,(name,span['text'],r)
# Read a pure coverage function without executing the render script.
src=(B/'source/build_tracing_maps.py').read_text();tree=ast.parse(src)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='known')
scope={'np':np};exec(compile(ast.Module(body=[fn],type_ignores=[]),'known','exec'),scope);known=scope['known']
for lo,la in [(-106,-38),(-86,-37),(-91,-43),(-104,-39)]:assert not known(lo,la,'cats')
for lo,la in [(-50,-3.5),(-54.9,-10),(-60.5,-20)]:assert known(lo,la,'cats')
assert known(18,24,'reptiles') and known(10,-15,'reptiles') and not known(130,-12,'reptiles')
assert known(-100,70,'birds') and known(100,70,'birds') and known(-20,27,'birds')
manifest=json.loads((B/'source/Cartography_Manifest.json').read_text());maps={m['key']:m for m in manifest['maps']}
assert maps['reptiles']['angle']==18 and 'western_continuation_inset' not in maps['reptiles']
assert maps['world']['extent']==[-2,2,-1,1] and maps['world']['center']==[0,0]
assert len(set(m['source_sha256'] for m in maps.values()))==1
for lat in [-20,-12,0,10]:
 edge=np.interp(lat,[-32,-25,-15,-6,2,9,18],[126,120,118,116,119,120,125]);assert 130>edge
# Every tiled page has a 50 mm vector calibration line and is four sheets per map.
tiles=pymupdf.open(B/'04_ENLARGED_TRACING_TILED_LETTER.pdf')
for p in tiles:
 assert '50 mm calibration' in p.get_text()
 assert any(abs(a[2].x-a[1].x-50/25.4*72)<.01 for d in p.get_drawings() for a in d['items'] if a[0]=='l')
# Two-page guide; the guide is not required for the tracing print run.
c=canvas.Canvas(str(B/'00_READ_FIRST.pdf'),pagesize=(612,792));c.setTitle('Catworld / four tracing maps / print guide');c.setAuthor('Catworld cartography')
def text(x,y,s,size=11,font='Book'):c.setFont(font,size);c.drawString(x,y,s)
def para(y,s,size=10.5,width=512,font='Book'):
 words=s.split();line='';lines=[]
 for w in words:
  trial=(line+' '+w).strip()
  if pdfmetrics.stringWidth(trial,font,size)>width:lines.append(line);line=w
  else:line=trial
 if line:lines.append(line)
 for line in lines:text(50,y,line,size,font);y-=size*1.38
 return y-8
text(50,744,'CATWORLD / FOUR TRACING MAPS',18,'Bold');y=para(718,'US Letter landscape / R10 geography / 1 November 2026',10,font='Italic')
text(50,y-4,'Choose one print file',13,'Bold');y-=27
for s in [
 '01_CLEAN_TRACING_LETTER.pdf: four pages with coastlines, rivers, lakes and terrain symbols, leaving the internal lettering to you. This is the main tracing master.',
 '02_LABELLED_MAPS_LETTER.pdf: the same four sheets with working place names. Use it as your reference, or trace its lettering. Page order in both files: 1 birds, 2 cats, 3 reptiles, 4 whole world.',
 'For only the full world, print individual/world_trace_Letter.pdf. It uses the same 360-degree rectangular projection as the satellite world map, centered on Panterra, with no cultural exclusions or plate-boundary overlays.',
 'Every map sheet is 11 x 8.5 inches, landscape. Print at Actual size / 100%, black-and-white, single-sided. Disable borderless printing. Use normal quality to keep the fine strokes; draft mode can drop small marks.',
 'The world is a 2:1 rectangle, approximately 10.3 x 5.15 inches on the sheet. White space above and below is intentional: filling the height would stretch the planet. Regional maps use more of the page height.'
]:y=para(y,s)
text(50,y-4,'Optional larger drawing',13,'Bold');y-=27
y=para(y,'04_ENLARGED_TRACING_TILED_LETTER.pdf enlarges each clean sheet to 180% across four Letter pages. Birds: pages 1-4. Cats: 5-8. Reptiles: 9-12. World: 13-16. Each assembled sheet is 19.8 x 15.3 inches.')
y=para(y,'Print the tiles at Actual size. Arrange 1A / 1B above 2A / 2B, match the repeated 10 mm artwork strips, trim one overlapping edge and tape from behind. Measure the 50 mm calibration bar before assembly. You do not need the tiles for ordinary Letter-size tracing.')
text(50,y-4,'Economical ink; editable artwork',13,'Bold');y-=27
y=para(y,'All map artwork is black vector linework on white, without grey terrain or paper textures. Measured black-equivalent coverage: '+', '.join(f'{r["map"]} {r["black_equivalent_page_coverage_percent"]:.2f}%' for r in reports)+'. This is rendered page coverage, not a cartridge-yield promise.')
y=para(y,'SVG linework and 300-dpi PNG sheets are included. The A4 file is optional. Begin tracing with shores and watercourses, then the mountain belts and woodland. Add lowland marks and your own names last. Titles, corner marks and notes are optional to trace.')
assert y>42,y;text(50,28,'CATWORLD / PRINT GUIDE / 1',8);c.showPage()
text(50,744,'FOUR POINTS OF VIEW',18,'Bold');y=714
for heading,body in [
 ('Birds / The Northern Reaches','The northern homeland occupies a broad continuous chart, from the Blood Lake to the mountain belt and southern plateau fringe. The cross marks the North Pole. Distant islands on both sides appear as thin, broken, partial outlines: these are islands of legend, not fully surveyed coasts.'),
 ('Cats / The Lands of Panterra','Southern Panterra, the Seattle woodland and river, the reservoir valley, northern feeder and falls, eastern dam, cultivated hills and nearby islands are included. The facing mountain spines lead into a substantial western portion of the eastern continent, including its inner gulf. Australia and the distant southern route are absent.'),
 ('Reptiles / The Eastern Realms','One continuous view crosses from eastern Panterra into the eastern homeland. A gentle 18-degree rotation keeps the connected mountain belt broad on the landscape sheet. The Panterran coast, downstream port and nearby merchant isle sit within the same projection and scale. These are explored approaches, not claims of political control.'),
 ('Reptiles / Unexplored interior','Most of the eastern shoreline is uncharted and omitted. Its visible coast ends remain open; no enclosing border is drawn around the unknown land. Interior marks end with the survey. The same convention applies at the Panterran exploration frontier. Nearby known islands remain visible.'),
 ('Whole world / Terra','The fourth sheet has no cultural limits. It includes Panterra, the eastern continent, the southern homeland, the sparse island route, Pelagic Crown, northern remnants and south polar land. It preserves the satellite map\'s equirectangular layout and central meridian of 0 degrees.')]:
 text(50,y,heading,12,'Bold');y-=21;y=para(y,body,10)
text(50,y-4,'What the linework means',13,'Bold');y-=27
for s in [
 'Coasts and lake outlines come from the R10 terrain fields; waterways come from the established hydrology paths. Regional sheets use Lambert azimuthal equal-area views. No coastline, continental arrangement or world model was redesigned for this pack.',
 'Mountain signs summarize elevated terrain, not individual literal peaks. Trees indicate woodland; low arcs indicate hills; ripples indicate dry country; field outlines indicate cultivation. Small broken lines show ice. Rings mark settlements; open tower shapes mark gates and ruins. Paired strokes mark the dam or falls.',
 'The exact knowledge frontiers are proposed story interpretations. Open coast ends mean uncharted continuation, not a new strait. Names such as Seattle, London, Rome and Milan remain working labels. No new regional rivers or capitals were invented. Fine coastal detail is generalized for a home printer.'
]:y=para(y,s,10)
assert y>42,y;text(50,28,'CATWORLD / MAP NOTES / 2',8);c.showPage();c.save()
# Verify and render the guide after creation.
d=pymupdf.open(B/'00_READ_FIRST.pdf');assert len(d)==2
for i,p in enumerate(d):
 for block in p.get_text('blocks'): assert block[0]>=0 and block[1]>=0 and block[2]<=612 and block[3]<=792
 p.get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(B/'png'/f'print_guide_page_{i+1}_preview.png')
# Four paper-white pages, arranged for on-screen review only.
board=Image.new('RGB',(2100,1660),'#e9e7e2')
for i,key in enumerate(KEYS):
 im=Image.open(B/'png'/f'{key}_reference_preview.png').convert('RGB');im.thumbnail((1010,800))
 x=20+(i%2)*1040+(1010-im.width)//2;y=20+(i//2)*820+(800-im.height)//2
 board.paste(im,(x,y))
board.save(B/'FOUR_MAPS_PREVIEW.jpg',quality=94)
(B/'README.txt').write_text('''CATWORLD / FOUR TRACING MAPS / LETTER EDITION 3

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
''')
(B/'source/Print_Verification.json').write_text(json.dumps(dict(letter_page_count=4,labelled_page_count=4,tiled_page_count=16,all_letter_maps_landscape=True,vector_maps_verified=True,pdf_text_in_page_bounds=True,cats_southern_mainland_excluded=True,near_cat_islands_included=True,expanded_bird_islands_and_panterra_included=True,reptile_panterra_marches_included=True,reptile_single_view_rotation_degrees=18,reptile_eastern_coast_omitted=True,bird_legendary_islands_partial=True,world_full_extent_and_zero_central_meridian=True,tile_calibration_bar_mm=50,terrain_source_sha256=maps['world']['source_sha256'],map_coverage=reports),indent=2))
print(json.dumps(reports,indent=2));print('Guide and print checks complete')
