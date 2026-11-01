"""R9 redline: hinged eastern core, curved shelf and sparse ocean islands.
Apply once after R8. Physical elevations remain metres.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, distance_transform_edt, gaussian_filter, zoom, label
from scipy.interpolate import PchipInterpolator
B=Path(__file__).resolve().parents[1]
CHAIN=[(276,-31),(284.5,-30.6),(291,-27.3),(299.5,-20),(305,-10),(310,-3.5),(315,7),(320,13)]
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def east_forward(lo,la):
 # Hinge at the existing western connection; southward rotation grows eastward.
 lo=np.asarray(lo);la=np.asarray(la);fade=1-smooth((la-44)/25);t=smooth((lo-45)/38);ang=np.radians(-13)*t*fade
 x=(lo-55)*.85;y=la-35
 xx=x*np.cos(ang)-y*np.sin(ang);yy=x*np.sin(ang)+y*np.cos(ang)
 dip=28*smooth((lo-26)/40)*(1-smooth((lo-72)/32))*fade
 return 55+xx/.85,35+yy-dip

def revise(apply_east=True):
 z=dict(np.load(B/'source/terrain_fields.npz'));h,w=z['land'].shape
 Y,X=np.mgrid[:h,:w];lat=(90-(Y+.5)*180/h).astype('f');lon=((X+.5)*360/w-180).astype('f');ux=lon%360
 c=np.array(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255
 # Invert the smooth two-dimensional warp, preserving terrain/biomes/coasts together.
 roi=(lon>24)&(lon<177)&(lat>-62)&(lat<75);tx=lon[roi];ty=lat[roi];sx=tx.copy();sy=ty.copy()
 if apply_east:
  for _ in range(65):
   fx,fy=east_forward(sx,sy);sx+=.45*(tx-fx);sy+=.45*(ty-fy)
  coords=[(90-sy)/180*h-.5,(sx+180)/360*w-.5]
  for k,a in z.items():
   old=a.copy();a[roi]=map_coordinates(old,coords,order=0 if a.dtype==bool else 1,mode='nearest')
  for k in range(3):c[...,k][roi]=map_coordinates(c[...,k].copy(),coords,order=1,mode='nearest')
 # Retire the old straight island approach and its submerged shelf.
 labs,_=label(z['land']);aust=labs[int((90+39)/180*h),int((-104+180)/360*w)];main=labs[int((90-20)/180*h),int(180/360*w)]
 zone=(ux>276)&(ux<316)&(lat>-38)&(lat<14)
 erase=zone&z['land']&~np.isin(labs,[aust,main]);clear=zone&(~z['land']|erase)
 for k in ['land','lake','small_lake','river']:z[k][erase]=False
 z['height'][clear]=-2100;z['surface'][clear]=0;c[clear]=[.012,.052,.095]
 rng=np.random.default_rng(9009)
 def noise(scale):
  sh=(max(4,h//scale),max(8,w//scale));a=rng.normal(size=sh).astype('f');return zoom(a,(h/sh[0],w/sh[1]),order=3,mode='wrap')[:h,:w]
 n1=noise(60);n2=noise(13);n3=noise(3)
 # Five islands follow a steep departure from the peninsula, then flatten toward the old shield.
 islands=[('Shelf fragment west',284.5,-30.6,2.9,1.6,23,1900,'shelf'),('Shelf fragment east',291,-27.3,2.0,1.0,28,1550,'shelf'),('Middle arc island',299.5,-20.0,1.3,.65,62,2100,'arc'),('Panterran arc remnant',305.1,-10.0,.70,.36,78,1150,'arc'),('Peninsula fore-island',310,-3.5,.48,.27,55,820,'arc'),
 ('Pelagic Crown / bigger Hawaii',210,-3.8,4.1,2.8,-22,4300,'hotspot'),('Crown older island',217.5,3.4,1.0,.60,-35,1750,'hotspot'),('Crown eroded remnant',228,9.1,.38,.25,-25,260,'hotspot'),
 ('Northern fjord island',191,49,1.8,.85,15,1400,'glacial'),('Northern split island',205,46.6,1.25,.75,-30,1100,'glacial'),('Northern skerry',213,51,.62,.35,30,600,'glacial'),
 ('Western seamount island',153,50,.50,.34,20,950,'hotspot'),('Western companion',148,46,.23,.17,35,400,'hotspot'),
 ('South ocean volcanic island',165,-42,.85,.43,-20,1900,'hotspot'),('South ocean remnant',173,-48,.32,.19,-25,650,'hotspot'),
 ('Equatorial ocean island',178,23,.45,.24,45,1200,'hotspot'),('Equatorial companion',183,27,.21,.15,35,350,'hotspot'),
 ('Warm-water atoll',234,-19,.34,.26,12,12,'atoll'),('Remote warm-water atoll',249,24,.27,.22,10,9,'atoll'),
 ('Northern ocean volcanic island',279,52,.55,.32,-10,1300,'hotspot'),('Northern ocean remnant',271,49,.25,.16,20,420,'hotspot'),
 ('Southern polar fore-island',220,-59,.75,.40,30,850,'glacial')]
 records=[]
 for j,(name,lo,la,a,b,ang,peak,kind) in enumerate(islands):
  dx=(lon-(lo+180)%360+180+180)%360-180 # wrapped difference
  dx=(ux-lo+180)%360-180;dy=lat-la;ang=np.radians(ang)
  xx=dx*np.cos(ang)+dy*np.sin(ang);yy=-dx*np.sin(ang)+dy*np.cos(ang)
  theta=np.arctan2(yy/b,xx/a);edge=1+.17*np.sin(3*theta+j)+.11*np.cos(5*theta-j*.8)+.055*np.sin(9*theta)
  rr=np.sqrt((xx/a)**2+(yy/b)**2)/edge
  island=(rr<1)&~z['land']
  if kind=='atoll':island&=rr>.57
  interior=np.maximum(0,1-rr);elev=35+peak*interior**1.3*(.87+.1*np.sin(xx*4+yy*2)+.05*n2)
  if kind=='hotspot':elev+=peak*.18*np.exp(-((xx-.3*a)/(.22*a))**2-(yy/(.35*b))**2)
  if kind=='atoll':elev=np.full_like(elev,peak)
  elev*=np.minimum(distance_transform_edt(island)/2,1)
  wet=np.clip(.42+.28*smooth((xx/a+.3)/1.1)+.06*n2,.2,.85)
  grass=np.stack([.35+.015*n2,.37+.015*n2,.20+.008*n3],-1);forest=np.stack([.10+.008*n3,.24+.014*n3,.12+.009*n3],-1)
  f=smooth((wet-.40)/.32);nc=grass*(1-f[...,None])+forest*f[...,None]
  rock=smooth((elev-1500)/1800);nc=nc*(1-rock[...,None])+np.array([.30,.29,.26])*rock[...,None]
  if kind=='glacial':
   snow=smooth((elev-700+(la-47)*90)/700);nc=nc*(1-snow[...,None])+np.array([.83,.88,.89])*snow[...,None]
  gy,gx=np.gradient(elev);shade=np.clip(1-.0018*gx+.0026*gy,.58,1.16);nc*=shade[...,None]
  if kind=='atoll':nc[:]=[.57,.59,.39]
  for k in ['height','surface']:z[k][island]=elev[island]
  z['land'][island]=True;z['wet'][island]=wet[island];c[island]=nc[island]
  # Each island has a submerged apron; deep ocean remains between unrelated groups.
  apron=(rr<1.9)&~z['land'];bed=-120-2600*smooth((rr-1)/.9);z['height'][apron]=np.maximum(z['height'][apron],bed[apron])
  if kind=='atoll':z['height'][(rr<.57)&~z['land']]=-18
  records.append(dict(name=name,lon=(lo+180)%360-180,lat=la,kind=kind,peak_m=float(elev[island].max()),cells=int(island.sum())))
 # A submerged curved ribbon preserves the migration concept without a dry connection today.
 dist=np.full((h,w),999.,dtype='f');tt=np.linspace(0,1,len(CHAIN));t=np.linspace(0,1,160);pp=np.array(CHAIN);cx=PchipInterpolator(tt,pp[:,0])(t);cy=PchipInterpolator(tt,pp[:,1])(t)
 for x,y in zip(cx,cy):dist=np.minimum(dist,np.hypot((ux-x)*.84,lat-y))
 shelf=(dist<2.4)&~z['land'];z['height'][shelf]=-42-12*smooth(dist[shelf]/2.4)+3*np.sin(ux[shelf]);z['surface'][shelf]=0
 # Refresh coastal water only around the edited oceans and eastern block.
 ocean=~z['land']&~z['lake'];waterzone=((ux>145)&(ux<318)&(lat>-64)&(lat<60))|(roi&(lat<48))
 dd=distance_transform_edt(~z['land']);sea=np.zeros_like(c)+[.012,.052,.095];sea+=np.exp(-dd/7)[...,None]*[.014,.10,.10]
 shallow=np.exp(-np.maximum(-z['height']-10,0)/85)*ocean;sea+=shallow[...,None]*[.008,.025,.028]
 c[ocean&waterzone]=sea[ocean&waterzone]
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 aquatic=z['river']|z['lake']|z['small_lake']
 for name,im in [('albedo_4096.png',np.uint8(np.clip(c,0,1)*255)),('height_16bit.png',np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)),('land_mask.png',np.uint8(z['land'])*255),('roughness.png',np.uint8(np.where(aquatic,.25,np.where(z['land'],.86,.30))*255))]:Image.fromarray(im).save(B/'textures'/name)
 fs=json.load(open(B/'source/features.json'))
 for f in fs:
  if apply_east and 24<f['lon']<177 and -62<f['lat']<57:f['lon'],f['lat']=map(float,east_forward(f['lon'],f['lat']))
  if f['id']=='20':f.update(lon=-60.8,lat=-19,name='Curved southern shelf archipelago',description='Five islands bend out from the Panterran peninsula; largest fragments near the southern mainland')
  if f['id']=='27':f.update(lon=-56,lat=-10,description='Curved drowned shelf; proposed migration corridor at lower sea level')
  if f['id']=='13':f.update(lon=-45,lat=10,description='Peninsula departure into the curved shelf island route')
  if f['id']=='26':f.update(lon=175,lat=-12,description='Deep ocean with isolated volcanic islands; no continuous eastern-to-southern land bridge')
 fs += [dict(id='37',name='Pelagic Crown / bigger Hawaii',lon=-150,lat=-3.8,description='Large isolated volcanic island; sparse older companions to the northeast'),dict(id='38',name='Northern fore-islands',lon=-155,lat=46.6,description='Three rugged islands south of the northern remnant and Greenland-like polar land'),dict(id='39',name='Southern ocean volcanic outpost',lon=165,lat=-42,description='Isolated shield island and distant eroded remnant')]
 json.dump(fs,open(B/'source/features.json','w'),indent=2)
 p=json.load(open(B/'source/planet.json'));p.update(revision=9,geographic_revision='South-swept eastern neck and additional southward inclination; curved five-island shelf; isolated hotspot and northern fore-islands');json.dump(p,open(B/'source/planet.json','w'),indent=2)
 json.dump(dict(revision=9,eastern_rotation_additional_deg=13 if apply_east else 0,neck_depression_deg=28 if apply_east else 0,eastern_warp_applied=apply_east,archipelago_centerline=CHAIN,islands=records,main_hydrology_unchanged=True),open(B/'source/Ocean_Revision_R9.json','w'),indent=2)
 print('R9 terrain complete:',len(records),'authored islands')
if __name__=='__main__':revise()
