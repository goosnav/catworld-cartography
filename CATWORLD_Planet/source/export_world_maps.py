"""Primary rectangular exports and matching conceptual tectonic sheets."""
from pathlib import Path
import json,math
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from scipy.ndimage import gaussian_filter,zoom
from revise_r9 import CHAIN,east_forward
from revise_r6 import east_transform
B=Path(__file__).resolve().parents[1];O=B/'world_maps';O.mkdir(exist_ok=True)
FONT='/System/Library/Fonts/Supplemental/Arial'
def font(n,b=False):return ImageFont.truetype(FONT+(' Bold' if b else '')+'.ttf',n)
c=np.asarray(Image.open(B/'textures/albedo_8192.png'));H,W=c.shape[:2]
# Clean exports are the exact globe surface in equirectangular coordinates.
for center,name in [(180,'01_world_ocean_centered'),(0,'02_world_panterra_centered')]:
 a=np.roll(c,round(-center/360*W),axis=1);Image.fromarray(a).save(O/(name+'.png'))
 Image.fromarray(a).resize((2200,1100),Image.Resampling.LANCZOS).save(O/(name+'_preview.jpg'),quality=94)
# Shared boundaries: endpoint coordinates are deliberately reused at junctions.
R=(315,37);J=(160,-30);T=(200,78);A=(302,-18);K=(285,-65);S=(200,-65)
sp=[(-45,37),(-20,37),(0,37),(30,37),(52,37),(72,35),(95,30),(122,27),(145,23)]
collision=[]
for x,y in sp:
 if x>54.58:x,y=east_transform(x,y)
 if x>24:x,y=east_forward(x,y)
 collision.append((float(x)%360,float(y)))
