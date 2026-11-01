"""Check the delivered atlas, geographic connectivity and primary flow direction."""
import ast, hashlib, json, re
from pathlib import Path
import numpy as np
from PIL import Image
from scipy.ndimage import label
B=Path(__file__).resolve().parents[1]
for p in (B/'source').glob('*.py'):ast.parse(p.read_text())
views=json.load(open(B/'source/views.json'))+json.load(open(B/'source/dam_views.json'))
assert len(views)==14
images=[]
for v in views:
 for folder,suffix in [('renders',''),('annotated','_annotated')]:
  p=B/folder/(v['name']+suffix+'.png')
  with Image.open(p) as im:
   im.load();size=im.size
   expected=(2600,2060) if folder=='annotated' else ((2400,1600) if v['name'][:2] in ['09','10'] else (2048,2048))
   assert size==expected,(p,size,expected)
  images.append({'path':str(p.relative_to(B)),'size':size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
assert len(set(i['sha256'] for i in images))==28
for target in re.findall(r'(?:href|src)="([^"]+)"',(B/'OPEN_ATLAS.html').read_text()):
 if not target.startswith(('http:','https:','#')):assert (B/target).is_file(),target
model=json.load(open(B/'source/Model_Verification.json'));assert model['atlas_cameras']==12 and model['geographic_landmarks']==30
assert all(i['packed'] for i in model['packed_images'])
z=np.load(B/'source/terrain_fields.npz');land=z['land'];h,w=land.shape
# Merge the longitude seam before checking continental connectivity.
def components(mask):
 labs,count=label(mask);parent=np.arange(count+1)
 def find(i):
  while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
  return i
 for a,b in zip(labs[:,0],labs[:,-1]):
  if a and b:parent[find(b)]=find(a)
 return np.array([find(i) for i in range(count+1)])[labs]
def at(a,lo,la):return int(a[int((90-la)/180*h),int((lo+180)/360*w)%w])
lab=components(land);anchors=[(0,20),(120,5),(-160,-30)];ids=[at(lab,*q) for q in anchors]
assert ids[0]==ids[1] and ids[2]>0 and ids[2]!=ids[0]
assert at(lab,105,-77) not in ids
low=components(land|(z['height']>=-65));assert len(set(at(low,*q) for q in anchors))==1
la=90-(np.arange(h)+.5)*180/h;lo=((np.arange(w)+.5)*360/w-180)%360
channel=(lo[None,:]>85)&(lo[None,:]<171)&(la[:,None]<-18)&(la[:,None]>-60)
assert not np.any(channel&land&(lab!=ids[0]))
geography=json.load(open(B/'source/Geography_Verification.json'))
p=np.array(json.load(open(B/'source/hydrology_paths.json'))['seattle_to_lake']);x=((p[:,0]+180)/360*w).astype(int)%w;y=np.clip(((90-p[:,1])/180*h).astype(int),0,h-1);v=z['surface'][y,x]
assert np.all(np.diff(v)<=1) and abs(float(v[-1])-690)<1
q=np.array(json.load(open(B/'source/hydrology_paths.json'))['dam_to_city']);ov=z['surface'][np.clip(((90-q[:,1])/180*h).astype(int),0,h-1),((q[:,0]+180)/360*w).astype(int)%w]
assert np.all(np.diff(ov)<=1)
cities=[]
for f in json.load(open(B/'source/features.json')):
 if f['id'] in ['06','16','24','25']:
  y=int((90-f['lat'])/180*h);x=int((f['lon']+180)/360*w)
  assert land[y,x] and not z['lake'][y,x]
  cities.append({'id':f['id'],'name':f['name'],'on_land':True,'height_m':float(z['height'][y,x])})
import pymupdf
pdf=pymupdf.open(B/'guide/CATWORLD_Creator_Guide.pdf')
assert len(pdf)>=20
report={'revision':5,'clean_views':14,'annotated_views':14,'images':images,'pdf_pages':len(pdf),'all_gallery_links_exist':True,'models':[str(p.relative_to(B)) for p in (B/'model').glob('*.blend')],'main_and_east_connected':True,'southern_core_separate':True,'historical_shelf_connected_at_minus65m':True,'no_island_arc_between_east_and_south':True,'south_polar_land_separate':True,'main_river_sampled_surface_m':v.tolist(),'main_river_sampled_direction_descending':True,'dam_outlet_sampled_surface_m':ov.tolist(),'dam_outlet_sampled_direction_descending':True,'city_sites':cities,'all_source_python_parses':True}
json.dump(report,open(B/'source/Delivery_Verification.json','w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='images'},indent=2))
