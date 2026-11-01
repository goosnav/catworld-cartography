from PIL import Image,ImageDraw,ImageFont
import math
import numpy as np
from reshape_geography import forward,forward_a,SPINE,CHAIN
from pathlib import Path
B=Path(__file__).resolve().parents[1]
def f(s,b=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if b else '')+'.ttf',s)
im=Image.new('RGB',(2400,1800),'#10191f');d=ImageDraw.Draw(im)
d.text((65,45),'CATWORLD / THREE CORES, ONE COLLISION SYSTEM',font=f(44,1),fill='#f3e8cf')
d.text((65,110),'Proposed history and moisture routes. Schematic boundaries; no plate or climate simulation.',font=f(25),fill='#a5bbc5')
tex=Image.open(B/'textures/albedo_4096.png').convert('RGB').resize((2200,1100));td=ImageDraw.Draw(tex)
def pt(lon,lat):return ((lon+180)/360*2200,(90-lat)/180*1100)
for lon in range(-180,181,30):td.line([pt(lon,-90),pt(lon,90)],fill='#28404a',width=1)
for lat in range(-60,61,30):td.line([pt(-180,lat),pt(180,lat)],fill='#28404a',width=1)
def map_pt(lo,la):return (forward if lo>=180 or lo<=-100 else forward_a)(lo,la)
def line(coords,col,width=5,transform=True):
 if transform:coords=[map_pt(lo,la) for lo,la in coords]
 for sh in [-360,0,360]:td.line([pt(lo+sh,la) for lo,la in coords],fill=col,width=width,joint='curve')
def arrow(a,b,col,transform=True):
 if transform:a=map_pt(*a);b=map_pt(*b)
 for sh in [-360,0,360]:
  aa=pt(a[0]+sh,a[1]);bb=pt(b[0]+sh,b[1]);td.line([aa,bb],fill=col,width=5);ang=math.atan2(bb[1]-aa[1],bb[0]-aa[0]);td.polygon([bb,(bb[0]-19*math.cos(ang-.45),bb[1]-19*math.sin(ang-.45)),(bb[0]-19*math.cos(ang+.45),bb[1]-19*math.sin(ang+.45))],fill=col)
orange='#f2b270';blue='#74a0df';cyan='#6de7dd'
line([(-63,28),(-40,32),(-15,37),(15,36),(45,37),(75,39),(100,33),(130,29),(145,27),(158,22),(171,16)],orange,8)
line(SPINE,orange,8,False)
for lo,la in [(-35,33),(20,36),(82,37),(155,23)]:
 arrow((lo,la+13),(lo,la+4),orange);arrow((lo,la-13),(lo,la-4),orange)
arrow((196,36),(196,27),orange,False);arrow((196,10),(196,19),orange,False)
line([(122,19),(123,12),(130,2),(138,-9)],blue,6)
line([(235,45),(228,39),(224,34),(233,30)],blue,6,False)
line([(-123,16),(-113,-3),(-103,-16)],blue,6,False)
line(CHAIN,'#cbbb99',5,False)
# Maritime exposure and descent into the dry basin, not generic latitude stripes.
arrow((142,42),(137,29),cyan,False);arrow((134,25),(117,14),cyan,False)
arrow((177,44),(200,42),cyan,False);arrow((-48,19),(-36,19),cyan)
def label(txt,loc,size=22,col='#f3e8cf'):
 x,y=pt(*loc);bb=td.textbbox((0,0),txt,font=f(size,1));w=bb[2];x=max(8,min(x,2190-w));td.rounded_rectangle((x-6,y-5,x+w+6,y+size+7),radius=4,fill='#10191f');td.text((x,y),txt,font=f(size,1),fill=col)
for txt,loc in [('1 / PANTERRA',(-30,-1)),('2 / DRY INTERIOR',(105,-12)),('3 / MARITIME CORE',(-163,44)),('DROWNED SHELF',(-99,-37)),('ARCTIC OCEAN',(-65,83)),('POLAR LAND',(40,-78)),('OLD IMPACT',(-16,58))]:label(txt,loc)
label('MOISTURE',(125,49),19,cyan);label('MOISTURE',(-179,49),19,cyan)
im.paste(tex,(100,180));d=ImageDraw.Draw(im)
heads=['1 / OLD CRUST + IMPACT','2 / TWO OCEANS CLOSE','3 / RIFTING, WATER + ICE']
columns=[['Three older continental cores survive.','The northern impact scars one craton.','Its red apron merges into the mainland;','the crater is older than the collision.'],['Panterra docks with eastern terranes.','A compact oblique junction adds the third','core. Broad sutures continue across the','short neck onto the maritime spine.'],['Rifts explain gulfs and angular capes.','A drowned shelf preserves an island','bridge. Ice cuts the polar coasts; winds','place the dry basin behind the wall.']]
for x,head,lines in zip([100,860,1610],heads,columns):
 d.text((x,1320),head,font=f(28,1),fill=orange)
 for j,txt in enumerate(lines):d.text((x,1380+j*40),txt,font=f(26),fill='#c4d1d6')
d.text((100,1625),'ORANGE: collision     BLUE: rifts     PALE: former shelf bridge     CYAN: proposed moisture routes',font=f(25),fill='#c4d1d6')
d.text((100,1690),'Terrain analogue: Mapzen Terrain Tiles / AWS; USGS SRTM & GMTED. Warped into fictional topography.',font=f(22),fill='#8fa7b1')
im.save(B/'guide/Tectonic_Framework.png')
