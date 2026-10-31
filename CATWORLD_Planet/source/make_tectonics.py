from PIL import Image,ImageDraw,ImageFont
import math,json,numpy as np
from pathlib import Path
B=Path(__file__).resolve().parents[1];fnt='/System/Library/Fonts/Supplemental/Arial.ttf';bold='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def f(s,b=False):return ImageFont.truetype(bold if b else fnt,s)
im=Image.new('RGB',(2400,1800),'#10191f');d=ImageDraw.Draw(im)
d.text((65,45),'CATWORLD / A PROPOSED TECTONIC HISTORY',font=f(46,1),fill='#f3e8cf')
d.text((65,110),'Geographic explanation, not a plate-motion simulation. Boundaries are schematic.',font=f(26),fill='#a5bbc5')
tex=Image.open(B/'textures/albedo_4096.png').resize((2200,1100));im.paste(tex,(100,180));d=ImageDraw.Draw(im)
def pt(lon,lat):return (100+(lon+180)/360*2200,180+(90-lat)/180*1100)
for lon in range(-180,181,30):d.line([pt(lon,-85),pt(lon,85)],fill='#28404a',width=1)
for lat in range(-60,61,30):d.line([pt(-180,lat),pt(180,lat)],fill='#28404a',width=1)
def line(coords,col,width=5):d.line([pt(*p) for p in coords],fill=col,width=width,joint='curve')
def arrow(a,b,col):
 a=pt(*a);b=pt(*b);d.line([a,b],fill=col,width=5);ang=math.atan2(b[1]-a[1],b[0]-a[0]);q=[b,(b[0]-20*math.cos(ang-.45),b[1]-20*math.sin(ang-.45)),(b[0]-20*math.cos(ang+.45),b[1]-20*math.sin(ang+.45))];d.polygon(q,fill=col)
line([(-63,28),(-40,32),(-15,37),(15,36),(45,37),(75,39),(100,33),(130,25),(160,10)],'#f2b270',7)
for lo,la in [(-35,33),(10,36),(62,38),(115,29)]:arrow((lo,la+14),(lo,la+4),'#f2b270');arrow((lo,la-14),(lo,la-4),'#f2b270')
line([(-119,-15),(-116,-26),(-118,-36),(-128,-47)],'#f2b270',6)
arrow((-103,-31),(-113,-31),'#f2b270');arrow((-139,-33),(-124,-33),'#f2b270')
line([(122,19),(123,12),(130,2),(138,-9)],'#74c5df',6)
arrow((124,7),(114,6),'#74c5df');arrow((130,7),(140,8),'#74c5df')
line([(-126,-22),(-116,-26),(-105,-30)],'#74c5df',6)
line([(-56,-13),(-67,-22),(-85,-29),(-106,-32)],'#cbbb99',3)
for text,loc in [('NORTHERN CRATON',(5,54)),('PANTERRAN PLATE',(-25,-1)),('EASTERN TERRANES',(135,-20)),('SOUTHERN SHIELD',(-147,-22)),('BROKEN SHELF',(-76,-36))]:
 x,y=pt(*loc);box=d.textbbox((0,0),text,font=f(22,1));d.rounded_rectangle((x-8,y-6,x+box[2]+8,y+28),radius=4,fill='#10191f');d.text((x,y),text,font=f(22,1),fill='#f3e8cf')
d.text((100,1320),'1 / IMPACT',font=f(29,1),fill='#da8870');d.text((860,1320),'2 / COLLISION',font=f(29,1),fill='#f2b270');d.text((1610,1320),'3 / RIFTING + EROSION',font=f(29,1),fill='#74c5df')
columns=[['An ancient strike damages an older','northern craton. Later erosion exposes','iron-rich rocks; a breached rim floods.','The crater is not the mountain suture.'],['Convergence closes an older ocean.','Crust thickens into a broad mountain','belt linking Panterra and the eastern','lands, with parallel thrusts and passes.'],['Younger extension opens the eastern','gulf and southern shelf basin. Faults','guide angular coasts; rivers and ice','cut the smaller bays and fjords.']]
for xx,ls in zip([100,860,1610],columns):
 for j,txt in enumerate(ls):d.text((xx,1380+j*40),txt,font=f(27),fill='#c4d1d6')
d.text((100,1625),'ORANGE = convergence / mountain belts     BLUE = extension / rift gulfs     PALE = drowned shelf connection',font=f(25),fill='#c4d1d6')
d.text((100,1690),'Terrain analogue: Mapzen Terrain Tiles / AWS; USGS SRTM & GMTED. Warped and rescaled for a fictional planet.',font=f(22),fill='#8fa7b1')
im.save(B/'guide/Tectonic_Framework.png')
