"""Culture-specific vector tracing charts derived from Catworld R10 geography.
Run with numpy, scipy, contourpy, shapely, reportlab and pymupdf installed.
"""
from pathlib import Path
import math,json,heapq,hashlib
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter,distance_transform_edt,maximum_filter
from shapely.geometry import LineString
import contourpy
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pymupdf
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parents[1]
MODEL=Path('/Users/jbs/Documents/business/studio/catworld/CATWORLD_Planet')
Z=np.load(MODEL/'source/terrain_fields.npz');HY=json.load(open(MODEL/'source/hydrology_paths.json'));FE=json.load(open(MODEL/'source/features.json'))
for d in ['svg','png','individual','source']: (B/d).mkdir(exist_ok=True)
for name,fn in [('Book','Times New Roman.ttf'),('Italic','Times New Roman Italic.ttf'),('Bold','Times New Roman Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+fn))
W,H=792.,612. # All four sheets use US Letter landscape
RECT=(25,55,W-25,H-68)
CFG=[dict(key='birds',title='THE NORTHERN REACHES',culture='Birds',center=(0,48),angle=15,extent=None,seed=302),dict(key='cats',title='THE LANDS OF PANTERRA',culture='Cats',center=(12,12),angle=0,extent=None,seed=405),dict(key='reptiles',title='THE EASTERN REALMS',culture='Reptiles',center=(63,8),angle=18,extent=None,seed=806),dict(key='world',title='TERRA / THE WHOLE WORLD',culture='World',center=(0,0),angle=0,extent=(-2,2,-1,1),seed=912)]
def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
def inverse(x,y,lon0,lat0):
 rho=np.hypot(x,y);cc=2*np.arcsin(np.minimum(rho/2,.99999));p=np.radians(lat0);r=np.maximum(rho,1e-9)
 la=np.arcsin(np.cos(cc)*np.sin(p)+y*np.sin(cc)*np.cos(p)/r)
 lo=np.radians(lon0)+np.arctan2(x*np.sin(cc),r*np.cos(p)*np.cos(cc)-y*np.sin(p)*np.sin(cc))
 return (np.degrees(lo)+180)%360-180,np.degrees(la)
def forward(lo,la,lo0,la0):
 p=np.radians(la);p0=np.radians(la0);d=np.radians(np.asarray(lo)-lo0);k=np.sqrt(2/np.maximum(1+np.sin(p0)*np.sin(p)+np.cos(p0)*np.cos(p)*np.cos(d),1e-9))
 return k*np.cos(p)*np.sin(d),k*(np.cos(p0)*np.sin(p)-np.sin(p0)*np.cos(p)*np.cos(d))
def known(lo,la,k):
 if k=='world':return np.ones(np.broadcast(lo,la).shape,dtype=bool)
 if k=='birds':
  main=(lo>-67)&(lo<70)&(la>25+3*np.sin(np.radians(lo*3)))
  legend=(abs(lo)>70)&(abs(lo)<145)&(la>62)&(la<76+4*np.sin(np.radians(lo*4)))
  return main|legend
 if k=='cats':
  eastedge=86+5*np.sin(np.radians(la*5))
  return (lo>-65)&(lo<eastedge)&(la>-40)&(la<42-3*np.sin(np.radians(lo*3)))&((lo<35)|(la>-14))
 westedge=8+8*np.sin(np.radians(la*4))
 eastedge=115+5*np.sin(np.radians(la*4))
 return (lo>westedge)&(lo<eastedge)&(la>-46)&(la<43)

class Art:
 def __init__(self):self.items=[]
 def line(self,p,w=.48,dash=None,fill=False):
  if len(p)>1:self.items.append(dict(kind='path',p=[tuple(map(float,q)) for q in p],w=w,dash=dash,fill=fill))
 def ellipse(self,x,y,rx,ry,w=.45):self.line([(x+rx*math.cos(t),y+ry*math.sin(t)) for t in np.linspace(0,2*np.pi,25)],w)
 def text(self,x,y,t,size=11,font='Book',align='center',halo=False):self.items.append(dict(kind='text',x=float(x),y=float(y),t=t,size=size,font=font,align=align,halo=halo))
 def render(self,c):
  for e in self.items:
   c.setStrokeColorRGB(0,0,0);c.setFillColorRGB(0,0,0)
   if e['kind']=='text':
    c.setFont(e['font'],e['size']);tw=pdfmetrics.stringWidth(e['t'],e['font'],e['size']);x=e['x']-(tw/2 if e['align']=='center' else 0)
    if e['halo']:c.setFillColorRGB(1,1,1);c.rect(x-3,e['y']-2,tw+6,e['size']+3,fill=1,stroke=0);c.setFillColorRGB(0,0,0)
    c.drawString(x,e['y'],e['t']);continue
   c.setLineWidth(e['w']);c.setLineCap(1);c.setLineJoin(1);c.setDash(e['dash'] or [])
   p=c.beginPath();p.moveTo(*e['p'][0])
   for q in e['p'][1:]:p.lineTo(*q)
   if e['fill']:
    c.setFillColorRGB(1,1,1);c.drawPath(p,stroke=0,fill=1)
   c.drawPath(p,stroke=1,fill=0)
 def svg(self,path):
  import html
  out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W/72*25.4:.2f}mm" height="{H/72*25.4:.2f}mm" viewBox="0 0 {W} {H}"><title>Catworld tracing map</title><rect width="100%" height="100%" fill="white"/>']
  for e in self.items:
   if e['kind']=='text':
    out.append(f'<text x="{e["x"]:.2f}" y="{H-e["y"]:.2f}" font-family="Times New Roman,serif" font-size="{e["size"]}" text-anchor="{ "middle" if e["align"]=="center" else "start" }">{html.escape(e["t"])}</text>');continue
   pts=' '.join(f'{x:.2f},{H-y:.2f}' for x,y in e['p']);da=' stroke-dasharray="'+' '.join(map(str,e['dash']))+'"' if e['dash'] else ''
   if e['fill']:out.append(f'<polygon points="{pts}" fill="white" stroke="none"/>')
   out.append(f'<polyline points="{pts}" fill="none" stroke="black" stroke-width="{e["w"]}" stroke-linejoin="round" stroke-linecap="round"{da}/>')
  path.write_text('\n'.join(out+['</svg>']))

def chart(cfg):
 k=cfg['key'];rng=np.random.default_rng(cfg['seed']);a=Art();theta=np.radians(cfg.get('angle',0));ct,st=np.cos(theta),np.sin(theta)
 def coverage(lon,lat):
  m=known(lon,lat,k)
  if cfg.get('part')=='main':m&=(lon>42)
  if cfg.get('part')=='marches':m&=(lon<48)
  return m
 def project(lon,lat):
  if k=='world':return np.asarray(lon)/90,np.asarray(lat)/90
  u,v=forward(lon,lat,*cfg['center']);return ct*u-st*v,st*u+ct*v
 if cfg['extent'] is None:
  iy,ixx=np.mgrid[0:2048:8,0:4096:8];glon=(ixx+.5)*360/4096-180;glat=90-(iy+.5)*180/2048
  mask=Z['land'][::8,::8]&coverage(glon,glat)
  px,py=project(glon[mask],glat[mask]);xmin,xmax=px.min(),px.max();ymin,ymax=py.min(),py.max()
  pad=.035*max(xmax-xmin,ymax-ymin);cfg['extent']=tuple(map(float,(xmin-pad,xmax+pad,ymin-pad,ymax+pad)))
 xmin,xmax,ymin,ymax=cfg['extent']
 scale=min((RECT[2]-RECT[0])/(xmax-xmin),(RECT[3]-RECT[1])/(ymax-ymin));xoff=(RECT[0]+RECT[2]-(xmax+xmin)*scale)/2;yoff=(RECT[1]+RECT[3]-(ymax+ymin)*scale)/2
 nx,ny=1500,1150;xs=np.linspace(xmin,xmax,nx);ys=np.linspace(ymin,ymax,ny);xx,yy=np.meshgrid(xs,ys);lo,la=(xx*90,yy*90) if k=='world' else inverse(ct*xx+st*yy,-st*xx+ct*yy,*cfg['center']);coords=[np.clip((90-la)/180*2048-.5,0,2047),(lo+180)/360*4096-.5]
 land=map_coordinates(Z['land'],coords,order=0,mode='grid-wrap');elev=map_coordinates(Z['surface'],coords,order=1,mode='grid-wrap');wet=map_coordinates(Z['wet'],coords,order=1,mode='grid-wrap');lake=map_coordinates(Z['lake']|Z['small_lake'],coords,order=0,mode='grid-wrap');know=coverage(lo,la)
 # Unknown territory removes coastline as well as interior detail.
 detail=know.copy()
 if k=='birds':detail&=(abs(lo)<70)
 shore=distance_transform_edt(land&~lake);water=~land|lake
 def pos(lon,lat):x,y=project(lon,lat);return float(xoff+x*scale),float(yoff+y*scale)
 def ix(x,y):return int(np.clip(round(((y-yoff)/scale-ymin)/(ymax-ymin)*(ny-1)),0,ny-1)),int(np.clip(round(((x-xoff)/scale-xmin)/(xmax-xmin)*(nx-1)),0,nx-1))
 def allowed(p,margin=1):
  i,j=ix(*p);return bool(detail[i,j] and land[i,j] and not lake[i,j] and shore[i,j]>margin)
 def lines(field,width,mask=know,dash=None):
  co=contourpy.contour_generator(x=xs*scale+xoff,y=ys*scale+yoff,z=gaussian_filter(field.astype(float),.7),name='serial')
  for path in co.lines(.5):
   if len(path)<5:continue
   path=np.array(LineString(path).simplify(.32,preserve_topology=False).coords)
   keep=np.array([mask[ix(*p)] for p in path])
   # Include complete nearby islands when most of their shoreline is already known.
   if k not in ['birds','reptiles'] and np.linalg.norm(path[0]-path[-1])<1 and np.ptp(path[:,0])<65 and np.ptp(path[:,1])<65 and keep.mean()>.55:keep[:]=True
   start=None
   for ii,v in enumerate(np.r_[keep,False]):
    if v and start is None:start=ii
    if not v and start is not None:
     if ii-start>1:a.line(path[start:ii],width,dash)
     start=None
 def clipped_geo(points,width=.6,dash=None):
  pts=[]
  for lon,lat in points:
   x,y=pos(lon,lat)
   if RECT[0]<x<RECT[2] and RECT[1]<y<RECT[3] and coverage(lon,lat):pts.append((x,y))
   else:
    if len(pts)>1:a.line(pts,width,dash)
    pts=[]
  if len(pts)>1:a.line(pts,width,dash)
 # Real coastlines; clip individual line segments at knowledge edges, never close an unknown coast.
 if k=='birds':
  lines(land,.70,mask=know&(abs(lo)<70))
  lines(land,.38,mask=know&(abs(lo)>=70),dash=[3,3])
 else:lines(land,.70)
 lines(lake,.64)
 # Sparse short coastal accents, only offshore and only on known shores.
 co=contourpy.contour_generator(x=xs*scale+xoff,y=ys*scale+yoff,z=gaussian_filter(land.astype(float),1.3))
 for path in co.lines(.20):
  if len(path)<90:continue
  path=np.array(LineString(path).simplify(.55).coords)
  for start in range(8,len(path)-7,29):
   seg=path[start:start+6]
   if all(detail[ix(*q)] for q in seg):a.line(seg,.27)
 # Directed, established Panterran waterways. No fantasy cross-continent rivers.
 if k in ['cats','reptiles','birds','world']:
  for name,p in HY.items():clipped_geo(p,.72 if name.startswith('lake_to_') else .55)
 # Mask symbol placement around rivers so forest and terrain do not hide the watercourses.
 riverdist=np.full((ny,nx),999.,dtype='f');riverpix=np.zeros((ny,nx),bool)
 if k in ['cats','birds','reptiles','world']:
  for p in HY.values():
   for lon,lat in p:riverpix[ix(*pos(lon,lat))]=True
  riverdist=distance_transform_edt(~riverpix)
 symbols=[];occupied=np.zeros((ny,nx),bool);counts={}
 # Mountain symbols follow elevation maxima; the range footprint is not a line of arbitrary triangles.
 sm=gaussian_filter(elev,2);cand=(sm>1800)&(sm==maximum_filter(sm,size=15))&land&detail&~lake&(shore>11)&(riverdist>20)
 indices=np.argwhere(cand);rng.shuffle(indices);indices=sorted(indices,key=lambda q:float(sm[tuple(q)]),reverse=True)
 peaks=[]
 for i,j in indices:
  if occupied[i,j]:continue
  # Cats know only the facing spines, increasingly sparsely beyond their frontier.
  if k=='cats' and la[i,j]>36 and rng.random()>.35:continue
  if k=='reptiles' and lo[i,j]<44 and rng.random()>.45:continue
  x,y=xoff+xs[j]*scale,yoff+ys[i]*scale
  ht=6+min(sm[i,j]/1300,7.)+rng.uniform(-1.1,1.1);ht*=cfg.get('symbol_scale',1);wi=ht*(.92+rng.random()*.45)
  if min(x-RECT[0],RECT[2]-x,y-RECT[1],RECT[3]-y)<ht:continue
  
  if not all(allowed(q,5) for q in [(x-wi*.65,y),(x+wi*.65,y),(x,y+ht)]):continue
  peaks.append((x,y,wi,ht));r=max(16,int(ht*.55/(scale*(xmax-xmin)/nx)));occupied[max(0,i-r):i+r+1,max(0,j-r):j+r+1]=True
 for x,y,wi,ht in sorted(peaks,key=lambda p:-p[1]):
  peak=(x+rng.uniform(-.22,.22)*wi,y+ht)
  a.line([(x-wi*.65,y),(x-wi*.32,y+ht*.5),peak,(x+wi*.36,y+ht*.45),(x+wi*.65,y)],.57,fill=True)
  a.line([peak,(x+wi*.05,y+ht*.56),(x+wi*.2,y+ht*.4),(x+wi*.11,y+ht*.13)],.40)
  a.line([(peak[0]-.1*wi,peak[1]-.25*ht),(x-wi*.12,y+ht*.48),(x-wi*.28,y+ht*.32)],.28)
  if ht>10:a.line([(x+.31*wi,y+.35*ht),(x+.43*wi,y+.17*ht)],.25)
 counts['mountains']=len(peaks)
 # Coherent woodland belts with open crowns, never solid black tree stamps.
 forest=(wet>.51)&(elev<2300)&land&detail&~lake&(shore>9)&(riverdist>12)
 if k=='cats':forest&=(lo<-23)&(lo>-53)&(la>7)&(la<32)
 if k=='birds':forest&=(la<62)&(elev<1800)
 if k=='world':forest&=((lo<-23)&(lo>-53)&(la>7)&(la<32))|((lo>110)&(wet>.58))|((lo<-80)&(lo>-100)&(wet>.58))
 if k=='reptiles':forest&=(wet>.58)&((la>5)|(lo>115))
 cells=[]
 for i in range(14,ny-14,max(12,round(4.2/(scale*(ymax-ymin)/ny)))):
  for j in range(14,nx-14,max(12,round(4.2/(scale*(xmax-xmin)/nx)))):
   ii=i+int(rng.integers(-5,6));jj=j+int(rng.integers(-5,6))
   if forest[ii,jj] and not occupied[ii,jj] and rng.random()<.76:cells.append((xoff+xs[jj]*scale,yoff+ys[ii]*scale,ii,jj))
 for x,y,i,j in sorted(cells,key=lambda t:-t[1]):
  ht=rng.uniform(4.5,6.8)*cfg.get('symbol_scale',1);wi=ht*.58
  if rng.random()<.62:
   a.line([(x-wi,y+1.2),(x-wi*.48,y+ht*.45),(x-wi*.7,y+ht*.45),(x,y+ht),(x+wi*.7,y+ht*.45),(x+wi*.48,y+ht*.45),(x+wi,y+1.2)],.43,fill=True)
   a.line([(x,y+1.2),(x,y-.65)],.34)
  else:
   a.line([(x-wi*.65,y+1.7),(x-wi,y+3),(x-wi*.72,y+4.5),(x-wi*.3,y+4.6),(x,y+ht),(x+wi*.55,y+ht*.82),(x+wi*.5,y+ht*.55),(x+wi,y+3),(x+wi*.6,y+1.7)],.43,fill=True);a.line([(x,y+1.7),(x,y-.6)],.34)
 counts['trees']=len(cells)
 # Lowland vocabulary follows geography: steppe, fertile hills, dunes and glacial upland.
 hills=dunes=grass=ice=fields=0
 for i in range(30,ny-30,32):
  for j in range(30,nx-30,34):
   ii=i+int(rng.integers(-9,10));jj=j+int(rng.integers(-9,10));x,y=xoff+xs[jj]*scale,yoff+ys[ii]*scale
   if not (detail[ii,jj] and land[ii,jj] and not lake[ii,jj] and shore[ii,jj]>16 and riverdist[ii,jj]>14) or occupied[ii,jj] or forest[ii,jj]:continue
   h=elev[ii,jj];lon,lat=lo[ii,jj],la[ii,jj]
   if k in ['birds','world'] and abs(lat)>65:
    if rng.random()<.55:
     a.line([(x-4,y+1),(x-1,y+.3),(x+1,y+1.2),(x+5,y)],.30);a.line([(x-1,y+.3),(x-2,y-2)],.27);ice+=1
   elif k in ['reptiles','world'] and ((lon>52) or (k=='world' and -125<lon<-90)) and wet[ii,jj]<.46 and h<2000:
    a.line([(x-6,y),(x-3,y+1.8),(x,y+2.2),(x+3,y+1.2),(x+6,y+.8)],.40)
    if rng.random()<.4:a.line([(x-3,y-2),(x,y-1),(x+3,y-1.4)],.27)
    dunes+=1
   elif k in ['cats','world'] and -45<lon<35 and lat<9 and h<1700 and rng.random()<.5:
    a.line([(x-4,y),(x-3,y+5),(x+4,y+4.3),(x+5,y-.6),(x-4,y)],.38);a.line([(x-.7,y+.2),(x-.3,y+3.7)],.25);a.line([(x+1.8,y+.1),(x+1.6,y+3.5)],.25);fields+=1
   elif h>650 and h<2300 and rng.random()<.6:
    a.line([(x-5,y),(x-3,y+2),(x,y+2.6),(x+3,y+1.8),(x+5,y)],.40);hills+=1
   elif (k=='cats' or (k=='reptiles' and lon<47)) and lat>17 and lat<34 and rng.random()<.42:
    a.line([(x-2,y),(x-3,y+2)],.3);a.line([(x,y),(x+.2,y+2.6)],.3);a.line([(x+2,y),(x+3,y+1.5)],.3);grass+=1
 counts.update(hills=hills,dune_groups=dunes,steppe_marks=grass,ice_marks=ice,fields=fields)
 # Crater escarpment: an eroded ring of rim ticks on land, NOT a new circular coastline.
 if k=='birds':
  for f in FE:
   if f['id']=='01':basin=f
  # The actual shoreline above already carries the complete irregular impact-basin geometry.
  # Tick the low coastal scar only beside water; use a modest selection to keep it economical.
  m=land&know&(shore>8)&(shore<15)&(la>54)&(la<73)&(abs(lo)<32)
  ids=np.argwhere(m);rng.shuffle(ids);done=[]
  for i,j in ids:
   x,y=xoff+xs[j]*scale,yoff+ys[i]*scale
   if any((x-u)**2+(y-v)**2<60 for u,v in done):continue
   if len(done)>64:break
   a.line([(x,y),(x+1.3,y-2.8)],.28);done.append((x,y))
 # Map symbols for established sites only; no invented reptile cities or bird capitals.
 idset={'birds':[],'cats':['05','06','08','09','14','15','16','17','24','25','31'],'reptiles':['05','06','09','10','25'],'world':[] }[k]
 sites=[]
 for f in FE:
  if f['id'] not in idset or not coverage(f['lon'],f['lat']):continue
  x,y=pos(f['lon'],f['lat'])
  if not (RECT[0]+6<x<RECT[2]-6 and RECT[1]+6<y<RECT[3]-6):continue
  if f['id'] in ['05','31']:
   a.line([(x-3,y-2),(x+3,y+2)],.85);a.line([(x-2,y-3),(x+4,y+1)],.36)
  elif f['id'] in ['08','09','10']:
   a.line([(x-3,y-2),(x-3,y+3),(x-1,y+3),(x-1,y),(x+1,y),(x+1,y+3),(x+3,y+3),(x+3,y-2)],.57,fill=True)
  elif f['id']=='15':
   a.line([(x-3,y-2),(x-3,y+3),(x-1,y+1),(x,y+3),(x+2,y+1),(x+2,y-2)],.42,fill=True)
  else:a.ellipse(x,y,1.7,1.7,.55)
  sites.append((f,x,y))
 if not cfg.get('inset'):
  # Fine corner frame and small compass leave the drawing area unfilled.
  for x,y,dx,dy in [(28,29,1,1),(W-28,29,-1,1),(28,H-29,1,-1),(W-28,H-29,-1,-1)]:a.line([(x,y+dy*16),(x,y),(x+dx*28,y)],.38)
  a.text(W/2,H-48,cfg['title'],16,'Book');a.text(W/2,49,'',8)
  if k!='birds':
   cx,cy=W-55,H-108
   dx,dy=-math.sin(theta)*20,math.cos(theta)*20
   a.line([(cx-dx*.65,cy-dy*.65),(cx+dx,cy+dy)],.45)
   a.line([(cx+dx*.6-4*math.cos(theta),cy+dy*.6-4*math.sin(theta)),(cx+dx,cy+dy),(cx+dx*.6+4*math.cos(theta),cy+dy*.6+4*math.sin(theta))],.45)
   a.text(cx+dx*1.5,cy+dy*1.5,'N',9)
  else:
   px,py=pos(0,90);a.line([(px-4,py),(px+4,py)],.35);a.line([(px,py-4),(px,py+4)],.35)
  a.text(36,17,f'{cfg["culture"].upper()} / TRACING MASTER',7,'Book','left');a.text(W-180,17,'R10 geography / Letter tracing edition',7,'Book','left')
 # Reference labels are separate from the clean drawing.
 labels={
 'birds':[(1.8,61,'BLOOD LAKE'),(-8,49,'THE NORTHERN MASSIFS'),(-40,58,'WESTERN HIGH COUNTRY'),(49,62,'EASTERN RIM'),(-100,70,'ISLES OF LEGEND'),(100,70,'ISLES OF LEGEND'),(-30,22,'SOUTHERN LANDS UNKNOWN')],
 'cats':[(-11,12,'GREAT RESERVOIR'),(-36,23,'SEATTLE FOREST'),(-6,25,'PLATEAU STEPPE'),(-4,-1,'CULTIVATED HILLS'),(-25,-10,'WESTERN UPLANDS'),(8,-19,'SOUTHERN SPINE'),(-10,39,'NORTHERN DIVIDE'),(48,33,'EASTERN APPROACHES')],
 'reptiles':[(7,24,'PANTERRAN MARCHES'),(113,0,'UNEXPLORED EAST'),(96,-20,'THE LEEWARD DESERT'),(76,-7,'RIFT GULF'),(91,16,'THE GREAT DIVIDE'),(118,-34,'SOUTHERN CAPES'),(40,32,'WESTERN APPROACH')],
 'world':[(-12,4,'PANTERRA'),(98,-19,'EASTERN CONTINENT'),(-109,-39,'SOUTHERN HOMELAND'),(2,65,'BLOOD LAKE'),(-150,-3,'PELAGIC CROWN'),(65,-80,'SOUTH POLAR LANDS')]}[k]
 ref=Art();ref.items=list(a.items)
 for lon,lat,text in labels:
  x,y=pos(lon,lat)
  if k=='birds' and text=='POLAR CROWN':x-=20;y+=10
  if RECT[0]<x<RECT[2] and RECT[1]<y<RECT[3]:
   if text=='UNEXPLORED EAST':
    ref.text(x,y+5,'UNEXPLORED',8.5,'Italic',halo=True);ref.text(x,y-5,'EASTWARD',8.5,'Italic',halo=True)
   else:ref.text(x,y,text,8 if cfg.get('inset') else 10,'Italic',halo=True)
 for f,x,y in sites:
  name={'05':'Dam','06':'Downstream port','08':'Western Gate','09':'Central Gate','10':'Eastern Gate','14':'Fishing village','15':'Cliff ruins','16':'London','17':'Milan','24':'Seattle','25':'Rome','31':'Plateau falls'}[f['id']]
  if f['id']=='14':continue # Local site falls within dam symbol at world scale.
  dx,dy={'05':(25,-7),'25':(19,12),'16':(-10,-14),'31':(-25,10),'24':(-10,-14),'06':(25,-10),'15':(-25,-8)}.get(f['id'],(0,-14))
  ref.text(x+dx,y+dy,name,9,'Italic',halo=True)
 notes={'birds':'Polar routes and northern homeland, extending into Panterra. The pole is marked by a cross.', 'cats':'Panterra and the western reaches of the eastern continent. Open coast ends mark the limits of exploration.', 'reptiles':'One continuous chart: Panterran marches and eastern homeland. Open coast ends lead into unexplored lands.', 'world':'Full 360-degree equirectangular world; Panterra centered. No cultural limits are applied.'}
 if not cfg.get('inset'):ref.text(W/2,37,notes[k],8,'Italic',halo=True)
 if k=='birds':
  px,py=pos(0,90)
  ref.line([(px-4,py),(px+4,py)],.45);ref.line([(px,py-4),(px,py+4)],.45)
  ref.text(px,py-14,'North Pole',8,'Italic',halo=True)
 return a,ref,dict(**cfg,projection='Equirectangular, central meridian 0' if k=='world' else 'Lambert azimuthal equal-area; spherical radius cancels in page placement',symbols=counts,paths=len(a.items),source_sha256=hashlib.sha256((MODEL/'source/terrain_fields.npz').read_bytes()).hexdigest())

allstats=[];clean=pymupdf.open();key=pymupdf.open()
for cfg in CFG:
 W,H=792.,612.
 RECT=(25,55,W-25,H-68)
 a,r,stats=chart(cfg)
 allstats.append(stats)
 for suffix,art,doc in [('trace',a,clean),('reference',r,key)]:
  p=B/'individual'/f'{cfg["key"]}_{suffix}_Letter.pdf';c=canvas.Canvas(str(p),pagesize=(W,H),pageCompression=1);c.setTitle(cfg['title']+' / '+suffix);c.setAuthor('Catworld cartography');art.render(c);c.showPage();c.save();doc.insert_pdf(pymupdf.open(p))
  pg=pymupdf.open(p);pg[0].get_pixmap(matrix=pymupdf.Matrix(1.3,1.3),alpha=False).save(B/'png'/f'{cfg["key"]}_{suffix}_preview.png')
  if suffix=='trace':
   art.svg(B/'svg'/f'{cfg["key"]}_trace.svg')
   pix=pg[0].get_pixmap(matrix=pymupdf.Matrix(300/72,300/72),alpha=False,colorspace=pymupdf.csGRAY);pix.save(B/'png'/f'{cfg["key"]}_trace_300dpi.png')
 print(cfg['key'],stats['symbols'],flush=True)
clean.save(B/'01_CLEAN_TRACING_LETTER.pdf');key.save(B/'02_LABELLED_MAPS_LETTER.pdf')
# Alternate A4 pages retain each map's orientation and vector linework.
d=pymupdf.open()
for i,srcp in enumerate(clean):
 pw,ph=(595.28,841.89) if srcp.rect.height>srcp.rect.width else (841.89,595.28)
 p=d.new_page(width=pw,height=ph);p.show_pdf_page(pymupdf.Rect(20,20,pw-20,ph-20),clean,i)
d.save(B/'03_CLEAN_TRACING_A4.pdf',garbage=4,deflate=True)
# Optional 180% enlargement: four Letter sheets per map, 10 mm overlapping strips.
d=pymupdf.open();enlarge=1.8;overlap=28.3465/enlarge
for i,cfg in enumerate(CFG):
 W,H=clean[i].rect.width,clean[i].rect.height
 for row in range(2):
  for col in range(2):
   x0=col*(W-overlap)/2;y0=row*(H-overlap)/2;clip=pymupdf.Rect(x0,y0,x0+(W+overlap)/2,y0+(H+overlap)/2)
   p=d.new_page(width=W,height=H);x=(W-clip.width*enlarge)/2;y=(H-clip.height*enlarge)/2
   target=pymupdf.Rect(x,y,x+clip.width*enlarge,y+clip.height*enlarge);p.show_pdf_page(target,clean,i,clip=clip,keep_proportion=False)
   p.insert_text((28,17),f'{cfg["culture"].upper()} / {row+1}{chr(65+col)} / ACTUAL SIZE / 10 mm overlap',fontsize=7)
   for xx,yy,sx,sy in [(target.x0,target.y0,-1,-1),(target.x1,target.y0,1,-1),(target.x0,target.y1,-1,1),(target.x1,target.y1,1,1)]:
    p.draw_line((xx+sx*2,yy),(xx+sx*7,yy),width=.35);p.draw_line((xx,yy+sy*2),(xx,yy+sy*7),width=.35)
   p.draw_line((35,H-17),(176.7323,H-17),width=.5);p.insert_text((185,H-14),'50 mm calibration',fontsize=7)
d.save(B/'04_ENLARGED_TRACING_TILED_LETTER.pdf',garbage=4,deflate=True)
(B/'source/Cartography_Manifest.json').write_text(json.dumps(dict(revision='Tracing edition 3',world_revision=10,maps=allstats,print_scale='Four US Letter landscape originals; culturally rotated regional maps and one Panterra-centered equirectangular world; optional 180% tiled enlargement',knowledge_limits='Interpretive cultural coverage, not political borders',geometry='Coast and lake outlines sampled from R10; established hydrology paths projected from R10; relief symbols follow physical elevation',new_rivers=False),indent=2))
