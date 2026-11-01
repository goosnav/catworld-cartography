import json, csv, math, textwrap, re, html, shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image as RImage,Table,TableStyle,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
B=Path(__file__).resolve().parents[1]
F='/System/Library/Fonts/Supplemental/Arial.ttf';FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(s,b=False):return ImageFont.truetype(FB if b else F,s)
views=json.load(open(B/'source/views.json'));views+=json.load(open(B/'source/dam_views.json'))
views.sort(key=lambda x:x['name'])
select={'01': ['01', '02', '03', '04', '05', '06', '07', '24', '16', '25'], '02': ['02', '10', '18', '19', '22', '26'], '03': ['07', '08', '11', '12', '13', '20', '21', '24', '27'], '04': ['11', '12', '18', '19', '21', '26', '27', '23'], '05': ['01', '02', '09', '10', '23', '28'], '06': ['11', '12', '13', '17', '29', '30'], '07': ['02', '03', '04', '05', '06', '07', '16', '24', '25'], '08': ['01', '02', '09', '28'], '11': ['11', '12', '20', '21', '26', '27'], '12': ['10', '18', '19', '22', '26'], '13': ['04', '07', '24', '16', '25'], '14': ['11', '12', '13', '20', '27']}
titles={'01':'PANTERRA / FRONT HEMISPHERE','02':'EASTERN HEMISPHERE','03':'WESTERN HEMISPHERE','04':'FAR-SIDE HEMISPHERE','05':'NORTH POLAR VIEW','06':'SOUTH POLAR VIEW','07':'PANTERRA / REGIONAL STUDY','08':'NORTHERN IMPACT BASIN','09':'GREAT DAM / VALLEY CONTEXT','10':'GREAT DAM / STRUCTURAL STUDY','11':'SOUTHERN CONTINENT','12':'EASTERN CONTINENT','13':'SEATTLE / PRIMARY WATERWAY','14':'EASTERN ARCHIPELAGO'}
for v in views:
 name=v['name'];idx=name[:2];im=Image.open(B/'renders'/f'{name}.png').convert('RGBA');im.thumbnail((1800,1800))
 out=Image.new('RGB',(2600,2060),'#10191f');d=ImageDraw.Draw(out);offx=(1860-im.width)//2;offy=155+(1800-im.height)//2;out.paste(im,(offx,offy),im)
 d.text((55,40),'CATWORLD  /  '+titles[idx],font=font(42,True),fill='#f2ead8')
 sub='Local engineering concept · 1 unit = 1 km' if idx in ['09','10'] else f"View center {v['latitude']:.0f}° latitude / {v['longitude']:.0f}° longitude · relief 10×"
 d.text((55,100),sub,font=font(25),fill='#93acb7');d.line((1900,160,1900,1920),fill='#35505b',width=2)
 if idx in ['07','13']:
  for points in v.get('flowpaths',{}).values():
   for j in range(2,len(points),2):
    a,b=points[j-1],points[j]
    if not all(.02<t<.98 for t in a+b):continue
    x,y=offx+b[0]*im.width,offy+b[1]*im.height
    ang=math.atan2(b[1]-a[1],b[0]-a[0]);length=18
    d.line([(x-length*math.cos(ang-.5),y-length*math.sin(ang-.5)),(x,y),(x-length*math.cos(ang+.5),y-length*math.sin(ang+.5))],fill='#ffbc8b',width=4)
  d.text((55,1930),'FLOW: SEATTLE → SUPER-LAKE → DAM → DOWNSTREAM CITY',font=font(23,True),fill='#ffbc8b')
 ff=[f for f in v['features'] if f['visible'] and (idx not in select or f['id'] in select[idx])]
 yy=190
 for f in ff:
  x=offx+f['x']*im.width;y=offy+f['y']*im.height
  d.ellipse((x-20,y-20,x+20,y+20),fill='#d55748',outline='#ffdfc4',width=2)
  box=d.textbbox((0,0),f['id'],font=font(21,True));d.text((x-(box[2]-box[0])/2,y-13),f['id'],font=font(21,True),fill='white')
  d.text((1950,yy),f['id'],font=font(26,True),fill='#ef8c75')
  text=f['name'];lines=textwrap.wrap(text,width=31)
  for k,line in enumerate(lines):d.text((2010,yy+k*30),line,font=font(25,True),fill='#f2ead8')
  yy+=len(lines)*30+12
  if f.get('description'):
   for line in textwrap.wrap(f['description'],width=43):d.text((2010,yy),line,font=font(21),fill='#a9bdc6');yy+=26
  yy+=27
 d.text((55,1985),'ANNOTATED REFERENCE   /   Proposed geography · 31 OCT 2026',font=font(24),fill='#93acb7')
 d.text((1950,1900),'Numbers locate features.',font=font(23),fill='#a9bdc6');d.text((1950,1932),'Markers are not to scale.',font=font(23),fill='#a9bdc6')
 out.save(B/'annotated'/f'{name}_annotated.png')
