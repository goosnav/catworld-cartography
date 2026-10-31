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
z=np.load(B/'source/terrain_fields.npz');land=z['land'];h,w=land.shape;shift=w*3//4;lab,n=label(np.roll(land,shift,axis=1))
anchors=[(0,20),(150,5),(-140,-30)]
ids=[int(lab[int((90-la)/180*h),(int((lo+180)/360*w)+shift)%w]) for lo,la in anchors]
assert len(set(ids))==1 and ids[0]>0
assert int(lab[-3,w//2])!=ids[0]
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
pdf=pymupdf.open(B/'guide/CATWORLD_Geography_Atlas.pdf')
assert len(pdf)>=20
report={'revision':2,'clean_views':14,'annotated_views':14,'images':images,'pdf_pages':len(pdf),'all_gallery_links_exist':True,'models':[str(p.relative_to(B)) for p in (B/'model').glob('*.blend')],'three_cores_connected':True,'south_polar_land_separate':True,'main_river_sampled_surface_m':v.tolist(),'main_river_sampled_direction_descending':True,'dam_outlet_sampled_surface_m':ov.tolist(),'dam_outlet_sampled_direction_descending':True,'city_sites':cities,'all_source_python_parses':True}
json.dump(report,open(B/'source/Delivery_Verification.json','w'),indent=2)
print(json.dumps({k:v for k,v in report.items() if k!='images'},indent=2))
