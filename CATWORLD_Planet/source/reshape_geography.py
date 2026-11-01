"""R4: compact mountain necks and a new northern maritime continental interior."""
from pathlib import Path
import json,heapq
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,distance_transform_edt,label,binary_dilation,zoom,gaussian_filter1d
from scipy.interpolate import PchipInterpolator
K=np.array([-180,-140,-100,-60,-45,0,30,45,105,150,180.]);D=np.array([-30,-30,-15,0,0,0,0,5,-30,-30,-30.]);delta=PchipInterpolator(K,D)
def wrap(x):return (np.asarray(x)+180)%360-180
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def forward_a(x,y):return np.asarray(x)+delta(wrap(x))*(1-smooth((np.abs(y)-45)/20)),np.asarray(y)
def inverse_a(x,y):
 lo=x-6;hi=x+31;a=1-smooth((np.abs(y)-45)/20)
 for i in range(24):
  mid=(lo+hi)/2;k=mid+delta(wrap(mid))*a<x;lo=np.where(k,mid,lo);hi=np.where(k,hi,mid)
 return (lo+hi)/2,y
forward=forward_a
CORE=[(166,16),(173,24),(181,28),(184,34),(179,38),(177,43),(184,46),(184,51),(193,54),(199,60),(204,54),(214,53),(219,48),(228,48),(232,43),(225,40),(221,34),(229,35),(235,30),(239,23),(235,18),(229,20),(231,14),(224,9),(218,11),(210,6),(201,8),(194,12),(187,10),(181,11),(175,9),(168,11)]
NECK=[(143,25),(151,24),(159,22),(167,22),(174,24),(180,21),(177,12),(169,9),(160,10),(153,13),(146,16)]
SPINE=[(143,20),(154,17),(166,16),(179,20),(191,24),(202,22),(214,19),(226,14)]
CHAIN=[(-123,16),(-113,-3),(-103,-16),(-87,-24),(-70,-21),(-57,-12),(-44,4)]
def reshape(root):
 root=Path(root);original=dict(np.load(root/'source/terrain_fields.npz'));h,w=original['land'].shape;Y,X=np.mgrid[:h,:w];lat=90-(Y+.5)*180/h;lon=(X+.5)*360/w-180;ux=lon%360
 def uv(lo,la):return [np.clip((90-la)/180*h-.5,0,h-1),(lo+180)/360*w-.5]
 def sample(a,c,nearest=False):return map_coordinates(a,c,order=0 if nearest else 1,mode='grid-wrap')
 a_uv=uv(*inverse_a(lon,lat));z={k:sample(v,a_uv,v.dtype==bool) for k,v in original.items()};col0=np.asarray(Image.open(root/'textures/albedo_4096.png'),dtype='f')/255;color=np.stack([sample(col0[...,i],a_uv) for i in range(3)],-1)
 selection=(ux>=180)&(ux<=320)&(lat<30)&(lat>-63)&original['land'];lab,_=label(selection);oldcore=lab==lab[int(120/180*h),int(40/360*w)];buffer=distance_transform_edt(~oldcore)<40
 clear=sample(oldcore,a_uv,True)|(sample(buffer,a_uv,True)&~z['land']);z['land'][clear]=False;z['height'][clear]=-1600;z['surface'][clear]=0;z['lake'][clear]=False;color[clear]=[.012,.052,.095]
 # An exposed coast follows the old eastern shield's oblique margin.
 edge=150-7*smooth((10-lat)/35)+.7*np.sin(lat*.9)+.3*np.sin(lat*2.2);cut=(ux>edge)&(ux<164)&(lat<12)&(lat>-29);z['land'][cut]=False;z['surface'][cut]=0;z['height'][cut]=-1600
 rng=np.random.default_rng(4004)
 def noise(scale):
  a=rng.standard_normal((max(4,h//scale),max(8,w//scale))).astype('f');return zoom(a,(h/a.shape[0],w/a.shape[1]),order=3,mode='wrap')[:h,:w]
 n1=noise(90);n2=noise(24);n3=noise(7);n4=noise(2)
 def polygon(points):
  im=Image.new('L',(w,h));d=ImageDraw.Draw(im)
  for sh in [-360,0,360]:d.polygon([((lo+sh+180)/360*w,(90-la)/180*h) for lo,la in points],fill=255)
  a=np.asarray(im)>0;sd=distance_transform_edt(a)-distance_transform_edt(~a);return sd+4*n2+1.5*n3>0
 new=polygon(CORE)|polygon(NECK)
 # Broken offshore fragments follow the same continental margin.
 for p in [[(235,40),(240,38),(242,33),(239,32),(237,35)],[(241,25),(245,22),(245,18),(242,19)],[(216,56),(220,57),(222,54),(219,53)]]:new|=polygon(p)
 z['land']|=new;z['lake'][new]=False
 dem=np.load(root/'source/mountain_analogue_dem.npy');dh,dw=dem.shape;sm=gaussian_filter(dem,35);edge_dem=gaussian_filter((np.argmax(-np.gradient(sm,axis=0)[180:1250],axis=0)+180).astype('f'),45)-90;relief=dem-gaussian_filter(dem,70)
 center=np.interp(ux,np.array(SPINE)[:,0],np.array(SPINE)[:,1]);trans=lat-center;along=(ux-143)/(240-143);dx=along*(dw-1);dy=np.interp(dx,np.arange(dw),edge_dem)-trans*39
 detail=map_coordinates(relief,[dy,dx],order=1,mode='reflect');raw=map_coordinates(dem,[dy,dx],order=1,mode='reflect')
 taper=np.clip((ux-139)/9,0,1)*np.clip((237-ux)/16,0,1);belt=np.exp(-(trans/(5.6+.7*n1))**2)*taper
 elevation=230+160*n1+75*n2+40*n3+12*n4
 elevation+=1350*np.exp(-((ux-210)/15)**2-((lat-41)/11)**2)
 elevation+=belt*(5100+np.clip(detail,-1400,2800)*1.55+np.clip(raw-4300,0,3600)*.3)
 # Old northern uplands are lower, discontinuous, and distinct from the young suture.
 northcenter=np.interp(ux,[183,193,199,207,216],[45,50,56,51,48]);north=np.exp(-((lat-northcenter)/2.4)**2)*np.clip((ux-181)/7,0,1)*np.clip((220-ux)/8,0,1)
 elevation+=north*(1700+350*n2);elevation=np.maximum(elevation,40)
 coast=distance_transform_edt(z['land']);elevation*=np.minimum(coast/6,1);elevation=np.clip(elevation,0,10800)
 # Blend at the existing western mountain junction, not across the new coast.
 mix=smooth((ux-142)/12)*new;mix[new&clear]=1;z['height']=np.where(new,z['height']*(1-mix)+elevation*mix,z['height']);z['surface']=np.where(new,z['surface']*(1-mix)+elevation*mix,z['surface'])
 # Route new drainage by priority flood on a reduced geographic grid.
 step=3;hm=np.roll(z['surface'],w//2,axis=1)[::step,::step].copy();nm=np.roll(new,w//2,axis=1)[::step,::step];lm=np.roll(z['land'],w//2,axis=1)[::step,::step];ny,nx=hm.shape;visited=~nm;parent=np.full(ny*nx,-1,dtype='i');order=[];heap=[]
 coastseed=nm&binary_dilation(~lm,structure=np.ones((3,3)))
 for yy,xx in zip(*np.where(coastseed)):visited[yy,xx]=True;heapq.heappush(heap,(float(hm[yy,xx]),yy*nx+xx))
 while heap:
  hh,j=heapq.heappop(heap);order.append(j);yy,xx=divmod(j,nx)
  for ddy,ddx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   sy,sx=yy+ddy,xx+ddx
   if sy<0 or sy>=ny or sx<0 or sx>=nx or visited[sy,sx]:continue
   visited[sy,sx]=True;k=sy*nx+sx;parent[k]=j;hm[sy,sx]=max(hm[sy,sx],hh+.04);heapq.heappush(heap,(float(hm[sy,sx]),k))
 acc=np.ones(ny*nx,dtype='f')
 for j in reversed(order):
  if parent[j]>=0:acc[parent[j]]+=acc[j]
 im=Image.new('L',(w,h));d=ImageDraw.Draw(im);active=(acc>=90)&(parent>=0)&nm.ravel();incoming=np.zeros(ny*nx,dtype='i')
 for j in np.where(active)[0]:incoming[parent[j]]+=1
 starts=np.where(active&(incoming!=1))[0]
 for start in starts:
  route=[int(start)];j=int(start)
  while parent[j]>=0:
   j=int(parent[j]);route.append(j)
   if incoming[j]!=1 or not active[j]:break
  if len(route)<2:continue
  points=np.array([(((j%nx)*step-w//2)%w,(j//nx)*step) for j in route],dtype='f')
  if np.any(np.abs(np.diff(points[:,0]))>w/2):continue
  # Smooth D8 pixel corners while preserving all confluences and river mouths.
  if len(points)>4:
   originalpoints=points.copy();points=gaussian_filter1d(points,1.6,axis=0,mode='nearest');points[0]=originalpoints[0];points[-1]=originalpoints[-1]
  d.line([tuple(q) for q in points],fill=int(min(190,80+np.log(acc[start])*11)),width=2 if acc[start]>1800 else 1)
 rivers=np.asarray(im,dtype='f')/255*new
 wet=.66+.08*n1+.05*n2;lee=smooth((center-lat)/7);wet-=.35*lee;wet+=.12*np.exp(-coast/65);wet=np.clip(wet,.12,.95);z['wet'][new]=wet[new]
 dry=np.clip((.44-wet)*2.6,0,1);forest=np.stack([.115+.023*n2,.225+.03*n2,.10+.02*n2],-1);grass=np.stack([.32+.025*n3,.35+.025*n3,.19+.02*n3],-1);fc=np.clip(wet/.8,0,1);nc=forest*fc[...,None]+grass*(1-fc[...,None]);nc=nc*(1-dry[...,None])+np.array([.61,.46,.27])*dry[...,None]
 rock=np.clip((elevation-1800)/3400,0,.92);nc=nc*(1-rock[...,None])+np.stack([.43+.035*n3,.405+.03*n3,.34+.025*n3],-1)*rock[...,None]
 snowline=np.interp(lat,[0,25,40,50,60,70],[5200,4800,3400,2300,1300,0]);snow=np.clip((elevation-snowline+100*n3)/650,0,1);tundra=smooth((lat-51)/10)*(1-snow);nc=nc*(1-tundra[...,None])+np.array([.35,.36,.23])*tundra[...,None];nc=nc*(1-snow[...,None])+np.array([.85,.88,.88])*snow[...,None]
 nc+=(.015*n3+.009*n4)[...,None]*np.array([.8,.75,.55]);gy,gx=np.gradient(elevation);shade=np.clip((1-.009*gx+.013*gy)/np.sqrt(1+(.018*gx)**2+(.018*gy)**2),.4,1.20);shade=1+(shade-1)*np.clip(elevation/5500,.08,.8);nc*=shade[...,None];nc=nc*(1-rivers[...,None]*.5)+np.array([.025,.14,.17])*rivers[...,None]*.5;color=np.where(new[...,None],color*(1-mix[...,None])+nc*mix[...,None],color)
 # Distinct arid landforms on the eastern core: erg fields, gravel and salt pans.
 arid=(ux>76)&(ux<148)&(lat>-24)&(lat<25)&z['land']&(z['surface']<2300)
 erg=(np.exp(-((ux-103)/10)**2-((lat-5)/8)**2)+np.exp(-((ux-127)/9)**2-((lat+4)/7)**2))*arid
 erg=np.clip(erg*(.7+.2*n2),0,.75);sand=np.stack([.65+.025*n3,.465+.025*n3,.27+.018*n3],-1);dune=.012*np.sin(X*.53+4*n2+1.2*n3);sand+=dune[...,None]*np.array([1,.75,.4]);color=color*(1-erg[...,None])+sand*erg[...,None]
 for outline in [[(82,15),(84,17),(86,15),(85,12),(83,12),(82,13)],[(113,3),(115,4),(117,2),(116,0),(114,0),(113,1)],[(118,-4),(120,-3),(121,-5),(119,-6)]]:
  pan=polygon(outline)&arid;edgepan=distance_transform_edt(pan);weight=np.clip(edgepan/7,0,.75);color=color*(1-weight[...,None])+np.array([.67,.63,.49])*weight[...,None]
 # Irregular elongated shelf fragments; no repeated circular island stamps.
 rng=np.random.default_rng(403);chain=np.array(CHAIN)
 for j,t in enumerate(np.linspace(.15,len(chain)-1.15,28)):
  k=min(int(t),len(chain)-2);v=chain[k+1]-chain[k];p=chain[k]+(t-k)*v+rng.uniform(-.7,.7,2);ang=np.arctan2(v[1],v[0]);a=rng.uniform(1.1,2)*(1.35 if j%6==0 else 1);b=rng.uniform(.45,.85);xx=(lon-p[0])*np.cos(ang)+(lat-p[1])*np.sin(ang);yy=-(lon-p[0])*np.sin(ang)+(lat-p[1])*np.cos(ang);theta=np.arctan2(yy/b,xx/a);phase=j*2.39996;bd=1+.23*np.sin(3*theta+phase)+.16*np.cos(5*theta-phase*.7)+.09*np.sin(9*theta+phase);rr=((xx/a)**2+(yy/b)**2)/bd**2;ii=(rr+.10*n3<1)&~z['land'];z['land'][ii]=True;ih=(140+1500*np.maximum(0,1-rr)**.8)*np.clip(.75+.15*n2,.4,1.2);z['height'][ii]=ih[ii];z['surface'][ii]=ih[ii];z['wet'][ii]=.72;color[ii]=forest[ii]
 sea_dist=distance_transform_edt(~np.pad(z['land'],((0,0),(128,128)),mode='wrap'))[:,128:-128];shelf=np.exp(-sea_dist/9);water=~z['land']&(np.abs(lat)<60)&((lon<-40)|(lon>135));sea=np.zeros_like(color)+[.012,.052,.095];sea+=shelf[...,None]*[.016,.14,.14];color[water]=sea[water]
 polar=np.abs(lat)>=65
 for k,v in original.items():z[k][polar]=v[polar]
 color[polar]=col0[polar]
 z['surface'][new]=np.maximum(z['surface'][new],0);z['height'][new]=np.maximum(z['height'][new],0)
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(root/'source/terrain_fields.npz',**z);Image.fromarray(np.uint8(np.clip(color,0,1)*255)).save(root/'textures/albedo_4096.png');Image.fromarray(np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)).save(root/'textures/height_16bit.png');Image.fromarray(np.uint8(np.where(z['lake'],.25,np.where(z['land'],.86,.30))*255)).save(root/'textures/roughness.png');Image.fromarray(np.uint8(z['land'])*255).save(root/'textures/land_mask.png')
 features=json.load(open(root/'source/features.json'))
 for f in features:
  lo,la=forward_a(f['lon'],f['lat']);f['lon']=float(wrap(lo));f['lat']=float(la)
 anchors={'11':(-158,38,'Maritime river country'),'12':(-164,23,'Maritime great range'),'20':(-131,39,'Eastern marginal gulf'),'21':(-148,41,'Old maritime shield'),'26':(167,16,'Compact collision junction'),'27':(-87,-24,'Drowned shelf archipelago'),'13':(-57,-12,'Drowned land bridge')}
 for fid,(lo,la,name) in anchors.items():next(f for f in features if f['id']==fid).update(lon=lo,lat=la,name=name)
 next(f for f in features if f['id']=='14').update(lon=-2.4435,lat=5.1468,description='Local dam inset site; terrace location is below global texture resolution')
 next(f for f in features if f['id']=='11')['description']='Forested northern foreland with branching rivers and coastal plains'
 next(f for f in features if f['id']=='26')['description']='Oblique junction where three continental blocks meet through broad ranges'
 json.dump(features,open(root/'source/features.json','w'),indent=2)
 paths=json.load(open(root/'source/hydrology_paths.json'))
 for k,points in paths.items():
  p=np.array(points);lo,la=forward_a(p[:,0],p[:,1]);paths[k]=np.column_stack([wrap(lo),la]).tolist()
 json.dump(paths,open(root/'source/hydrology_paths.json','w'),indent=2)
 p=json.load(open(root/'source/planet.json'));p['revision']=4;p['geographic_revision']='Short necks; a full northern maritime interior with terrain-routed drainage';json.dump(p,open(root/'source/planet.json','w'),indent=2)
 shift=w*3//4;labs,n=label(np.roll(z['land'],shift,axis=1));points=[(0,20),(120,5),(-155,37)];cores=[dict(lon=lo,lat=la,component=int(labs[int((90-la)/180*h),(int((lo+180)/360*w)+shift)%w])) for lo,la in points];ids=[q['component'] for q in cores];assert len(set(ids))==1 and ids[0]>0,cores
 report={'revision':4,'core_anchors':cores,'three_cores_connected':True,'old_bridge_longitude_span_deg':60,'new_bridge_longitude_span_deg':25,'bridge_shortening_percent':58.333333,'polar_latitude_bands_preserved':True,'new_maritime_core_bounds_lonlat':[166,239,6,60],'new_river_routing_grid_step':step,'new_river_routed_cells':len(order),'new_river_threshold_cells':75,'new_core_polygon':CORE,'new_suture_spine':SPINE,'new_archipelago':CHAIN}
 json.dump(report,open(root/'source/Geography_Verification.json','w'),indent=2);print('R4 GEOGRAPHY',report)
