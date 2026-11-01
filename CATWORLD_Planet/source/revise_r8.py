"""R8 process-informed art direction. Apply once after R7, not an erosion simulation.
Keep the approved tectonic layout, but replace repeated relief, painted bands,
uniform river strokes and regular lake silhouettes with coupled regional terrain.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import gaussian_filter,map_coordinates,distance_transform_edt,label,binary_dilation
from scipy.interpolate import PchipInterpolator
from scipy.spatial import cKDTree

def smooth(v):
 v=np.clip(v,0,1);return v*v*(3-2*v)

def revise(root):
 B=Path(root);z=dict(np.load(B/'source/terrain_fields.npz'));H,W=z['land'].shape
 Y,X=np.mgrid[:H,:W];lat=(90-(Y+.5)*180/H).astype('f');lon=((X+.5)*360/W-180).astype('f')
 oldh=z['height'].copy();oldsurf=z['surface'].copy();oldland=z['land'].copy()
 ref=np.asarray(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255
 rng=np.random.default_rng(8061)
 xyz=[np.cos(np.radians(lat))*np.cos(np.radians(lon)),np.cos(np.radians(lat))*np.sin(np.radians(lon)),np.sin(np.radians(lat))]
 def noise(f):
  cube=rng.standard_normal((64,64,64)).astype('f');a=map_coordinates(cube,[32+x*f for x in xyz],order=3,mode='grid-wrap',prefilter=True);return a.astype('f')
 n1,n2,n3,n4=[noise(f) for f in [8,25,80,220]]
 print('R8 spherical material fields',flush=True)
 # Polar coasts retain their geographic centres but lose polygon corners and straight segments.
 land=z['land'];polar=(abs(lat)>70)
 warped=map_coordinates(land.astype('f'),[Y+2.4*n2+1.2*n3,X+(3.5*n2+2*n3)/np.maximum(.13,np.cos(np.radians(lat)))],order=1,mode='nearest')
 lp=gaussian_filter(warped,1.2)>.5;land[polar]=lp[polar]
 new=land&~oldland;lost=~land&oldland
 oldh[new]=np.maximum(30,gaussian_filter(np.maximum(oldh,0),5)[new]);oldh[lost]=-60
 z['land']=land;coast=distance_transform_edt(land);offshore=distance_transform_edt(~land)
 # Remove obsolete channel and lake trenches before replacing them. This avoids duplicate ghosts.
 aquatic=z['river']|z['small_lake'];erase=binary_dilation(aquatic,iterations=7)
 _,idx=distance_transform_edt(erase,return_indices=True)
 terrain=oldh.copy();terrain[erase]=oldh[tuple(idx)][erase]
 macro=gaussian_filter(terrain,32)
 dem=np.load(B/'source/mountain_analogue_dem.npy');dh,dw=dem.shape
 # Bounded, gently warped DEM sampling: no reflecting rows and no repeated mirrored ridges.
 relief=dem-gaussian_filter(dem,95)
 a=(lon+180)/360
 row=np.clip((73-lat)/146*(dh-1)+1.5*n1,0,dh-1)
 col=np.clip(a*(dw-1)+2*n1,0,dw-1)
 dr=map_coordinates(relief,[row,col],order=1,mode='nearest')
 # Rotate a second bounded patch over the southern shield; crossfade instead of tile seams.
 row2=np.clip(800+(lon+104)*13+(lat+39)*4+1.5*n1,20,dh-20)
 col2=np.clip(1300-(lat+39)*20+(lon+104)*5+2*n2,20,dw-20)
 southern=smooth((lon+145)/15)*smooth((-65-lon)/14)*smooth((-lat-10)/13)*smooth((lat+66)/12)
 dr2=map_coordinates(relief,[row2,col2],order=1,mode='nearest');dr=dr*(1-southern)+dr2*southern
 # High ground has deeply incised massifs; sedimentary lowlands have much gentler relief.
 amplitude=.12+2.8*smooth((macro-900)/3200)
 terrain=macro+amplitude*dr+18*n3+5*n4
 terrain=np.maximum(25,terrain)*smooth(coast/4)+12*smooth((4-coast)/4)
 terrain[~land]=oldh[~land]
 terrain=np.minimum(terrain,10300)
 # Polar relief uses spherical noise rather than latitude-longitude DEM sampling.
 # This removes the radial pinching where meridians meet.
 polarblend=smooth((abs(lat)-68)/10)*land
 polarheight=(2100+420*n1+160*n2+55*n3)*smooth(coast/9)+20
 terrain=terrain*(1-polarblend)+polarheight*polarblend
 # Impact basin: asymmetrical eroded sectors and drainage, retaining the established basin extent.
 dl=((lon-1.8168+180)%360-180)*np.cos(np.radians(lat));dy=lat-64.987
 radius=np.hypot(dl,dy);az=np.arctan2(dy,dl)
 impact=smooth((24-radius)/8)*land
 sector=.65+.22*np.sin(3*az+.6)+.13*np.sin(7*az)
 terrain=terrain*(1-impact*.55)+((macro*(.72+.28*sector)+dr*1.5)*(impact*.55))
 # Smooth the reservoir perimeter without moving its outlets, and flood small tributary coves.
 lake=z['lake'];sd=distance_transform_edt(lake)-distance_transform_edt(~lake)
 paths=json.load(open(B/'source/hydrology_paths.json'));hydro=json.load(open(B/'source/Hydrology_Verification.json'))
 protected=np.zeros((H,W),bool)
 for path in list(paths.values())[:3]:
  for lo,la in [path[0],path[-1]]:
   protected|=((lon-lo)*np.cos(np.radians(la)))**2+(lat-la)**2<1.1**2
 contour=gaussian_filter(sd,1.1)+1.8*n2+.7*n3
 lake=np.where(protected,lake,contour>0)&land
 dd=distance_transform_edt(~lake);valley=np.exp(-(dd/10)**2)*land*~lake
 terrain=terrain*(1-valley)+np.maximum(710,710+dd*(6+3*n2))*valley
 terrain[lake]=600;z['lake']=lake;z['height']=terrain;z['surface']=terrain.copy();z['surface'][~land]=0;z['surface'][lake]=690
 print('R8 relief and drowned valley',flush=True)
 # Curves keep their story corridors but acquire asymmetrical bends. Tributary joins move with parents.
 parents={'northern_feeder_west_tributary':'mountains_to_lake','northern_feeder_east_tributary':'mountains_to_lake','seattle_northern_tributary':'lake_to_seattle_to_ocean','seattle_coastal_tributary':'lake_to_seattle_to_ocean','seattle_southern_tributary':'lake_to_seattle_to_ocean','eastern_southern_tributary':'lake_to_eastern_dam_to_ocean','seattle_estuary_branch':'lake_to_seattle_to_ocean'}
 newpaths={};newprofiles={};curves={};levels={};allriver=np.zeros((H,W),bool)
 waterfield=np.zeros((H,W),dtype='f');riparian=np.zeros((H,W),dtype='f')
 for k,(name,points) in enumerate(paths.items()):
  pts=np.array(points);lev=np.array(hydro['profiles'][name]['designed_water_m'])
  t=np.linspace(0,1,len(pts));tangent=np.gradient(pts,axis=0);norm=np.linalg.norm(tangent,axis=1);normal=np.c_[-tangent[:,1],tangent[:,0]]/np.maximum(norm[:,None],1e-9)
  bend=(.11*np.sin(t*9*np.pi+k)+.055*np.sin(t*19*np.pi+k*2))*np.sin(np.pi*t)**1.2
  if name=='lake_to_eastern_dam_to_ocean':bend*=smooth(t/.22)
  moved=pts+normal*bend[:,None]
  if name in parents:
   parent=parents[name];oldparent=np.array(paths[parent]);j=np.argmin(np.sum((oldparent-(pts[0] if name=='seattle_estuary_branch' else pts[-1]))**2,axis=1))
   end=0 if name=='seattle_estuary_branch' else -1
   moved[end]=newpaths[parent][j];lev[end]=newprofiles[parent]['designed_water_m'][j]
   lev=np.minimum.accumulate(lev)
  newpaths[name]=moved.tolist();newprofiles[name]=dict(designed_water_m=lev.tolist(),descending=True)
  tt=np.linspace(0,1,1800);curve=np.c_[PchipInterpolator(t,moved[:,0])(tt),PchipInterpolator(t,moved[:,1])(tt)];wl=PchipInterpolator(t,lev)(tt)
  curves[name]=curve;levels[name]=wl
  mask=Image.new('L',(W,H));water=Image.new('F',(W,H));dm=ImageDraw.Draw(mask);dw=ImageDraw.Draw(water)
  uv=np.c_[(curve[:,0]+180)/360*W,(90-curve[:,1])/180*H]
  trunk=k<3
  for j in range(len(uv)-1):
   width=max(1,round((1.35+1.6*tt[j] if trunk else .9+.8*tt[j])*(1+.15*np.sin(tt[j]*35+k))))
   segment=[tuple(uv[j]),tuple(uv[j+1])];dm.line(segment,fill=255,width=width);dw.line(segment,fill=float(wl[j]),width=width)
  m=np.array(mask)>0;v=np.array(water);dist,ind=distance_transform_edt(~m,return_indices=True);near=v[tuple(ind)]
  # Floodplain width scales with position downstream, while banks blend into existing ground.
  bank=near+12+dist*(7+3*smooth(n2));blend=np.exp(-(dist/5)**2)*land*~lake
  z['height']=z['height']*(1-blend)+bank*blend;z['surface'][blend>.001]=z['height'][blend>.001]
  m&=land&~lake
  z['height'][m]=v[m]-12;z['surface'][m]=v[m];allriver|=m;waterfield[m]=v[m]
  riparian=np.maximum(riparian,np.exp(-(dist/4)**2)*land)
 # Raster cells at saved path samples use the exact recorded level, including confluences.
 for name,points in newpaths.items():
  for (lo,la),lev in zip(points,newprofiles[name]['designed_water_m']):
   y=int((90-la)/180*H);x=int((lo+180)/360*W)%W
   if land[y,x] and not lake[y,x]:allriver[y,x]=True;waterfield[y,x]=lev
 z['river']=allriver;z['surface'][allriver]=waterfield[allriver];z['height'][allriver]=waterfield[allriver]-12
 json.dump(newpaths,open(B/'source/hydrology_paths.json','w'),indent=2);hydro.update(revision=8,profiles=newprofiles);json.dump(hydro,open(B/'source/Hydrology_Verification.json','w'),indent=2)
 # Distinct natural basins, not matching Y-shaped stamps. Width follows subdued valley lobes.
 small=np.zeros((H,W),bool);records=[]
 specs=[(9,23,1.55,.42,-.50),( -5.25,25.1,1.12,.62,.42),(-32.7,19.1,.38,1.12,-.18)]
 for j,(lo,la,rx,ry,ang) in enumerate(specs):
  dx=lon-lo;dy=lat-la;u=dx*np.cos(ang)+dy*np.sin(ang);v=-dx*np.sin(ang)+dy*np.cos(ang)
  center=.18*np.sin(u/rx*3+j)+.06*np.sin(u/rx*7)
  score=1-(u/rx)**2-((v-center)/ry)**2+.19*n2+.12*n3
  m=(score>0)&land&~lake&~binary_dilation(allriver,iterations=2)
  labs,count=label(m);sizes=np.bincount(labs.ravel());sizes[0]=0;m=labs==sizes.argmax()
  dist=distance_transform_edt(~m);surround=(dist>9)&(dist<19)&land&~allriver&~lake
  level=float(np.floor(np.percentile(z['height'][surround],10)/25)*25-30)
  b=np.exp(-(dist/5)**2)*land*~allriver*~lake
  z['height']=z['height']*(1-b)+(level+12+dist*(9+2*n2))*b;z['surface'][b>.001]=z['height'][b>.001]
  z['height'][m]=level-25;z['surface'][m]=level;small|=m;records.append(dict(center=[lo,la],surface_m=level,cells=int(m.sum())))
 z['small_lake']=small
 print('R8 river bends, confluences and lake basins',flush=True)
 # A continuous moisture field follows coastal exposure, relief and broad regional rain shadows.
 height=z['height'];gy,gx=np.gradient(gaussian_filter(height,1));reliefshade=np.clip(1-.00038*gx+.00055*gy,.74,1.15)
 valleytexture=smooth((-dr-60)/350)
 west=smooth((-lon-18+1.4*n1)/14)*smooth((lat+12+n1)/11)*smooth((35-lat+n1)/10)
 main=smooth((lon+60)/8)*smooth((48-lon)/8)*smooth((lat+32)/8)*smooth((40-lat)/8)
 farm=smooth((18-lat+n1)/13)*smooth((lon+37)/10)*main
 wet=z['wet'].copy();wet=gaussian_filter(wet,13)+.075*n1+.035*n2+.035*valleytexture
 wet=wet*(1-main)+(.28+.50*west+.17*farm+.055*valleytexture+.07*n1+.025*n2+.08*riparian)*main
 wet=np.clip(wet,0,.95);z['wet']=wet.astype('f')
 desert=np.zeros_like(ref)+[.48,.365,.225];desert+=(.018*n1+.012*n2+.006*n3)[...,None]*[1,.8,.5]
 steppe=np.zeros_like(ref)+[.41,.39,.265];grass=np.zeros_like(ref)+[.29,.345,.185]
 forest=np.zeros_like(ref)+[.095,.22,.125]
 green=smooth((wet-.27)/.34);c=desert*(1-smooth((wet-.14)/.20)[...,None])+steppe*smooth((wet-.14)/.20)[...,None]
 c=c*(1-green[...,None])+grass*green[...,None]
 woods=smooth((wet-.57)/.22)*smooth((3400-height)/1900)
 c=c*(1-woods[...,None])+forest*woods[...,None]
 # Southern shield: warm weathered interior, greener maritime east, subdued dry lake pans.
 red=np.zeros_like(c)+[.47,.285,.16];red+=(.014*n2+.008*n3)[...,None]
 interior=southern*smooth((.55-wet)/.3)*smooth((coast-5)/12)
 c=c*(1-interior[...,None]*.65)+red*interior[...,None]*.65
 # Farms are tonal regional mosaics on low slopes, not a regular checkerboard of giant fields.
 mosaic=(.014*n2+.01*n3+.004*n4)*farm*smooth((2000-height)/1200)
 c+=mosaic[...,None]*[.8,1,.3]
 rock=smooth((height-2300)/2500)*.85
 rockcol=np.zeros_like(c)+[.39,.365,.30];rockcol+=(.022*n2+.012*n3)[...,None]
 c=c*(1-rock[...,None])+rockcol*rock[...,None]
 # Iron staining follows eroded basin sectors rather than an even red annulus.
 iron=smooth((20-radius)/5)*land*smooth((radius-7)/4)*(.72+.18*n1+.12*valleytexture)
 iron=np.clip(iron,0,.75);c=c*(1-iron[...,None])+np.array([.48,.22,.105])*iron[...,None]
 # Cold exposed ground is tundra and rock, never a green ring around polar ice.
 cold=smooth((abs(lat)-59)/10)
 c=c*(1-cold[...,None])+np.array([.36,.35,.28])*cold[...,None]
 # Sparse, altitude-controlled snow and exposed steep ridges break the horizontal wall.
 snowline=np.where(lat>=0,5000-80*np.maximum(lat-25,0),5200-100*np.maximum(-lat-42,0))
 snowline+=220*n1+110*n2
 snow=smooth((height-snowline)/800)
 snow=np.maximum(snow,smooth((lat-67+n1)/8)*.95)
 snow=np.maximum(snow,smooth((-lat-64+n1)/8)*.98)
 exposure=smooth((np.hypot(gx,gy)-140)/450);snow*=1-exposure*.60
 ice=np.zeros_like(c)+[.79,.835,.85];ice+=(.012*n3+.006*n4)[...,None]
 c=c*(1-snow[...,None])+ice*snow[...,None]
 c*=reliefshade[...,None];c+=(.005*n3+.0025*n4)[...,None]
 # Ocean shelves vary with depth and sediment; avoid identical glowing turquoise coast halos.
 sea=np.zeros_like(c)+[.015,.066,.105]
 shallow=np.exp(-offshore/5)*(.55+.18*n1+.12*n2)
 sea+=shallow[...,None]*[.025,.095,.085]
 c[~land]=sea[~land]
 # Keep the red impact water; vary coastal iron suspension and open-basin depth.
 redwater=(~land)&(radius<20)&(lat>50)
 rwater=np.zeros_like(c)+[.19,.064,.039]
 suspension=np.exp(-offshore/10)*(.70+.18*n2+.10*n3)
 rwater+=suspension[...,None]*[.16,.07,.025]
 ironmix=smooth((20-radius)/3)*redwater
 c=c*(1-ironmix[...,None])+rwater*ironmix[...,None]
 # Polar pack in spherical coordinates has branching leads and a ragged seasonal edge.
 edge=74+1.2*n1+.7*n2
 amount=smooth((lat-edge)/3.2)*(~land)
 # Unequal polygonal floes with intermittent narrow leads, rather than wavy contour loops.
 seeds=rng.normal(size=(250,3));seeds[:,2]=abs(seeds[:,2])+2.2
 seeds/=np.linalg.norm(seeds,axis=1)[:,None]
 roi=lat>68;query=np.stack([q[roi] for q in xyz],-1)
 distances,_=cKDTree(seeds).query(query,k=2)
 leads=np.zeros((H,W),dtype='f');leads[roi]=np.exp(-((distances[:,1]-distances[:,0])/.0015)**2)
 leads*=smooth((n2+.5)/1.1)
 icepack=np.zeros_like(c)+[.68,.77,.80];icepack+=(.02*n2+.01*n4)[...,None]
 amount*=.94-.32*leads;c=c*(1-amount[...,None])+icepack*amount[...,None]
 aquatic=allriver|small|lake;depth=distance_transform_edt(aquatic)
 water=np.zeros_like(c)+[.025,.125,.155];water+=np.exp(-depth/2.5)[...,None]*[.01,.022,.01]
 c[aquatic]=water[aquatic]
 # Modest sediment fans where the actual mountain feeder reaches the reservoir and at the Seattle estuary.
 for name,spread in [('mountains_to_lake',.5),('lake_to_seattle_to_ocean',.65)]:
  p=curves[name][-1];v=curves[name][-1]-curves[name][-25];v=v/np.linalg.norm(v)
  dx=lon-p[0];dy=lat-p[1];along=dx*v[0]+dy*v[1];across=-dx*v[1]+dy*v[0]
  plume=np.exp(-((along-.35)/spread)**2-(across/(.16+.3*np.maximum(along,0)))**2)*.27
  plume*=((lake if name=='mountains_to_lake' else ~land)&(along>0))
  c=c*(1-plume[...,None])+np.array([.17,.24,.18])*plume[...,None]
 aa=gaussian_filter(aquatic.astype('f'),.4);edge=(aa>.01)&~aquatic&land
 c[edge]=c[edge]*(1-aa[edge,None]) + water[edge]*aa[edge,None]
 # Physical data remains distinct from the deliberately readable satellite-style surface.
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 z['surface'][allriver]=waterfield[allriver];z['surface'][lake]=690
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 maps={'albedo_4096.png':np.uint8(np.clip(c,0,1)*255),'height_16bit.png':np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535),'land_mask.png':np.uint8(land)*255,'roughness.png':np.uint8(np.where(aquatic,.34,np.where(land,.88,.39))*255)}
 for name,a in maps.items():Image.fromarray(a).save(B/'textures'/name)
 p=json.load(open(B/'source/planet.json'));p.update(revision=8,r8=dict(method='Bounded DEM relief, graded river bends, regionally continuous materials, irregular lake basins, altitude and exposure controlled snow',scope='Art-directed physical geography; not a numerical climate or erosion simulation',archipelago_retained_islands=5));json.dump(p,open(B/'source/planet.json','w'),indent=2)
 json.dump(dict(revision=8,small_lakes=records,coastline_changes='Local polar-edge relaxation only; approved continental layout retained',terrain='Replaced reflected DEM patterns and old trenches; bounded relief coordinates and subdued lowlands'),open(B/'source/Natural_Landforms_Revision.json','w'),indent=2)
 print('R8 TERRAIN COMPLETE',flush=True)
if __name__=='__main__':revise(Path(__file__).resolve().parents[1])
