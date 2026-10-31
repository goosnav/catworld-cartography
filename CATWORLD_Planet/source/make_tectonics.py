from PIL import Image,ImageDraw,ImageFont
import math
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
def line(coords,col,width=5):
 for sh in [-360,0,360]:td.line([pt(lo+sh,la) for lo,la in coords],fill=col,width=width,joint='curve')
def arrow(a,b,col):
 for sh in [-360,0,360]:
  aa=pt(a[0]+sh,a[1]);bb=pt(b[0]+sh,b[1]);td.line([aa,bb],fill=col,width=5);ang=math.atan2(bb[1]-aa[1],bb[0]-aa[0]);td.polygon([bb,(bb[0]-19*math.cos(ang-.45),bb[1]-19*math.sin(ang-.45)),(bb[0]-19*math.cos(ang+.45),bb[1]-19*math.sin(ang+.45))],fill=col)
orange='#f2b270';blue='#74a0df';cyan='#6de7dd'
line([(-63,28),(-40,32),(-15,37),(15,36),(45,37),(75,39),(100,33),(130,29),(145,27),(158,22),(171,16),(181,9),(190,1),(199,-8),(210,-18),(222,-29),(235,-39)],orange,8)
for lo,la in [(-35,33),(20,36),(82,37),(155,23),(199,-8)]:
 arrow((lo,la+13),(lo,la+4),orange);arrow((lo,la-13),(lo,la-4),orange)
line([(174,9),(170,-3),(165,-16),(154,-23)],orange,5)
line([(122,19),(123,12),(130,2),(138,-9)],blue,6)
line([(163,3),(164,-6),(168,-12)],blue,6)
line([(-126,-22),(-116,-26),(-105,-30)],blue,6)
line([(-118,-39),(-103,-33),(-86,-26),(-70,-21),(-57,-12),(-44,4)],'#cbbb99',5)
# Maritime exposure and descent into the dry basin, not generic latitude stripes.
arrow((174,42),(172,23),cyan);arrow((178,17),(156,4),cyan)
arrow((-103,-8),(-132,-23),cyan);arrow((-48,19),(-36,19),cyan)
def label(txt,loc,size=22,col='#f3e8cf'):
 x,y=pt(*loc);bb=td.textbbox((0,0),txt,font=f(size,1));w=bb[2];x=max(8,min(x,2190-w));td.rounded_rectangle((x-6,y-5,x+w+6,y+size+7),radius=4,fill='#10191f');td.text((x,y),txt,font=f(size,1),fill=col)
for txt,loc in [('1 / PANTERRA',(-30,-1)),('2 / DRY INTERIOR',(119,-15)),('3 / MARITIME CORE',(-168,-28)),('DROWNED SHELF',(-94,-45)),('ARCTIC OCEAN',(-65,83)),('POLAR LAND',(40,-78)),('OLD IMPACT',(-16,58))]:label(txt,loc)
label('MOISTURE',(137,49),19,cyan);label('MOISTURE',(-115,0),19,cyan)
im.paste(tex,(100,180));d=ImageDraw.Draw(im)
heads=['1 / OLD CRUST + IMPACT','2 / TWO OCEANS CLOSE','3 / RIFTING, WATER + ICE']
columns=[['Three older continental cores survive.','The northern impact scars one craton.','Its red apron merges into the mainland;','the crater is older than the collision.'],['Panterra docks with eastern terranes.','A later, oblique collision adds the third','core. Broad sutures continue across the','map seam and onto the southern spine.'],['Rifts explain gulfs and angular capes.','A drowned shelf preserves an island','bridge. Ice cuts the polar coasts; winds','place the dry basin behind the wall.']]
for x,head,lines in zip([100,860,1610],heads,columns):
 d.text((x,1320),head,font=f(28,1),fill=orange)
 for j,txt in enumerate(lines):d.text((x,1380+j*40),txt,font=f(26),fill='#c4d1d6')
d.text((100,1625),'ORANGE: collision     BLUE: rifts     PALE: former shelf bridge     CYAN: proposed moisture routes',font=f(25),fill='#c4d1d6')
d.text((100,1690),'Terrain analogue: Mapzen Terrain Tiles / AWS; USGS SRTM & GMTED. Warped into fictional topography.',font=f(22),fill='#8fa7b1')
im.save(B/'guide/Tectonic_Framework.png')
