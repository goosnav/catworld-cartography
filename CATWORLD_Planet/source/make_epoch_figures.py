"""R5: seasonal epoch, lowstand geometry, tectonic framework and visual comparison."""
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from revise_southern import SPINE,CHAIN
B=Path(__file__).resolve().parents[1];G=B/'guide';BG='#10191f';INK='#efe7d6';MUTED='#abc2ca';TEAL='#7cdccc';GOLD='#e3b479'
def font(n,b=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if b else '')+'.ttf',n)
def text(d,p,s,n=30,col=INK,b=False):d.text(p,s,font=font(n,b),fill=col)
def base(title,sub,h=1500):
 im=Image.new('RGB',(2200,h),BG);d=ImageDraw.Draw(im);text(d,(70,45),title,44,b=True);text(d,(70,112),sub,27,MUTED);return im,d
tex=np.asarray(Image.open(B/'textures/albedo_4096.png'));h,w=tex.shape[:2];tex=np.roll(tex,w//2,axis=1)
def world_map():return Image.fromarray(tex).resize((2060,1030),Image.Resampling.LANCZOS)
def pt(lo,la):return (lo%360/360*2060,(90-la)/180*1030)
def lab(d,loc,txt,col=INK):
 x,y=pt(*loc);ft=font(25,True);bw=d.textlength(txt,font=ft);x=max(8,min(x,2050-bw));d.rounded_rectangle((x-6,y-6,x+bw+7,y+36),4,fill=BG);text(d,(x,y),txt,25,col,True)
im,d=base('CURRENT EPOCH / NORTH AUTUMN, SOUTH SPRING','Proposed Ls 255 degrees: 833 years after equinox; 167 years until northern winter solstice.')
m=world_map();q=ImageDraw.Draw(m)
for la in [60,30,0,-30,-60]:q.line([(0,pt(0,la)[1]),(2060,pt(0,la)[1])],fill='#657784',width=1)
for loc,txt in [((8,66),'BLOOD LAKE / FREEZE BEGINS'),((72,47),'SNOWY NORTHERN RANGES'),((20,4),'MILD LOWLANDS'),((184,-30),'SOUTHERN SPRING'),((233,-10),'WARMING ISLAND SEAS'),((70,-78),'RELIC GROUNDED ICE'),((208,57),'SMALL NORTHERN REMNANT')]:lab(q,loc,txt)
im.paste(m,(70,185));text(d,(70,1250),'North: shorter days, growing snow and sea ice; birds move toward lower-latitude refuges.',31)
text(d,(70,1300),'South: warming coasts, residual alpine glaciers; dry interior remains dry despite spring.',31)
text(d,(70,1370),'Ice extent and biome colours are design hypotheses. Reference lighting is not the actual polar-day/night pattern.',26,MUTED)
im.save(G/'Seasonal_Epoch.png')
z=np.load(B/'source/terrain_fields.npz');land=np.roll(z['land'],w//2,axis=1);height=np.roll(z['height'],w//2,axis=1)
x0,x1=int(165/360*w),int(320/360*w);y0,y1=int((90-24)/180*h),int((90+63)/180*h)
im,d=base('THE CAT CROSSING / SAME SHELF, TWO SEA LEVELS','An illustrative historical scenario. Gold shows shelf exposed at 65 m below the present ocean.',1550)
for j,low in enumerate([False,True]):
 pic=tex.copy();exposed=(height>=-65)&~land
 if low:pic[exposed]=[190,153,98]
 pic=Image.fromarray(pic[y0:y1,x0:x1]).resize((2060,530),Image.Resampling.LANCZOS);q=ImageDraw.Draw(pic)
 def cp(lo,la):return ((lo-165)/155*2060,(24-la)/87*530)
 for a,b in zip(CHAIN[:-1],CHAIN[1:]):
  aa,bb=cp(*a),cp(*b)
  for t in np.arange(0,1,.14):
   p=(aa[0]+(bb[0]-aa[0])*t,aa[1]+(bb[1]-aa[1])*t);p2=(aa[0]+(bb[0]-aa[0])*min(1,t+.07),aa[1]+(bb[1]-aa[1])*min(1,t+.07));q.line([p,p2],fill='#e99870',width=3)
 yy=210+j*625;im.paste(pic,(70,yy));text(d,(70,yy-43),'THEN / SOUTHERN WINTER - PROPOSED LOWSTAND' if low else 'NOW / SOUTHERN SPRING - ISLANDS AND STRAITS',29,TEAL,True)
text(d,(70,1460),'Geometry checked: connected at -65 m, separate today. Ice volumes, sea-level history and crossing date are not simulated.',26,MUTED)
im.save(G/'Migration_Lowstand.png')
im,d=base('TECTONICS / TWO JOINED CORES, ONE DETACHED CONTINENT','Proposed geological history. The southern escarpment is not an extension of the northern collision.')
m=world_map();q=ImageDraw.Draw(m)
def line(points,col,width=6):
 for a,b in zip(points[:-1],points[1:]):
  aa,bb=pt(*a),pt(*b)
  if abs(aa[0]-bb[0])<1000:q.line([aa,bb],fill=col,width=width)
line([(-50,31),(-20,36),(10,37),(35,37),(52,37),(72,35),(95,30),(122,27),(145,23)],GOLD,8)
line(SPINE,'#a7a4dd',7);line(CHAIN,'#dfb7a3',5)
line([(230,-16),(242,-23),(254,-23),(268,-17),(285,-7)],'#6e9fd2',6)
for loc,txt in [((5,24),'PANTERRA'),((97,8),'EASTERN DRY CORE'),((163,2),'DEEP SEPARATING OCEAN'),((183,-30),'OLD SOUTHERN SHIELD'),((235,-4),'RIFTED SHELF'),((286,20),'TOWARD PANTERRA')]:lab(q,loc,txt)
im.paste(m,(70,185));text(d,(70,1250),'GOLD: main collision belt    VIOLET: old raised eastern margin    BLUE: extension    PALE: continental shelf ribbon',26,MUTED)
text(d,(70,1310),'Collision thickens the main mountain bridge. Southern rifting makes islands and angular bays.',31)
text(d,(70,1360),'Low sea level can expose the shelf; it cannot expose the deep ocean separating the eastern and southern continents.',27)
im.save(G/'Tectonic_Framework.png')
# Before/after uses the previous far-side angle and the new 12-degree southern framing.
im,d=base('FAR SIDE / REBUILT AS A SEPARATE SOUTHERN WORLD','Previous northern extension -> independent southern mainland and eastern archipelago.',1300)
for j,p in enumerate([B/'source/reference_R4_far_side.jpg',B/'renders/04_far_side.png']):
 pic=Image.open(p).convert('RGBA');pic.thumbnail((1000,1000),Image.Resampling.LANCZOS);im.paste(pic,(70+j*1070,220),pic)
 text(d,(70+j*1070,170),'PREVIOUS / R4' if j==0 else 'REVISED / R5',32,MUTED if j==0 else TEAL,True)
text(d,(70,1240),'R4 centre: 180 lon / 0 lat. R5 centre: 180 lon / 12 south. Same globe scale; southern framing adjusted.',26,MUTED)
im.save(G/'Revision_Comparison.jpg',quality=94)
print('R5 EPOCH FIGURES COMPLETE')
# Geometric daylight at the proposed epoch, without refraction or terrain horizons.
import math,json,csv
dec=math.asin(math.sin(math.radians(23.4))*math.sin(math.radians(255)));rows=[]
for f in json.load(open(B/'source/features.json')):
 if f['id'] in ['01','02','03','04','11','21','23','28','29']:
  q=-math.tan(math.radians(f['lat']))*math.tan(dec);hours=24 if q<=-1 else 0 if q>=1 else 24/math.pi*math.acos(q)
  rows.append(dict(id=f['id'],region=f['name'],latitude_deg=round(f['lat'],3),daylight_hours=round(hours,2),solar_declination_deg=round(math.degrees(dec),3)))
with open(G/'Seasonal_Reference.csv','w') as out:
 writer=csv.DictWriter(out,fieldnames=rows[0]);writer.writeheader();writer.writerows(rows)
