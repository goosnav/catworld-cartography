"""R7 natural landforms pass. Apply once after R6; all elevations remain in metres."""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import map_coordinates,gaussian_filter,zoom,distance_transform_edt,label,binary_dilation

def shift_point(lo,la):
 x=lo%360;t=float(np.clip((313-x)/40,0,1));return ((x+10*t+180)%360-180,la-t)
def revise(root):
 B=Path(root);z=dict(np.load(B/'source/terrain_fields.npz'));h,w=z['land'].shape
 Y,X=np.mgrid[:h,:w];lat=90-(Y+.5)*180/h;lon=(X+.5)*360/w-180;ux=lon%360
 c=np.asarray(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255
 rng=np.random.default_rng(7017)
 def noise(scale):
  a=rng.standard_normal((max(4,h//scale),max(8,w//scale))).astype('f')
  return zoom(a,(h/a.shape[0],w/a.shape[1]),order=3,mode='wrap')[:h,:w]
 n1,n2,n3=noise(70),noise(18),noise(5)
 def smooth(t):t=np.clip(t,0,1);return t*t*(3-2*t)
 def at(a,lo,la):return a[int((90-la)/180*h),int((lo+180)/360*w)%w]
 # Retain two large continental fragments, one mid-chain island and two small remnants.
 labs,count=label(z['land']);keep=[int(at(labs,*p)) for p in [(-83.6,-29.12),(-75.6,-24.29),(-60.98,-11.71),(-54.33,-2.84),(-50.7,1.01)]]
 sea_roi=(ux>270)&(ux<313)&(lat>-38)&(lat<12)
 main_ids={int(at(labs,0,20)),int(at(labs,-114,-38))}
 remove=sea_roi&z['land']&~np.isin(labs,keep+list(main_ids))
 z['land'][remove]=False;z['height'][remove]=-42;z['surface'][remove]=0;z['wet'][remove]=0
 c[remove]=[.015,.065,.105]
 # Compress the gap, translating the whole southern continent east by 10 degrees and south by 1.
 # The final Panterran endpoint stays fixed. The same warp moves shelf, relief and colour together.
 roi=(ux>210)&(ux<313)&(lat>-66)&(lat<14)
 oldx=np.where(ux<283,ux-10,(ux-78.25)/.75);delta=np.clip((313-oldx)/40,0,1)
 oldlat=lat+delta;oldlon=(oldx+180)%360-180
 coords=[((90-oldlat)/180*h-.5)[roi],((oldlon+180)/360*w-.5)[roi]]
 for k,a in z.items():
  b=a.copy();b[roi]=map_coordinates(a,coords,order=0 if a.dtype==bool else 1,mode='nearest');z[k]=b
 for k in range(3):c[...,k][roi]=map_coordinates(c[...,k].copy(),coords,order=1,mode='nearest')
 land=z['land'];lake=z['lake'];river=z['river'];coast=distance_transform_edt(land)
 original_river_height=z['height'][river].copy();original_river_surface=z['surface'][river].copy()
 sea_region=roi&~land
 shore_distance=distance_transform_edt(~land)
 sea=np.zeros_like(c)+[.012,.052,.095];sea+=np.exp(-shore_distance/8)[...,None]*[.012,.075,.075]
 c[sea_region]=sea[sea_region]
 # Erase the circular lake stamps and their artificial round embankments.
 oldsmall=z['small_lake'];erase=binary_dilation(oldsmall,iterations=8)
 _,ind=distance_transform_edt(erase,return_indices=True)
 for k in ['height','surface']:
  source=z[k].copy();z[k][erase]=source[tuple(ind)][erase]
 c[erase]=c[tuple(ind)][erase]
 # Break regular lowland lumps into subdued, dissected uplands. River corridors stay fixed.
 dem=np.load(B/'source/mountain_analogue_dem.npy');dh,dw=dem.shape
 dr=map_coordinates(dem-gaussian_filter(dem,38),[((lat+35)/90*(dh-1)+19*n2).ravel(),((lon+68)/115*(dw-1)+32*n1).ravel()],order=1,mode='reflect').reshape(h,w)
 waterdist=distance_transform_edt(~(river|lake));low=(lon>-55)&(lon<42)&(lat>-30)&(lat<34)&land
 strength=smooth(waterdist/14)*smooth(coast/10)*smooth((2200-z['height'])/1500)*low*.78
 target=gaussian_filter(z['height'],8)+np.clip(dr,-900,900)*.12+7*n3
 z['height']=z['height']*(1-strength)+target*strength;z['surface'][low&~lake&~river]=z['height'][low&~lake&~river]
 # Moisture boundaries follow irregular terrain rather than a straight longitude stripe.
 west=smooth((-lon-17+2.6*n1+1.5*n2)/15)*smooth((lat+13+n1)/11)*smooth((34-lat+n1)/10)
 farm=smooth((18-lat+2*n1)/12)*smooth((lon+34+n2)/11)
 wet=np.clip(.29+.045*n1+.035*n2+.48*west+.19*farm+.08*np.exp(-coast/24),.15,.9)
 steppe=np.stack([.445+.014*n2,.418+.015*n2,.267+.009*n3],-1)
 grass=np.stack([.345+.012*n2,.376+.012*n2,.205+.008*n3],-1)
 forest=np.stack([.105+.011*n2+.005*n3,.232+.015*n2+.009*n3,.12+.007*n3],-1)
 v=smooth((wet-.30)/.30);nc=steppe*(1-v[...,None])+grass*v[...,None]
 woods=smooth((west-.18)/.70);nc=nc*(1-woods[...,None])+forest*woods[...,None]
 gy,gx=np.gradient(z['height']);shade=np.clip(1-.0011*gx+.0016*gy,.83,1.12)
 nc*=shade[...,None];nc+=(.004*n3)[...,None]
 mix=smooth((34-lat)/5)*smooth((lon+55)/5)*smooth((42-lon)/7)*smooth((lat+30)/6)*smooth((2400-z['height'])/1100)*low
 mix*=smooth(waterdist/5)
 c=c*(1-mix[...,None])+nc*mix[...,None];z['wet'][low]=wet[low]
 # Three distinct drowned valley basins: a branching rift trough, hooked upland lake, forest valley lake.
 outlines=[
 (1600,[(7.15,24.25),(7.6,24.1),(8.2,23.6),(8.65,23.55),(8.7,24.15),(9.0,24.65),(9.13,24.35),(8.98,23.25),(9.48,22.72),(10.15,22.18),(10.6,21.45),(10.25,21.6),(9.65,22.15),(9.05,22.45),(8.75,22.95),(8.18,23.05),(7.65,23.65)]),
 (1980,[(-6.95,26.25),(-6.4,26.05),(-5.9,25.62),(-5.4,25.55),(-5.0,25.88),(-4.7,26.25),(-4.62,25.92),(-4.98,25.2),(-4.5,24.8),(-4.1,24.7),(-3.65,24.25),(-3.82,23.8),(-4.15,24.3),(-4.65,24.28),(-5.25,24.83),(-5.7,25.08),(-6.2,25.23),(-6.6,25.75)]),
 (650,[(-33.3,20.25),(-32.95,20.1),(-32.7,19.55),(-32.35,19.38),(-31.95,19.45),(-31.55,19.23),(-31.82,19.07),(-32.35,19.1),(-32.55,18.75),(-32.8,18.1),(-33.0,17.85),(-33.1,18.35),(-32.95,18.95),(-33.15,19.55)])]
 small=np.zeros((h,w),bool);lake_records=[]
 for level,pts in outlines:
  im=Image.new('L',(w,h));ImageDraw.Draw(im).polygon([((lo+180)/360*w,(90-la)/180*h) for lo,la in pts],fill=255)
  m=np.asarray(im)>0;sd=distance_transform_edt(m)-distance_transform_edt(~m);m=(sd+.55*n3>0)&land&~lake&~binary_dilation(river,iterations=2)
  components,num=label(m);sizes=np.bincount(components.ravel());sizes[0]=0;m=components==sizes.argmax()
  # Tributary notches and valley walls are tied to the same basin footprint.
  dd=distance_transform_edt(~m)
  enclosing=(dd>15)&(dd<25)&land&~lake&~river
  level=min(level,float(np.floor(np.percentile(z['height'][enclosing],10)/25)*25-50))
  influence=np.exp(-(dd/7)**2)*land*(~lake)*(~river)
  banks=level+16+dd*(6+2*smooth(n2))
  z['height']=z['height']*(1-influence)+banks*influence
  z['surface'][influence>.001]=z['height'][influence>.001]
  z['height'][m]=level-24;z['surface'][m]=level
  edge=np.clip(distance_transform_edt(m)/2.8,0,1);water=np.array([.034,.145,.17])+((1-edge)*.025)[...,None]*[.3,1,.7]
  c[m]=water[m];small|=m
  lake_records.append(dict(level_m=level,outline_lon_lat=pts,pixels=int(m.sum())))
 z['small_lake']=small
 z['height'][river]=original_river_height;z['surface'][river]=original_river_surface
 # Remove the ruler-straight snow edge by blending lower alpine transition with irregular elevation contours.
 north=land&(lon>-65)&(lon<65)&(lat>36)&(lat<53)&~river&~lake
 lum=c.mean(axis=2);snow=smooth((lum-.57)/.16)*north
 transition=smooth((lat-38+1.8*n1+.7*n2)/11)*smooth((z['height']-2300+220*n2)/2300)
 rock=np.stack([.43+.025*n2,.405+.022*n2,.32+.014*n3],-1)
 c=c*(1-(snow*(1-transition)*.82)[...,None])+rock*(snow*(1-transition)*.82)[...,None]
 # Anti-aliased water edges remove hard raster steps without altering water levels.
 aquatic=river|small|lake;aa=gaussian_filter(aquatic.astype('f'),.45)
 edge=(aa>.02)&(aa<.98)&~aquatic&land
 c[edge]=c[edge]*(1-aa[edge,None]*.6)+np.array([.029,.14,.17])*aa[edge,None]*.6
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 for name,im in [('albedo_4096.png',np.uint8(np.clip(c,0,1)*255)),('height_16bit.png',np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)),('land_mask.png',np.uint8(land)*255),('roughness.png',np.uint8(np.where(aquatic,.25,np.where(land,.86,.30))*255))]:Image.fromarray(im).save(B/'textures'/name)
 fs=json.load(open(B/'source/features.json'))
 for f in fs:
  if f['id'] in ['11','12','20','21','27']:
   f['lon'],f['lat']=shift_point(f['lon'],f['lat'])
  if f['id']=='20':f['description']='Two large rifted fragments, one middle island and two small remnants; wide open straits toward Panterra'
 json.dump(fs,open(B/'source/features.json','w'),indent=2)
 p=json.load(open(B/'source/planet.json'));p['revision']=7;p['r7']=dict(southern_move_east_deg=10,southern_move_south_deg=1,archipelago_retained_islands=5,small_lakes='three elongated branching valley basins',terrain='subdued dissected lowlands; irregular biome and alpine transitions');json.dump(p,open(B/'source/planet.json','w'),indent=2)
 r=json.load(open(B/'source/Geography_Verification.json'));r.update(revision=7,nominal_archipelago_islands=5,core_polygon=[shift_point(*p) for p in r['core_polygon']],eastern_range_spine=[shift_point(*p) for p in r['eastern_range_spine']],historical_shelf_centerline=[shift_point(*p) for p in r['historical_shelf_centerline']]);json.dump(r,open(B/'source/Geography_Verification.json','w'),indent=2)
 json.dump(dict(revision=7,retained_island_seed_components=keep,removed_island_cells=int(remove.sum()),lake_basins=lake_records,move_east_deg=10,move_south_deg=1),open(B/'source/Natural_Landforms_Revision.json','w'),indent=2)
 print('R7 NATURAL LANDFORMS COMPLETE',flush=True)
if __name__=='__main__':revise(Path(__file__).resolve().parents[1])
