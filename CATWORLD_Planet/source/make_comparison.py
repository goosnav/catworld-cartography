"""Rebuild the R2/R4 review sheet using bundled R2 thumbnails."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import sys
B=Path(__file__).resolve().parents[1]
def font(size,bold=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if bold else '')+'.ttf',size)
im=Image.new('RGB',(1920,2210),'#10191f');d=ImageDraw.Draw(im)
d.text((60,35),'CATWORLD / SHORTER BRIDGE, REBUILT FAR-SIDE CONTINENT',font=font(39,True),fill='#f2ead8')
for row,name in enumerate(['02_eastern','04_far_side']):
 y=110+row*1010
 for col in range(2):
  x=60+col*960;d.text((x,y),('PREVIOUS / R2' if col==0 else 'REVISED / R4')+' — '+('EASTERN VIEW' if row==0 else 'FAR SIDE'),font=font(27,True),fill='#a6bec8' if col==0 else '#8be0d4')
  p=B/'source'/f'reference_R2_{name}.jpg' if col==0 else B/('review_draft' if '--draft' in sys.argv else 'renders')/(name+'.png')
  pic=Image.open(p).convert('RGBA').resize((900,900),Image.Resampling.LANCZOS);im.paste(pic,(x+(900-pic.width)//2,y+50+(900-pic.height)//2),pic)
d.text((60,2155),'Bridge segment: 60° → 25° longitude · Same viewing angles and scale · Three connected continental cores',font=font(25),fill='#c5d4da')
im.save(B/'guide/Revision_Comparison.jpg',quality=94)