collision[0]=R;collision.append(J)
boundaries=[('collision',collision),('ridge',[J,(184,-7),(188,18),(178,37),(195,58),T]),('transform',[T,(241,72),(278,57),R]),('subduction',[R,(304,24),(306,12),(315,0),(309,-10),A]),('subduction',[A,(295,-31),(285,-42),(281,-54),K]),('transform',[J,(207,-22),(246,-19),(275,-14),A]),('ridge',[J,(182,-48),S]),('ridge',[(0,-65),(60,-65),(120,-65),(160,-65),S,(240,-65),K,(330,-65),(359.9,-65)])]
colors={'collision':'#ffb86b','subduction':'#f57970','ridge':'#69d5e0','transform':'#dbabf1'}
for center,name in [(180,'03_tectonics_ocean_centered'),(0,'04_tectonics_panterra_centered')]:
 mw,mh=4096,2048;off=140
 base=Image.fromarray(np.roll(c,round(-center/360*W),axis=1)).resize((mw,mh),Image.Resampling.LANCZOS)
 base=Image.blend(base,Image.new('RGB',base.size,'#0d2029'),.30)
 out=Image.new('RGB',(mw,mh+380),'#10191f');out.paste(base,(0,off));d=ImageDraw.Draw(out)
 def pt(p):return (((p[0]-center+180)%360)/360*mw,(90-p[1])/180*mh+off)
 def segments(points):
  from scipy.interpolate import PchipInterpolator
  p=np.array(points,dtype=float);p[:,0]=np.degrees(np.unwrap(np.radians(p[:,0])))
  t=np.r_[0,np.cumsum(np.hypot(np.diff(p[:,0]),np.diff(p[:,1])))];tt=np.linspace(0,t[-1],max(20,int(t[-1]*3)))
  xx=PchipInterpolator(t,p[:,0])(tt);yy=PchipInterpolator(t,p[:,1])(tt)
  for i in range(len(tt)-1):
   a=pt((xx[i],yy[i]));b=pt((xx[i+1],yy[i+1]))
   if abs(a[0]-b[0])<mw/2:yield a,b
 def line(points,col,width=5,dashed=False):
  for i,(a,b) in enumerate(segments(points)):
   if not dashed or i%10<6:d.line([a,b],fill=col,width=width)
 def label(loc,title,small=None):
  x,y=pt(loc);ft=font(29,True);tw=d.textlength(title,font=ft);x=max(15,min(x,mw-tw-22))
  d.rounded_rectangle((x-10,y-6,x+tw+12,y+41+(26 if small else 0)),5,fill='#10191f');d.text((x,y),title,font=ft,fill='#f1eadb')
  if small:d.text((x,y+37),small,font=font(20),fill='#aec2c9')
 d.text((48,32),'CATWORLD / PROPOSED PLATE TECTONICS',font=font(45,True),fill='#f1eadb')
 d.text((48,90),f'Equirectangular | central meridian {center} degrees | R9 | plate boundaries are design hypotheses',font=font(25),fill='#aec2c9')
 for la in [-60,-30,0,30,60]:
  y=pt((0,la))[1];d.line((0,y,mw,y),fill='#344750',width=1)
 for kind,points in boundaries:
  line(points,colors[kind],7 if kind=='collision' else 5,kind=='transform')
  if kind=='subduction':
   for i,(a,b) in enumerate(segments(points)):
    if i%16:continue
    dx,dy=b[0]-a[0],b[1]-a[1];L=max(1,math.hypot(dx,dy));vx,vy=dx/L,dy/L
    d.polygon([(a[0]-7*vx,a[1]-7*vy),(a[0]+7*vx,a[1]+7*vy),(a[0]-17*vy,a[1]+17*vx)],fill=colors[kind])
 # Shelf is separate from the active trench, on its continental side.
 line(CHAIN,'#d9d2a0',4,True)
 # Hotspot age trail has only two exposed companions; dashed line is not land.
 line([(210,-3.8),(217.5,3.4),(228,9.1),(237,14)],'#ead47c',3,True)
 x,y=pt((210,-3.8));d.ellipse((x-17,y-17,x+17,y+17),outline='#ffe68c',width=4)
 # Plate motion arrows show relative direction only, with no invented velocity.
 for loc,dx,dy in [((230,25),-45,40),((255,-45),45,-35),((18,4),-20,-45),((85,60),15,45),((160,-77),45,0)]:
  x,y=pt(loc);d.line((x,y,x+dx,y+dy),fill='white',width=4);a=math.atan2(dy,dx)
  d.line([(x+dx-16*math.cos(a-.5),y+dy-16*math.sin(a-.5)),(x+dx,y+dy),(x+dx-16*math.cos(a+.5),y+dy-16*math.sin(a+.5))],fill='white',width=4)
 for loc,title,small in [((48,58),'BOREAL PLATE','northern craton + eastern upper plate'),((345,-35),'PANTERRAN PLATE','collision underthrust margin'),((215,33),'PELAGIC PLATE','oceanic lithosphere'),((242,-48),'SOUTHERN SHIELD PLATE','old continental interior'),((75,-80),'SOUTH POLAR PLATE',None),((210,-9),'PELAGIC CROWN','hotspot; two sparse companions'),((185,43),'NORTHERN FORE-ISLANDS','glacial continental fragments'),((281,-38),'DROWNED SHELF','migration proposal'),((87,4),'EASTERN CORE','inclined farther south')]:label(loc,title,small)
 y=mh+off+35
 for i,(kind,txt) in enumerate([('collision','Continental collision'),('subduction','Subduction / teeth on upper plate'),('ridge','Spreading ridge'),('transform','Transform boundary')]):
  x=45+i*1010;d.line((x,y+12,x+62,y+12),fill=colors[kind],width=7);d.text((x+80,y-5),txt,font=font(27),fill='#f1eadb')
 d.text((45,y+57),'PALE DASH: drowned continental shelf   |   GOLD DASH: hotspot age trail   |   WHITE ARROWS: proposed relative motion',font=font(27),fill='#c7d1d2')
 d.text((45,y+108),'Shelf edges are not automatically plate boundaries. Collision, subduction, rifting and hotspots have different signatures.',font=font(27),fill='#c7d1d2')
 d.text((45,y+153),'This is a geological story framework, not a solved plate reconstruction or numerical geodynamics simulation.',font=font(25),fill='#9fb2ba')
 out.save(O/(name+'.png'));out.resize((2200,round(out.height*2200/out.width))).save(O/(name+'_preview.jpg'),quality=94)
# Numbered world sheets use the same framing as the two primary maps.
features=json.load(open(B/'source/features.json'))
for center,stem in [(180,'05_world_ocean_annotated'),(0,'06_world_panterra_annotated')]:
 im=Image.fromarray(np.roll(c,round(-center/360*W),axis=1)).resize((4096,2048));d=ImageDraw.Draw(im)
 for f in features:
  x=((f['lon']-center+180)%360)/360*4096;y=(90-f['lat'])/180*2048
  d.ellipse((x-15,y-15,x+15,y+15),fill='#c45f43',outline='#fff0d8',width=2);d.text((x,y),f['id'],anchor='mm',font=font(18,True),fill='white')
 im.save(O/(stem+'.png'))
json.dump(dict(projection='equirectangular',clean_dimensions=[8192,4096],centers_deg=[180,0],tectonics_dimensions=[4096,2428],boundaries=boundaries,notes='Same globe colour and physical terrain; rectangular maps stretch polar land. Use globe views for local drawing proportions.'),open(O/'Projection_and_Tectonics.json','w'),indent=2)
print('PRIMARY WORLD MAPS COMPLETE')