# Whole-set contact sheet, with no omitted hemisphere.
cols=4;cw=720;ch=780;rows=math.ceil(len(views)/cols)
cs=Image.new('RGB',(cols*cw,rows*ch+160),'#10191f');d=ImageDraw.Draw(cs)
d.text((40,30),'CATWORLD / PLANET REFERENCE ATLAS',font=font(48,True),fill='#f2ead8');d.text((40,95),'Two connected cores · separate southern continent · northern autumn / southern spring',font=font(25),fill='#9bb2be')
for i,v in enumerate(views):
 im=Image.open(B/'renders'/f"{v['name']}.png").convert('RGBA');im.thumbnail((690,680));x=(i%cols)*cw;y=(i//cols)*ch+160;cs.paste(im,(x+(cw-im.width)//2,y+(680-im.height)//2),im)
 d.text((x+25,y+705),titles[v['name'][:2]],font=font(23,True),fill='#f2ead8')
cs.save(B/'CATWORLD_Contact_Sheet.jpg',quality=93)
# Catalogue and statistics.
features=json.load(open(B/'source/features.json'))
with open(B/'guide/Landmark_Catalogue.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=['id','name','lon','lat','description'],lineterminator='\n');w.writeheader();w.writerows({k:v for k,v in ff.items() if k!='sketch_xy'} for ff in features)
a=np.load(B/'source/terrain_fields.npz');h,w=a['land'].shape;la=90-(np.arange(h)+.5)*180/h;area=6100**2*(np.pi/h)*(2*np.pi/w)*np.cos(np.radians(la))[:,None]
stats={'land_area_km2':float((a['land']*area).sum()),'reservoir_area_km2':float((a['lake']*area).sum()),'peak_m':float(a['height'].max()),'radius_km':6100}
json.dump(stats,open(B/'source/statistics.json','w'),indent=2)
# Offline gallery is a file index, not an external service.
items='\n'.join(f'''<figure><a href="renders/{v['name']}.png"><img src="renders/{v['name']}.png" alt="{titles[v['name'][:2]]}"></a><figcaption>{titles[v['name'][:2]]} · <a href="annotated/{v['name']}_annotated.png">Annotations</a></figcaption></figure>''' for v in views)
(B/'OPEN_ATLAS.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Catworld / Planet Atlas</title><style>body{background:#10191f;color:#e8e0d1;font:17px/1.5 system-ui;margin:40px}a{color:#a8d4dd}h1{letter-spacing:.06em}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:25px}figure{margin:0}img{width:100%;aspect-ratio:1;object-fit:contain}figcaption{padding:10px 0}p{max-width:900px}</style><h1>CATWORLD / TERRA — REVISION 5</h1><p>Cloud-free references from one editable Blender globe. Click a view for the full-resolution PNG. The redline versions locate the landmarks. Radius 6,100 km; 23.4° tilt; 4,000 Earth years per orbit.</p><p><a href="guide/CATWORLD_Creator_Guide.pdf">Creator / showrunner guide</a> · <a href="model/CATWORLD_Terra.blend">Globe model</a> · <a href="model/CATWORLD_Dam_Study.blend">Dam study</a> · <a href="guide/Landmark_Catalogue.csv">Landmarks</a> · <a href="guide/Tectonic_Framework.png">Tectonic framework</a> · <a href="guide/Revision_Comparison.jpg">Before / after</a></p><main>'''+items+'</main></html>')
