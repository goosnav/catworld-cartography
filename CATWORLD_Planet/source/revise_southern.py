"""R5: detached southern continent, continental shelf migration route, late-autumn epoch.
Run once after the R4 reshape stage. The fields are art-directed, not a climate simulation.
"""
from pathlib import Path
import json,heapq
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import zoom,gaussian_filter,map_coordinates,distance_transform_edt,label,binary_dilation,gaussian_filter1d
CORE=[(177,-30),(181,-24),(188,-21),(192,-16),(198,-18),(201,-23),(205,-25),(209,-21),(212,-15),(217,-19),(223,-18),(227,-23),(224,-28),(230,-32),(228,-38),(222,-40),(220,-45),(214,-47),(212,-51),(207,-47),(202,-46),(199,-41),(194,-42),(191,-38),(188,-36),(184,-40),(180,-36)]
SPINE=[(218,-19),(220,-25),(222,-31),(219,-37),(216,-43),(211,-47)]
CHAIN=[(220,-23),(233,-22),(246,-22),(258,-19),(272,-15),(286,-8),(299,1),(313,12)]
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def revise(root):
 B=Path(root);z=dict(np.load(B/'source/terrain_fields.npz'));h,w=z['land'].shape;Y,X=np.mgrid[:h,:w];lat=90-(Y+.5)*180/h;lon=(X+.5)*360/w-180;ux=lon%360
 color=np.asarray(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255;initial_color=color.copy()
 rng=np.random.default_rng(5005)
 def noise(s):
  a=rng.standard_normal((max(4,h//s),max(8,w//s))).astype('f');return zoom(a,(h/a.shape[0],w/a.shape[1]),order=3,mode='wrap')[:h,:w]
 n1=noise(70);n2=noise(22);n3=noise(6);n4=noise(2)
 def polygon(pts,rough=1):
  im=Image.new('L',(w,h));d=ImageDraw.Draw(im)
  for sh in [-360,0,360]:d.polygon([((lo+sh+180)/360*w,(90-la)/180*h) for lo,la in pts],fill=255)
  a=np.asarray(im)>0;sd=distance_transform_edt(a)-distance_transform_edt(~a);return sd+rough*(3*n2+1.4*n3)>0
 # Remove the whole former northern maritime core and its two mountain necks.
 edge=150+4*np.sin(lat*.19)+1.6*np.sin(lat*.65)+.8*np.sin(lat*1.7)
 clear=(ux>edge)&(ux<300)&(lat>-62)&(lat<65)&((ux<250)|(lat<15))
 for k in ['land','lake']:z[k][clear]=False
 z['height'][clear]=-3100;z['surface'][clear]=0;z['wet'][clear]=0
 color[clear]=[.012,.052,.095]
 core=polygon(CORE,1.3);new=core.copy()
 # Continental fragments: long fault-aligned islands, gulf islands and an outer arc.
 outlines=[[(231,-20),(235,-17),(239,-16),(242,-18),(239,-20),(240,-22),(237,-23),(239,-27),(237,-30),(234,-27),(235,-24),(232,-24),(230,-22)],[(241,-29),(246,-25),(250,-24),(251,-26),(248,-29),(249,-31),(246,-32),(245,-36),(243,-35),(244,-31)],[(246,-16),(250,-13),(254,-14),(257,-16),(255,-17),(253,-16),(252,-19),(255,-20),(253,-22),(250,-20),(248,-19),(249,-17)],[(256,-23),(260,-21),(263,-23),(262,-27),(258,-29)],[(259,-15),(263,-12),(268,-11),(271,-13),(268,-14),(265,-14),(266,-17),(264,-20),(262,-18),(262,-16)],[(273,-15),(278,-12),(281,-14),(280,-18),(276,-19)],[(282,-8),(286,-5),(290,-6),(291,-10),(288,-12),(284,-10)],[(297,-2),(300,1),(303,0),(305,-3),(302,-6),(298,-4)],[(304,5),(309,8),(311,6),(310,2),(307,1)],[(205,-53),(208,-51),(210,-54),(207,-57),(204,-56)],[(230,-40),(232,-37),(236,-39),(238,-44),(235,-46),(232,-44)]]
 for pts in outlines:new|=polygon(pts,1.0)
 # Smaller asymmetric islands aligned with a remnant continental ribbon.
 for j in range(42):
  t=rng.uniform(.4,6.5);k=int(t);v=np.array(CHAIN[k+1])-CHAIN[k];p=np.array(CHAIN[k])+(t-k)*v+rng.normal(0,1.8,2);a=rng.uniform(.45,1.25);b=rng.uniform(.2,.6);ang=np.arctan2(v[1],v[0]);xx=(ux-p[0])*np.cos(ang)+(lat-p[1])*np.sin(ang);yy=-(ux-p[0])*np.sin(ang)+(lat-p[1])*np.cos(ang);th=np.arctan2(yy/b,xx/a);r=((xx/a)**2+(yy/b)**2)/(1+.24*np.sin(3*th+j)+.12*np.cos(7*th))**2;new|=r<1
 # A small northern remnant, not another northern continental mass.
 remnant=polygon([(194,54),(197,57),(201,58),(204,55),(202,52),(198,51),(196,53)],.9);new|=remnant
 z['land']|=new;z['lake'][new]=False;coast=distance_transform_edt(new)
 shore=distance_transform_edt(z['land']);easternedge=(ux>139)&(ux<165)&(lat>10)&(lat<45)&z['land'];taper=np.minimum(shore/6,1);z['height'][easternedge]*=taper[easternedge];z['surface'][easternedge]*=taper[easternedge]
 # Ancient shield, sandstone basins and rejuvenated eastern escarpment.
 center=np.interp(-lat,[15,19,25,31,37,43,47,60],[218,218,220,222,219,216,211,211]);trans=ux-center
 dem=np.load(B/'source/mountain_analogue_dem.npy');dh,dw=dem.shape;relief=dem-gaussian_filter(dem,60)
 detail=map_coordinates(relief,[(trans*43+dh*.5).ravel(),((-lat-10)/48*(dw-1)).ravel()],order=1,mode='reflect').reshape(h,w)
 belt=np.exp(-(trans/2.7)**2)*smooth((-lat-13)/8)*smooth((53+lat)/9)
 elev=230+140*n1+75*n2+28*n3+9*n4
 elev+=700*np.exp(-((ux-192)/9)**2-((lat+29)/10)**2)+420*np.exp(-((ux-207)/9)**2-((lat+34)/6)**2)
 elev+=belt*(2200+np.clip(detail,-850,1600)*1.1)
 islandridge=np.exp(-((lat-(-25+(ux-235)*.30))/4.2)**2)
 elev+=(1250+np.clip(detail,-500,1300)*.65)*islandridge*(~core)*(ux>230)*(ux<290)
 elev+=350*np.exp(-((ux-250)/9)**2-((lat+25)/12)**2)*(~core)
 elev=np.maximum(elev,35)*np.minimum(coast/5,1);elev[remnant]=500+300*np.maximum(n2[remnant],0)
 z['height'][new]=elev[new];z['surface'][new]=elev[new]
 # Recessed shelf joins the old mainland to the surviving archipelago and Panterra.
 dist=np.full((h,w),1000.,dtype='f')
 for a,b in zip(CHAIN[:-1],CHAIN[1:]):
  vx,vy=np.array(b)-a;t=np.clip(((ux-a[0])*vx+(lat-a[1])*vy)/(vx*vx+vy*vy),0,1);dist=np.minimum(dist,np.hypot((ux-a[0]-t*vx)*.82,lat-a[1]-t*vy))
 shelf=(dist<2.1)&~z['land'];bed=-38-14*smooth(dist/2.1)+4*np.sin(ux*.63)+2*n3
 z['height'][shelf]=np.maximum(z['height'][shelf],bed[shelf]);z['surface'][shelf]=0
 # Regional climates: dry subtropical west/interior, rainy eastern seaboard, cool wet southwest.
 wet=.22+.045*n1+.04*n2
 wet+=.52*smooth((ux-center+4)/7)*core
 wet+=.42*smooth((-lat-36)/9)*np.exp(-coast/75)*core
 wet+=.34*(~core);wet+=.12*np.exp(-coast/35);wet=np.clip(wet,.12,.92)
 z['wet'][new]=wet[new]
 sand=np.stack([.61+.035*n2,.405+.032*n2,.23+.023*n2],-1);forest=np.stack([.11+.018*n3,.245+.026*n3,.12+.015*n3],-1);grass=np.stack([.36+.02*n3,.38+.02*n3,.19+.02*n3],-1)
 g=smooth((wet-.23)/.24);f=smooth((wet-.48)/.3);nc=sand*(1-g[...,None])+grass*g[...,None];nc=nc*(1-f[...,None])+forest*f[...,None]
 # Interior ergs, pale endorheic pans and weathered stony ranges.
 erg=np.exp(-((ux-198)/9)**2-((lat+28)/6)**2)*core
 nc+=(.012*np.sin(X*.6+n2*5)*erg)[...,None]*np.array([1,.8,.5])
 for pts in [[(201,-31),(204,-30),(206,-32),(205,-35),(202,-34)],[(188,-28),(190,-26),(192,-28),(191,-30)]]:
  pan=polygon(pts,.5)&core;amount=np.clip(distance_transform_edt(pan)/6,0,.75);nc=nc*(1-amount[...,None])+np.array([.71,.66,.5])*amount[...,None]
 rock=np.clip((elev-1350)/2200,0,.8);nc=nc*(1-rock[...,None])+np.array([.40,.39,.33])*rock[...,None]
 snowline=3900-smooth((-lat-30)/25)*2400;snow=smooth((elev-snowline+70*n3)/500);nc=nc*(1-snow[...,None])+np.array([.86,.9,.92])*snow[...,None]
 gy,gx=np.gradient(elev);shade=np.clip((1-.008*gx+.013*gy)/np.sqrt(1+(.02*gx)**2+(.02*gy)**2),.55,1.2);nc*=1+(shade[...,None]-1)*np.clip(elev[...,None]/3500,.12,.9)
 nc+=(.009*n3+.007*n4)[...,None]
 # Priority-flood drainage for the new continental surface.
 step=3;hm=np.roll(z['surface'],w//2,axis=1)[::step,::step].copy();nm=np.roll(new,w//2,axis=1)[::step,::step];lm=np.roll(z['land'],w//2,axis=1)[::step,::step];ny,nx=hm.shape;visited=~nm;parent=np.full(ny*nx,-1,dtype='i');order=[];heap=[]
 for yy,xx in zip(*np.where(nm&binary_dilation(~lm,structure=np.ones((3,3))))):visited[yy,xx]=True;heapq.heappush(heap,(float(hm[yy,xx]),yy*nx+xx))
 while heap:
  hh,j=heapq.heappop(heap);order.append(j);yy,xx=divmod(j,nx)
  for ddy,ddx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   sy,sx=yy+ddy,xx+ddx
   if sy<0 or sy>=ny or sx<0 or sx>=nx or visited[sy,sx]:continue
   visited[sy,sx]=True;k=sy*nx+sx;parent[k]=j;hm[sy,sx]=max(hm[sy,sx],hh+.04);heapq.heappush(heap,(float(hm[sy,sx]),k))
 acc=np.ones(ny*nx,dtype='f')
 for j in reversed(order):
  if parent[j]>=0:acc[parent[j]]+=acc[j]
 im=Image.new('L',(w,h));d=ImageDraw.Draw(im);active=(acc>=65)&(parent>=0)&nm.ravel();incoming=np.zeros(ny*nx,dtype='i')
 for j in np.where(active)[0]:incoming[parent[j]]+=1
 for start in np.where(active&(incoming!=1))[0]:
  route=[int(start)];j=int(start)
  while parent[j]>=0:
   j=int(parent[j]);route.append(j)
   if incoming[j]!=1 or not active[j]:break
  if len(route)<2:continue
  pts=np.array([(((j%nx)*step-w//2)%w,(j//nx)*step) for j in route],dtype='f')
  if np.any(np.abs(np.diff(pts[:,0]))>w/2):continue
  if len(pts)>4:
   old=pts.copy();pts=gaussian_filter1d(pts,1.4,axis=0,mode='nearest');pts[0]=old[0];pts[-1]=old[-1]
  d.line([tuple(q) for q in pts],fill=140,width=2 if acc[start]>1000 else 1)
 rivers=np.asarray(im,dtype='f')/255*new
 # Arid channels are dry washes; permanent blue is confined to humid coastal catchments.
 stream=np.where((wet>.47)[...,None],np.array([.025,.12,.15]),np.array([.35,.28,.18]));nc=nc*(1-rivers[...,None]*.5)+stream*rivers[...,None]*.5;color[new]=nc[new]
 # Present epoch: Ls=255 deg, northern late autumn / southern late spring.
 northern=z['land']&(lat>38)&~z['lake'];snowline_n=np.interp(lat,[38,45,55,65,75,90],[3800,2500,1100,200,0,0]);frost=smooth((z['surface']-snowline_n+180*n2)/550)*northern
 seasonal=smooth((lat-39)/17)*.18*northern;color=color*(1-seasonal[...,None])+np.array([.34,.30,.21])*seasonal[...,None]
 color=color*(1-frost[...,None]*.86)+np.array([.81,.86,.90])*frost[...,None]*.86
 # Preserve the red lake's open centre while adding broken shore ice.
 blood=(np.hypot((lon-1.8)*.43,lat-65)<8)&~z['land'];distland=distance_transform_edt(~z['land']);lakeice=blood&(distland<5)&(lat>62)&(n3>-.2);color[lakeice]=[.65,.71,.73]
 ocean=~z['land']&~z['lake'];coastsea=distance_transform_edt(~np.pad(z['land'],((0,0),(128,128)),mode='wrap'))[:,128:-128];shallow=np.exp(-coastsea/10);sea=np.zeros_like(color)+[.012,.052,.095];sea+=shallow[...,None]*[.014,.12,.12]
 redistrict=clear|((lat<-60)&ocean)|((lat>65)&ocean&~blood);color[redistrict&ocean]=sea[redistrict&ocean]
 weight=np.clip(1-dist/2.2,0,1)*shelf;color=color*(1-weight[...,None]*.22)+np.array([.026,.16,.19])*weight[...,None]*.22
 # Northern pack expands, southern pack retreats; grounded southern ice survives spring.
 from seasonal_ice import northern_ice
 color=northern_ice(z,color,initial_color,lon,lat)
 southpack=ocean&(lat<-79+2*n1)&(n3>.3);color[southpack]=[.57,.7,.77]
 from open_eastern_ocean import open_ocean
 color,removed_arc_pixels=open_ocean(z,color,lon,lat)
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 Image.fromarray(np.uint8(np.clip(color,0,1)*255)).save(B/'textures/albedo_4096.png');Image.fromarray(np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)).save(B/'textures/height_16bit.png');Image.fromarray(np.uint8(np.where(z['lake'],.25,np.where(z['land'],.86,.30))*255)).save(B/'textures/roughness.png');Image.fromarray(np.uint8(z['land'])*255).save(B/'textures/land_mask.png')
 features=json.load(open(B/'source/features.json'))
 anchors={'11':(-140,-30,'Southern coastal river country','Warm eastern coastal catchments; southern late spring'),'12':(-139,-34,'Eastern escarpment','Rejuvenated old margin; distinct from the northern collision belt'),'20':(-125,-24,'Eastern shelf archipelago','Large continental fragments, drowned valleys and narrow sounds'),'21':(-163,-28,'Old southern shield','Dry sandstone basins, weathered uplands and salt pans'),'26':(169,-5,'Deep separating ocean','Open water separates the eastern core from the southern continent'),'27':(-100,-18,'Drowned migration shelf','Former dry crossing at illustrative sea level 65 m lower'),'13':(-57,-1,'Panterran shelf approach','Flooded final approach of the proposed cat migration route'),'23':(-161,55,'Northern remnant island','Small isolated glacial remnant; cooling into winter')}
 for f in features:
  if f['id'] in anchors:
   lo,la,name,desc=anchors[f['id']];f.update(lon=lo,lat=la,name=name,description=desc)
 json.dump(features,open(B/'source/features.json','w'),indent=2)
 p=json.load(open(B/'source/planet.json'));p.update(revision=5,geographic_revision='Detached southern continent and eastern shelf archipelago; main/eastern mountain link retained',seasonal_epoch={'solar_longitude_deg':255,'north':'late autumn; early winter conditions at high latitude','south':'late spring; approaching summer','years_since_northern_autumn_equinox':833,'years_until_northern_winter_solstice':167,'assumptions':'near-circular orbit, 24-hour rotation, habitable heat source unresolved'},migration_scenario={'old_homeland':'southern continent, proposed identification','lowstand_m':-65,'illustrative_crossing_years_before_present':1100,'mechanism':'southern grounded-ice storage; later net loss floods shelf','not_simulated':'ice mass, global sea level history and climate require further validation'})
 json.dump(p,open(B/'source/planet.json','w'),indent=2)
 shift=0
 def components(mask):
  labs,count=label(mask);parent=np.arange(count+1)
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for a,b in zip(labs[:,0],labs[:,-1]):
   if a and b:parent[find(b)]=find(a)
  table=np.array([find(i) for i in range(count+1)]);return table[labs]
 def val(a,lo,la):return int(a[int((90-la)/180*h),(int((lo+180)/360*w)+shift)%w])
 points=[(0,20),(120,5),(-160,-30)];lab=components(z['land']);ids=[val(lab,*q) for q in points];assert ids[0]==ids[1] and ids[2]>0 and ids[2]!=ids[0],ids
 low=components(z['land']|(z['height']>=-65));lowids=[val(low,*q) for q in points];assert len(set(lowids))==1 and lowids[0]>0,lowids
 area=6100**2*np.pi/h*2*np.pi/w*np.cos(np.radians(lat));report={'revision':5,'panterra_western_coast_preserved':True,'eastern_southern_ocean_has_no_island_arc':True,'removed_eastern_arc_pixels':removed_arc_pixels,'core_anchors':[dict(lon=lo,lat=la,component=i) for (lo,la),i in zip(points,ids)],'main_and_east_connected':True,'southern_core_separate':True,'south_polar_land_separate':val(lab,105,-77) not in ids,'historical_shelf_connected_at_minus65m':True,'lowstand_components':lowids,'southern_mainland_area_km2':float(area[core].sum()),'core_polygon':CORE,'eastern_range_spine':SPINE,'historical_shelf_centerline':CHAIN,'seasonal_epoch':p['seasonal_epoch'],'new_drainage_routed_cells':len(order)}
 json.dump(report,open(B/'source/Geography_Verification.json','w'),indent=2);print(json.dumps(report,indent=2))
if __name__=='__main__':revise(Path(__file__).resolve().parents[1])
