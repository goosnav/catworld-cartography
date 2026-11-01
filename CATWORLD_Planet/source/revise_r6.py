"""R6: coupled geography, plateau hydrology and a 35-degree seasonal snapshot."""
from pathlib import Path
import json, numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,zoom,distance_transform_edt,binary_opening,binary_dilation,label
from scipy.interpolate import PchipInterpolator
from revise_southern_r6 import CORE,SPINE,CHAIN

def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def east_transform(lo,la,inverse=False):
 lo=np.asarray(lo);la=np.asarray(la);a,b=np.radians(lo),np.radians(la)
 axis=np.array([np.cos(np.radians(38.15))*np.cos(np.radians(54.58)),np.cos(np.radians(38.15))*np.sin(np.radians(54.58)),np.sin(np.radians(38.15))])
 v=np.stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)],-1)
 ang=np.radians(8 if inverse else -8)*smooth((lo-54.58)/18)
 co=np.cos(ang)[...,None];si=np.sin(ang)[...,None]
 r=v*co+np.cross(axis,v)*si+axis*np.sum(v*axis,axis=-1)[...,None]*(1-co)
 return np.degrees(np.arctan2(r[...,1],r[...,0])),np.degrees(np.arcsin(np.clip(r[...,2],-1,1)))

def revise_r6(root):
 B=Path(root);z=dict(np.load(B/'source/terrain_fields.npz'));h,w=z['land'].shape
 yy,xx=np.mgrid[:h,:w];lat=(90-(yy+.5)*180/h).astype('f');lon=((xx+.5)*360/w-180).astype('f')
 color=np.asarray(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255
 roi=(lon>54.58)&(lon<180)&(lat>-62)&(lat<58)
 slo,sla=east_transform(lon[roi],lat[roi],True);coords=[(90-sla)/180*h-.5,(slo+180)/360*w-.5]
 for k,v in z.items():
  v=v.copy();v[roi]=map_coordinates(z[k],coords,order=0 if v.dtype==bool else 1,mode='grid-wrap');z[k]=v
 for i in range(3):color[...,i][roi]=map_coordinates(color[...,i].copy(),coords,order=1,mode='grid-wrap')
 rng=np.random.default_rng(6006)
 def noise(s):
  a=rng.standard_normal((h//s,w//s)).astype('f');return zoom(a,(h/a.shape[0],w/a.shape[1]),order=3,mode='wrap')[:h,:w]
 n1=noise(70);n2=noise(19);n3=noise(5);n4=noise(2)
 land=z['land']
 # A broad, dissected northern orogen replaces a single ribbon of mountains.
 dem=np.load(B/'source/mountain_analogue_dem.npy');dh,dw=dem.shape
 relief=dem-gaussian_filter(dem,45)
 dcoords=[((lat-27)/43*(dh-1)+20*n2).ravel(),((lon+75)/150*(dw-1)+30*n1).ravel()]
 dr=map_coordinates(relief,dcoords,order=1,mode='reflect').reshape(h,w)
 impact_distance=np.hypot((lon-1.8168)*.43,lat-64.987)
 protect=smooth((impact_distance-15)/6)
 province=smooth((lat-30)/7)*smooth((74-lat)/7)*smooth((lon+70)/8)*smooth((68-lon)/10)*protect
 eastern=np.zeros((h,w),dtype='f');center=36-.14*(slo-55)
 eastern[roi]=np.exp(-((sla-center)/6.0)**4)*smooth((slo-62)/10)*smooth((168-slo)/15)
 high=np.maximum(province,eastern)*land
 mountain_coast=smooth(distance_transform_edt(land)/15)
 folded=4200+950*n1+500*n2+1.65*dr+100*n3
 folded=np.clip(folded,2200,8900)*mountain_coast
 uplift=np.maximum(z['height'],folded)
 z['height']=z['height']*(1-high)+uplift*high;z['surface'][land]=z['height'][land]
 # Valley floors, scree and exposed bedrock have a consistent relief pattern.
 highcol=np.stack([.40+.035*n2,.365+.035*n2,.265+.025*n3],-1)
 valley=smooth((-dr-100)/450)*.40;highcol=highcol*(1-valley[...,None])+np.array([.30,.33,.19])*valley[...,None]
 gyh,gxh=np.gradient(z['height']);hs=np.clip(1-.002*gxh+.003*gyh,.58,1.17)
 highcol*=hs[...,None];color=color*(1-high[...,None])+highcol*high[...,None]
 oldlake=z['lake'].copy();lake=binary_opening(oldlake,iterations=3)
 labs,n=label(lake);counts=np.bincount(labs.ravel());counts[0]=0;lake=labs==counts.argmax()
 # Keep the original drowned valley. The crossed-out northeastern arm is removed.
 z['lake']=lake
 coast=distance_transform_edt(land)
 zone=land&(lon>-52)&(lon<36)&(lat>-48)&(lat<32)
 edge=smooth((32-lat)/6)*smooth((lon+52)/4)*smooth((36-lon)/6)*smooth((lat+48)/8)
 bench=1050+240*n1+105*n2+24*n3
 highground=bench+1350*smooth((lat-19)/12)
 coastal=smooth(coast/30)
 southern=smooth((16-lat)/12)
 rolling=170+220*np.maximum(n1+.7,0)+75*n2+24*n3
 target=(85+(highground*(1-southern)+rolling*southern)*coastal)
 blend=edge*.85*zone*smooth((4200-z['height'])/1600)
 z['height']=z['height']*(1-blend)+target*blend
 # Southern mountain groups: old uplifted blocks and eroded fold roots.
 southern_uplift=np.zeros((h,w),dtype='f')
 for ridge,width in [([(-32,-7),(-28,-7),(-24,-4),(-21,-8),(-22,-13)],33), ([(6,-10),(5,-13.5),(8.5,-15.3),(6.6,-18),(9.2,-20)],27)]:
  rim=Image.new('L',(w,h));rd=ImageDraw.Draw(rim);rd.line([((a+180)/360*w,(90-b)/180*h) for a,b in ridge],fill=255,width=2)
  dd=distance_transform_edt(np.asarray(rim)==0);province=np.exp(-(dd/width)**2)*land*smooth(coast/12)
  crests=np.clip(4200+700*n2+1.35*dr+150*n3,2200,5900)
  southern_uplift=np.maximum(southern_uplift,province*crests)
 z['height'][land]=np.maximum(z['height'][land],southern_uplift[land]);z['surface'][zone]=z['height'][zone]
 # The lake sits inside an incised valley, not on a flat elevated disk.
 dl=distance_transform_edt(~lake)
 valley_floor=690+80+140*n2+130*n3
 valley_weight=np.exp(-(dl/18)**2)*zone*(~lake)
 z['height']=z['height']*(1-valley_weight)+np.maximum(715,valley_floor)*valley_weight
 z['height'][lake]=600
 z['surface'][zone]=z['height'][zone];z['surface'][lake]=690
 z['height'][oldlake&~lake]=760;z['surface'][oldlake&~lake]=760
 # West is maritime forest; the interior plateau and foothills are dry steppe.
 west=smooth((-lon-18)/13)*smooth((lat+12)/10)*smooth((33-lat)/9)
 farm=smooth((18-lat)/10)*smooth((lon+33)/10)*zone
 wet=np.clip(.30+.07*n1+.035*n2+.49*west+.23*farm+.10*np.exp(-coast/22),.15,.90)
 z['wet'][zone]=wet[zone]
 steppe=np.stack([.45+.025*n2,.425+.025*n2,.255+.016*n3],-1)
 grass=np.stack([.35+.025*n2,.37+.025*n3,.19+.018*n3],-1)
 forest=np.stack([.10+.025*n3,.23+.03*n3,.105+.02*n4],-1)
 veg=smooth((wet-.27)/.27);nc=steppe*(1-veg[...,None])+grass*veg[...,None]
 # Crop mosaics represent regional agriculture, not individual fields at globe scale.
 cells=rng.random((h//3+1,w//4+1)).astype('f')
 cells=np.repeat(np.repeat(cells,3,axis=0),4,axis=1)[:h,:w]
 cells=gaussian_filter(cells,.65)-.5
 farms=np.stack([.335+.045*cells+.013*n3,.385+.040*cells+.012*n3,.175+.025*cells+.009*n4],-1)
 nc=nc*(1-farm[...,None])+farms*farm[...,None]
 wood=smooth((west-.20)/.70);nc=nc*(1-wood[...,None])+forest*wood[...,None]
 rock=smooth((z['height']-2200)/1800)*.9;nc=nc*(1-rock[...,None])+np.array([.43,.40,.32])*rock[...,None]
 gy,gx=np.gradient(z['height']);shade=np.clip(1-.0015*gx+.0025*gy,.7,1.15)
 nc*=shade[...,None];nc+=(.009*n3+.004*n4)[...,None];mix=edge*zone;color=color*(1-mix[...,None])+nc*mix[...,None]
 # Find an actual northeastern lake bank and grade one upper-plateau feeder into it.
 boundary=lake&binary_dilation(~lake);q=(lon+14.9)**2+(lat-16.34)**2;q[~boundary]=1e9
 iy,ix=np.unravel_index(q.argmin(),q.shape);mouth=[float(lon[iy,ix]),float(lat[iy,ix])]
 fall=[mouth[0]+.1,mouth[1]+.9]
 inlet=[[-30.9803, 36.8159], [-30.7872, 34.0401], [-29.8898, 32.1368], [-27.1172, 30.1533], [-22.5982, 29.0855], [-18.1677, 28.4392], [-17.0557, 26.7557], [-17.3309, 25.0903], [-19.6331, 22.9782], [-17.7141, 22.1531], [-14.8385, 20.9818], [-13.9349, 19.3762]]+[fall,mouth]
 inletlevel=[4500,3600,3000,2350,2050,1850,1650,1490,1330,1230,1180,1120,1090,690]
 westpath=[[-18.5944, 12.7096], [-20.7399, 12.8407], [-22.6727, 13.3273], [-26.2185, 13.3752], [-29.7948, 12.9449], [-33.1271, 12.6687], [-35.8512, 12.4202], [-38.3576, 9.6829]]
 # Snap the head to the actual western lake bank while keeping the creator's lower corridor.
 q=(lon-westpath[0][0])**2+(lat-westpath[0][1])**2;q[~boundary]=1e9;iy,ix=np.unravel_index(q.argmin(),q.shape);westpath[0]=[float(lon[iy,ix]),float(lat[iy,ix])]
 westlevel=[690,683,600,470,320,180,65,0]
 eastpath=[[-2.26, 4.9591], [-2.3378, 2.2019], [-1.6163, 0.7601], [0.93, -0.1383], [4.6624, -0.0145], [6.6582, -2.7092], [8, -4.7], [8.8, -7], [11, -8.3474]]
 eastlevel=[690,266,220,170,120,80,40,10,0]
 # Continuous interpolation uses the same heights for geometry and path metadata.
 allmask=np.zeros((h,w),bool);waterfield=np.zeros((h,w),dtype='f');flows={};profiles={}
 def river(name,pts,levels,width):
  pts=np.array(pts);ss=np.r_[0,np.cumsum(np.linalg.norm(np.diff(pts,axis=0),axis=1))];tt=np.linspace(0,ss[-1],max(400,int(ss[-1]*40)))
  curve=np.c_[PchipInterpolator(ss,pts[:,0])(tt),PchipInterpolator(ss,pts[:,1])(tt)];water=PchipInterpolator(ss,levels)(tt)
  mask=Image.new('L',(w,h));surf=Image.new('F',(w,h));dm=ImageDraw.Draw(mask);ds=ImageDraw.Draw(surf)
  uv=np.c_[(curve[:,0]+180)/360*w,(90-curve[:,1])/180*h]
  for j in range(len(uv)-1):
   pp=[tuple(uv[j]),tuple(uv[j+1])];dm.line(pp,fill=255,width=width);ds.line(pp,fill=float(water[j]),width=width)
  m=np.asarray(mask)>0;lev=np.asarray(surf).copy();dist,ind=distance_transform_edt(~m,return_indices=True);near=lev[tuple(ind)]
  banks=np.maximum(near+25,near+dist*13+6*n3);v=smooth((12-dist)/10)*land*(lon>-65)*(lon<40)*(~lake)
  z['height']=z['height']*(1-v)+banks*v;z['surface'][v>0]=z['height'][v>0]
  m&=land&~lake;z['height'][m]=np.maximum(0,lev[m]-10);z['surface'][m]=lev[m]
  green=np.exp(-(dist/8)**2)*.4*zone*(~lake);color[:]=color*(1-green[...,None])+np.array([.22,.32,.15])*green[...,None]
  color[m]=[.025,.135,.17];allmask[m]=True;waterfield[m]=lev[m]
  # Save dense geographic paths and exact designed water profiles.
  idx=np.linspace(0,len(curve)-1,64).astype(int);flows[name]=curve[idx].tolist();profiles[name]=dict(designed_water_m=water[idx].tolist(),descending=bool(np.all(np.diff(water)<=.01)))
 river('mountains_to_lake',inlet,inletlevel,3)
 river('lake_to_seattle_to_ocean',westpath,westlevel,5)
 river('lake_to_eastern_dam_to_ocean',eastpath,eastlevel,4)
 # Tributaries converge downstream; they are not extra reservoir spokes.
 river('northern_feeder_west_tributary',[[-31.19,28.8],[-29.42,28.15],[-26.26,26.24],[-24.36,26.68],inlet[4]],[2850,2700,2450,2250,inletlevel[4]],2)
 river('northern_feeder_east_tributary',[[-15.03,31.04],[-16,29.9],inlet[5]],[2600,2200,inletlevel[5]],2)
 river('seattle_northern_tributary',[[-32,21],[-31,18],[-30,15],westpath[4]],[950,720,470,westlevel[4]],2)
 river('seattle_coastal_tributary',[[-32.5,16.5],[-32.7,14.8],westpath[5]],[450,320,westlevel[5]],2)
 river('seattle_southern_tributary',[[-27,5],[-28,9.5],westpath[3]],[1050,730,westlevel[3]],2)
 river('eastern_southern_tributary',[[-1.34,-6.25],[-.75,-4.54],[1.07,-3.4],[3.02,-2.8],eastpath[4]],[720,530,360,240,eastlevel[4]],2)
 # A small mouth fork keeps the broad estuary readable without a maze of channels.
 river('seattle_estuary_branch',[westpath[6],[-38,13],[-41,14]],[65,25,0],2)
 # Three small lakes occupy distinct basins, rather than sprouting connected blue lines.
 small=np.zeros((h,w),bool);smallwater=np.zeros((h,w),dtype="f")
 for lo,la,rx,ry,level in [(9,23,.52,.30,1600),(-5,25,.45,.28,1980),(-32,19,.44,.32,650)]:
  m=(((lon-lo)/rx)**2+((lat-la)/ry)**2<1)&land&~lake
  small|=m;smallwater[m]=level
  ring=distance_transform_edt(~m);weight=np.exp(-(ring/5)**2)*zone*(~lake)
  z['height']=z['height']*(1-weight)+np.maximum(level+12,level+ring*4)*weight;z['surface'][zone&~lake]=z['height'][zone&~lake]
  z['height'][m]=level-20;z['surface'][m]=level;color[m]=[.035,.16,.19]
 z['small_lake']=small;z['river']=allmask;z['surface'][small]=smallwater[small];z['height'][small]=smallwater[small]-20
 z['surface'][allmask]=waterfield[allmask]
 sill=allmask&(((lon+20.5)**2+(lat-12.85)**2)<.07)&(waterfield>685)
 z['height'][sill]=685
 color[lake]=[.027,.16,.19];z['surface'][lake]=690;z['height'][lake]=600
 # Stronger autumn cooling; heat and ice mass are not calculated by a climate model.
 north=land&(lat>36)&~lake;sl=np.interp(lat,[36,45,55,65,80],[3900,2000,650,0,0]);sn=smooth((z['height']-sl+120*n2)/650)*north
 color=color*(1-sn[...,None]*.88)+np.array([.82,.87,.90])*sn[...,None]*.88
 ocean=~land;pack=ocean&(lat>66+2*np.sin(np.radians(lon)*3)+n1)&(lat<80)
 # Do not paint over the iron-red impact basin; its shoreline ice remains visible.
 red=(color[...,0]>color[...,1]*1.3)&(lon>-40)&(lon<40)&(lat>50);pack&=~red
 a=smooth((lat-66-n1)/8)*pack*.78;color=color*(1-a[...,None])+np.array([.66,.77,.82])*a[...,None]
 # Frame the valley and forest provinces with authoritative anchors.
 fs=json.load(open(B/'source/features.json'))
 for f in fs:
  if f['id'] in ['18','19','22']:
   f['lon'],f['lat']=map(float,east_transform(f['lon'],f['lat']))
 anchors={'06':(10.3271484375,-4.5263671875,'Alluvial trade outlet','Raised alluvial terrace beside the downstream eastern port and trade outlet'),'03':(-5,23,'Panterran Plateau','Steppe upland above the drowned reservoir valley'), '11':(-96,-36,'Southern eastern coast','Wet spring coast beneath the old escarpment'),'12':(-101,-42,'Southern escarpment','Old uplifted margin follows the redesigned eastern coast'),'20':(-75.6,-24.25,'Sparse eastern archipelago','Six principal islands and eight minor islands toward Panterra'),'21':(-116,-37,'Southern shield','Asymmetric dry continental interior'),'27':(-62.4,-13.75,'Drowned migration shelf','Submerged continental saddles between sparse island peaks'),'24':(-33.4,13.5,'Seattle / western forest country','Large forested region and lower-river port downstream of the western overflow'),'07':(-36,20,'Western old-growth country','Broad Seattle forest country; old growth covers the western watershed and hills'),'26':(182,-10,'Deep separating ocean','No island route between eastern and southern continents')}
 for f in fs:
  if f['id'] in anchors:
   lo,la,name,desc=anchors[f['id']];f.update(lon=lo,lat=la,name=name,description=desc)
 fs += [dict(id='31',name='Northern plateau falls',lon=fall[0],lat=fall[1],description='Upper-plateau river drops about 400 m into the reservoir valley'),dict(id='32',name='Natural western overflow',lon=-20.5,lat=12.85,description='High bedrock sill; reservoir spills west toward Seattle')]
 for f in fs:f.pop('sketch_xy',None)
 fs += [dict(id='33',name='Northern interior massifs',lon=-8,lat=48,description='Broad high country with parallel ranges, glaciated headwalls and deep valleys'),dict(id='34',name='Western high valleys',lon=-30,lat=40,description='Intermontane basins interrupt the vast northern mountain province')]
 fs += [dict(id='35',name='Southwestern mountain country',lon=-24,lat=-8,description='Broad older uplifts, high valleys and cultivated foothills'),dict(id='36',name='Southeastern peninsula ranges',lon=7,lat=-15,description='Rugged southern spine with lower tributary catchments')]
 json.dump(fs,open(B/'source/features.json','w'),indent=2);json.dump(flows,open(B/'source/hydrology_paths.json','w'),indent=2)
 p=json.load(open(B/'source/planet.json'));p.update(revision=6,tilt_deg=35,geographic_revision='Rotated eastern core; redesigned southern shield; sparse eastern archipelago; drowned plateau valley',r6=dict(eastern_rotation_deg=8,southern_shift_east_deg=41,southern_shift_south_deg=5,latest_southern_move_east_deg=16,principal_islands=6,minor_islands=8,reservoir_level_m=690,western_sill_bed_m=685,waterfall_drop_m=400))
 json.dump(p,open(B/'source/planet.json','w'),indent=2)
 json.dump(dict(revision=6,direction='Mountains -> plateau -> falls -> reservoir; reservoir -> western overflow -> Seattle -> sea; reservoir -> eastern dam -> downstream city -> sea',reservoir_level_m=690,western_overflow_sill_m=685,waterfall_upper_m=1090,waterfall_lower_m=690,profiles=profiles),open(B/'source/Hydrology_Verification.json','w'),indent=2)
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 for name,im in [('albedo_4096.png',np.uint8(np.clip(color,0,1)*255)),('height_16bit.png',np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)),('land_mask.png',np.uint8(land)*255),('roughness.png',np.uint8(np.where(lake|small|allmask,.25,np.where(land,.86,.3))*255))]:Image.fromarray(im).save(B/'textures'/name)
 r=json.load(open(B/'source/Geography_Verification.json'));r.update(revision=6,eastern_rotation_deg=8,nominal_archipelago_islands=14,plateau_valley=True);json.dump(r,open(B/'source/Geography_Verification.json','w'),indent=2)
 print('R6 TERRAIN COMPLETE',fall,mouth,flush=True)
if __name__=='__main__':revise_r6(Path(__file__).resolve().parents[1])
