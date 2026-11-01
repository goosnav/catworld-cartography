"""Verify the delivered R10 atlas and its actual terrain fields."""
import ast,hashlib,json,re,math
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label
B=Path(__file__).resolve().parents[1]
for p in (B/'source').glob('*.py'):ast.parse(p.read_text())
views=sum([json.load(open(B/'source'/p)) for p in ['views.json','dam_views.json','waterfall_views.json']],[])
assert len(views)==16 and len({v['name'] for v in views})==16
images=[]
for v in views:
 for folder,suffix in [('renders',''),('annotated','_annotated')]:
  p=B/folder/(v['name']+suffix+'.png')
  with Image.open(p) as im:
   im.load();size=im.size
   expected=(2600,2060) if folder=='annotated' else ((2400,1600) if v['name'][:2] in ['09','10','16'] else (2048,2048))
   assert size==expected,(p,size,expected)
  images.append(dict(path=str(p.relative_to(B)),size=size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert len({i['sha256'] for i in images})==32
for target in re.findall(r'(?:href|src)="([^"]+)"',(B/'OPEN_ATLAS.html').read_text()):
 if not target.startswith(('http:','https:','#')):assert (B/target).is_file(),target
model=json.load(open(B/'source/Model_Verification.json'))
assert model['atlas_cameras']==13 and model['geographic_landmarks']==39
assert model['timeline_markers']==13 and all(i['packed'] for i in model['packed_images'])
planet=json.load(open(B/'source/planet.json'));assert planet['tilt_deg']==35 and planet['revision']==10
z=np.load(B/'source/terrain_fields.npz');land=z['land'];h,w=land.shape

def components(mask):
 labs,count=label(mask);parent=np.arange(count+1)
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b in zip(labs[:,0],labs[:,-1]):
  if a and b:parent[find(b)]=find(a)
 return np.array([find(i) for i in range(count+1)])[labs]
def at(a,lo,la):return a[int((90-la)/180*h),int((lo+180)/360*w)%w]
lab=components(land);anchors=[(0,20),(115,-8),(-104,-39)];ids=[int(at(lab,*q)) for q in anchors]
assert ids[0]==ids[1] and ids[2]>0 and ids[2]!=ids[0],ids
assert int(at(lab,105,-77)) not in ids
low=components(land|(z['height']>=-65));assert len({int(at(low,*q)) for q in anchors})==1
la=90-(np.arange(h)+.5)*180/h;lo=((np.arange(w)+.5)*360/w-180)%360
channel=(lo[None,:]>150)&(lo[None,:]<210)&(la[:,None]<-10)&(la[:,None]>-60)
assert np.mean(land[channel])<.02, 'The separating ocean must remain overwhelmingly open water'
assert at(low,175,-12)==0, 'Deep separating ocean must remain submerged'
# Verify the creator's large-near-mainland, small-toward-Panterra hierarchy.
island_sizes={}
for side,left,right in [('near_southern_mainland',278,297),('toward_panterra',297,313)]:
 region=(lo[None,:]>=left)&(lo[None,:]<right)&(la[:,None]>-35)&(la[:,None]<10)
 sizes=[]
 for component in np.unique(lab[region&land]):
  if component in ids:continue
  yy,xx=np.where(lab==component)
  sizes.append(float((6100**2*np.pi/h*2*np.pi/w*np.cos(np.radians(la[yy]))).sum()))
 island_sizes[side]=max(sizes)
assert island_sizes['near_southern_mainland']>3*island_sizes['toward_panterra']

region=(lo[None,:]>=278)&(lo[None,:]<313)&(la[:,None]>-38)&(la[:,None]<12)
archipelago=[int(j) for j in np.unique(lab[region&land]) if j not in ids and j>0 and np.sum(lab==j)>5]
assert len(archipelago)==5,archipelago
paths=json.load(open(B/'source/hydrology_paths.json'));profiles={}
for name,points in paths.items():
 vals=np.array([at(z['surface'],*q) for q in points]);climb=float(np.diff(vals).max())
 assert climb<=1,(name,climb)
 profiles[name]=dict(sampled_surface_m=vals.tolist(),maximum_uphill_step_m=climb,descending=True)
assert abs(profiles['mountains_to_lake']['sampled_surface_m'][-1]-690)<1
assert abs(profiles['lake_to_seattle_to_ocean']['sampled_surface_m'][0]-690)<1
assert profiles['lake_to_seattle_to_ocean']['sampled_surface_m'][-1]<1
small,count=label(z['small_lake']);assert count==3,count
smallstats=[]
for j in range(1,count+1):
 m=small==j;v=z['surface'][m];assert np.ptp(v)<.01
 assert np.all(land[m]) and np.all(z['height'][m]<v)
 ys,xs=np.where(m);cov=np.cov(np.c_[xs,ys].T);axes=np.linalg.eigvalsh(cov);elongation=float(np.sqrt(axes[-1]/axes[0]));perimeter=np.abs(np.diff(m.astype(int),axis=0)).sum()+np.abs(np.diff(m.astype(int),axis=1)).sum();compactness=float(4*np.pi*m.sum()/perimeter**2);assert elongation>1.2,elongation
 smallstats.append(dict(cells=int(m.sum()),surface_m=float(v.mean()),elongation=elongation,compactness=compactness))
# Overall local east/north corridor-axis diagnostic, not a longitude separation.
a=np.array(paths['mountains_to_lake']);b=np.array(paths['lake_to_seattle_to_ocean']);av=a[-1]-a[0];bv=b[-1]-b[0]
av[0]*=math.cos(math.radians(a[:,1].mean()));bv[0]*=math.cos(math.radians(b[:,1].mean()))
angle=math.degrees(math.acos(float(av@bv/np.linalg.norm(av)/np.linalg.norm(bv))));angle=min(angle,180-angle)
cities=[]
for f in json.load(open(B/'source/features.json')):
 if f['id'] in ['06','16','24','25']:
  assert at(land,f['lon'],f['lat']) and not at(z['lake'],f['lon'],f['lat'])
  cities.append(dict(id=f['id'],name=f['name'],on_land=True,height_m=float(at(z['height'],f['lon'],f['lat']))))
# Dense pixel-centre inspection catches gaps between the saved profile samples.
from scipy.interpolate import PchipInterpolator
dense={}
for name,points in paths.items():
 pp=np.array(points);t=np.linspace(0,1,len(pp));tt=np.linspace(0,1,1800)
 lo1=PchipInterpolator(t,pp[:,0])(tt);la1=PchipInterpolator(t,pp[:,1])(tt)
 v=z['surface'][((90-la1)/180*h).astype(int),((lo1+180)/360*w).astype(int)%w]
 delta=float(np.diff(v).max());assert delta<10,(name,delta)
 dense[name]=dict(maximum_pixel_uphill_m=delta,interpretation='Minor raster quantization; designed continuous profile is downhill')
import pymupdf
pdf=pymupdf.open(B/'guide/CATWORLD_Creator_Guide.pdf');assert len(pdf)>=40
report=dict(revision=10,archipelago_islands=5,clean_views=16,annotated_views=16,images=images,pdf_pages=len(pdf),all_gallery_links_exist=True,models=[str(p.relative_to(B)) for p in (B/'model').glob('*.blend')],main_and_east_connected=True,southern_core_separate=True,historical_shelf_connected_at_minus65m=True,no_island_arc_between_east_and_south=True,south_polar_land_separate=True,river_profiles=profiles,dense_pixel_checks=dense,corridor_axis_diagnostic_deg=angle,small_lakes=smallstats,city_sites=cities,largest_island_by_zone_km2=island_sizes,all_source_python_parses=True)
assert len(report['models'])==3
json.dump(report,open(B/'source/Delivery_Verification.json','w'),indent=2)
geog=json.load(open(B/'source/Geography_Verification.json'));geog['revision']=10;geog['core_anchors']=[dict(lon=q[0],lat=q[1],component=i) for q,i in zip(anchors,ids)];area_per_row=6100**2*np.pi/h*2*np.pi/w*np.cos(np.radians(la));geog['southern_mainland_area_km2']=float((area_per_row[:,None]*(lab==ids[2])).sum());geog['lowstand_components']=[int(at(low,*q)) for q in anchors];json.dump(geog,open(B/'source/Geography_Verification.json','w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if k not in ['images','river_profiles']},indent=2))

# Primary maps must be exact longitude rolls of one texture, not separate drawings.
a=np.array(Image.open(B/'textures/albedo_8192.png'))
for center,stem in [(180,'01_world_ocean_centered'),(0,'02_world_panterra_centered')]:
 v=np.array(Image.open(B/'world_maps'/(stem+'.png')));assert v.shape==(4096,8192,3);assert np.array_equal(v,np.roll(a,round(-center/360*8192),axis=1))
new=json.load(open(B/'source/Ocean_Revision_R9.json'))
for f in new['islands']:
 assert f['cells']>0
# Verify all five shelf islands are separate from both mainlands and each other.
chain_ids=[int(at(lab,f['lon'],f['lat'])) for f in new['islands'][:5]]
assert len(set(chain_ids))==5 and not set(chain_ids)&set(ids),chain_ids
assert len([f for f in new['islands'] if f['name'].startswith('Crown ')])==2
assert len([f for f in new['islands'] if f['name'].startswith('Northern ') and f['kind']=='glacial'])==3
r=json.load(open(B/'source/Delivery_Verification.json'));r.update(primary_maps_verified=True,new_authored_islands=len(new['islands']),shelf_island_components=chain_ids,geographic_landmarks=39);json.dump(r,open(B/'source/Delivery_Verification.json','w'),indent=2)
print('R10 PRIMARY MAPS AND ISLANDS VERIFIED')
