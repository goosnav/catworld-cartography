"""Show the two creator-requested changes against the immediately preceding revision."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[1]
font=lambda n,b=False:ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if b else '')+'.ttf',n)
out=Image.new('RGB',(2400,2650),'#10191f');d=ImageDraw.Draw(out)
d.text((65,38),'CATWORLD / NATURAL LANDFORMS PASS',font=font(48,True),fill='#f3e9d7')
d.text((65,105),'R7 BEFORE',font=font(30,True),fill='#b4c5c9');d.text((1265,105),'R8 REVISED',font=font(30,True),fill='#91d4bf')
for row,name in enumerate(['07_panterra_close','06_south_pole']):
 for col in range(2):
  p=B/'source'/('reference_R7_'+name+'.jpg') if col==0 else B/'renders'/(name+'.png')
  im=Image.open(p).convert('RGBA');im.thumbnail((1130,1130),Image.Resampling.LANCZOS)
  x=35+1200*col;y=170+1230*row;out.paste(im,(x,y),im)
 title='Dissected relief / slimmer rivers / lake and vegetation variation' if row==0 else 'Spherical polar relief / exposed coastal rock / no meridian pinching'
 d.text((65,1320+1230*row),title,font=font(28),fill='#b4c5c9')
out.save(B/'guide/Revision_Comparison.jpg',quality=94)
