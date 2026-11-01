from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil,numpy as np
B=Path(__file__).resolve().parents[1]
shutil.copy2(B/'world_maps/03_tectonics_ocean_centered.png',B/'guide/Tectonic_Framework.png')
old=B/'source/reference_R8_world.jpg'
if not old.exists():
 p=B.parent/'CATWORLD_Planet_R8/textures/albedo_8192.png'
 if p.exists():
  a=np.array(Image.open(p));Image.fromarray(np.roll(a,a.shape[1]//2,axis=1)).resize((1800,900)).save(old,quality=94)
if old.exists():
 im=Image.new('RGB',(1900,2040),'#10191f');d=ImageDraw.Draw(im);font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',34)
 for i,p in enumerate([old,B/'world_maps/01_world_ocean_centered_preview.jpg']):
  q=Image.open(p).resize((1800,900));y=85+i*1000;im.paste(q,(50,y));d.text((50,y-50),'R8 / BEFORE' if i==0 else 'R9 / REVISED OCEANS AND SOUTH-SWEPT CONNECTION',font=font,fill='#eadfcb')
 im.save(B/'guide/Revision_Comparison.jpg',quality=94)
r=json.load(open(B/'source/Ocean_Revision_R9.json'))
lines=['# Catworld R9 - Ocean geography and tectonic framework','Prepared 1 November 2026. The latest green correction takes precedence over the earlier concavity wording.',
'## Connections and primary maps','The main-eastern bridge now descends southward into the eastern western flank. The east block rotates an additional 13 degrees. Height, colour and terrain masks move together. Arctic deformation fades smoothly to zero rather than leaving a cut at a latitude boundary. Panterra hydrology and the southern mainland remain in their established positions.',
'Two clean 8192 x 4096 equirectangular maps are primary exports. The ocean-centered sheet has the zero meridian at its edges, matching the redline. The Panterra-centered sheet has zero longitude in its middle. The same two framings are used for tectonic and numbered maps. Both clean maps are exact rolls of the globe texture; they cannot disagree about geography.',
'## Curved migration shelf','Five detached islands follow a curved route from the Panterran peninsula. The departure is steep and bends gradually westward toward the old homeland. Two larger continental fragments lie near the southern mainland; a middle arc island and two small remnants taper toward Panterra. A shallow submerged ribbon connects the groups at the proposed -65 m lowstand. This is a deliberate narrative constraint, not proof that such a shelf naturally follows an oceanic arc. Active subduction lies outside the shelf, while the exposed fragments are interpreted as inherited crust.',
'## Isolated ocean geography','Pelagic Crown is a working name for the bigger-Hawaii request: a large composite volcanic island with a wetter windward side and rocky high interior. Only two progressively smaller companions appear along its proposed older trail. The intervening ocean is deep, and this trail is separate from the migration shelf. Three small glacial continental fragments sit south of the northern remnant/Greenland-like polar land. Other ocean islands occur in widely spaced pairs, isolated shields or small atolls, rather than a uniformly random scatter. Atolls are intentionally enlarged enough to read at map scale.',
'## Reading the tectonic sheets','Five working plate domains are named. A collision boundary follows the great northern mountains and the displaced connecting belt. A subduction boundary follows the outer side of the southern arc; teeth mark the proposed overriding side. Spreading ridges lie in the large oceans and near the south polar plate. Transform links close the conceptual network. Arrows show proposed relative directions, not measured speeds. The whole network is a story framework, not a balanced reconstruction using Euler poles. Ridge and transform locations remain especially provisional.',
'Continental shelves are shallow margins of continents; they are not automatically places where plates meet. A mountain suture, a volcanic subduction arc, a rifted continental ribbon and a hotspot track therefore receive different symbols. The sparse hotspot trail must not be read as a land bridge.',
'## Authored island catalogue','Five entries replace the previous shelf islands; seventeen add new ocean or northern islands. The existing northern remnant and other established islands are retained.','| Working feature | Longitude | Latitude | Origin | Peak m |','|---|---:|---:|---|---:|']
for f in r['islands']:lines.append(f"| {f['name']} | {f['lon']:.1f} | {f['lat']:.1f} | {f['kind']} | {f['peak_m']:.0f} |")
lines+=['## Sources and limits','USGS, Understanding plate motions: https://pubs.usgs.gov/gip/dynamic/understanding.html . USGS, What is a hotspot: https://www.usgs.gov/faqs/what-a-hotspot-and-how-do-you-know-its-there . These support the geological mechanisms, not the fictional plate geometry.',
'The globe retains 10x relief exaggeration and enlarged rivers. Physical terrain is 4K; the 8K colour map improves coastline and river presentation but does not add physical elevation samples. Rectangular maps stretch high latitudes. Local dam and waterfall models are unchanged from R8. The full guide carries forward the 4000-year seasons, working 35-degree tilt, plateau-reservoir hydrology, rain shadows and unresolved heat-source constraints.']
(B/'guide/Ocean_and_Tectonics_R9.md').write_text('\n\n'.join(lines)+'\n')
print('R9 FIGURES AND NOTES COMPLETE')
# The latest correction is easiest to judge at the same map scale, side by side.
if old.exists():
 board=Image.new('RGB',(2060,900),'#10191f');draw=ImageDraw.Draw(board);ft=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial Bold.ttf',30)
 for i,p in enumerate([old,B/'world_maps/01_world_ocean_centered_preview.jpg']):
  q=Image.open(p);w,h=q.size;q=q.crop((0,int(h*30/180),int(w*145/360),int(h*145/180)));q=q.resize((990,785),Image.Resampling.LANCZOS);x=25+i*1030;board.paste(q,(x,85));draw.text((x,25),'BEFORE / R8' if i==0 else 'AFTER / R9 - SOUTHWARD CONNECTION',font=ft,fill='#eadfcb')
 board.save(B/'guide/Bridge_Correction_R9.jpg',quality=94)
