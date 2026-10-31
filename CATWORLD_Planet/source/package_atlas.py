import json, csv, math, textwrap, re, html, shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,Image as RImage,Table,TableStyle,KeepTogether
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
B=Path(__file__).resolve().parents[1]
F='/System/Library/Fonts/Supplemental/Arial.ttf';FB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
def font(s,b=False):return ImageFont.truetype(FB if b else F,s)
views=json.load(open(B/'source/views.json'));views+=json.load(open(B/'source/dam_views.json'))
views.sort(key=lambda x:x['name'])
select={'01':['01','02','03','04','05','06','07','08','16'],'02':['01','02','09','10','18','19','22'],'03':['07','08','11','12','13','15','20','21'],'04':['11','12','18','19','21','23'],'05':['01','02','08','09','10','23'],'06':['11','12','13','16','17','18','20'],'07':['02','03','04','05','06','07','14','15','16','17'],'08':['01','02','09'],'11':['11','12','13','20','21'],'12':['10','18','19','22']}
titles={'01':'PANTERRA / FRONT HEMISPHERE','02':'EASTERN HEMISPHERE','03':'WESTERN HEMISPHERE','04':'FAR-SIDE HEMISPHERE','05':'NORTH POLAR VIEW','06':'SOUTH POLAR VIEW','07':'PANTERRA / REGIONAL STUDY','08':'NORTHERN IMPACT BASIN','09':'GREAT DAM / VALLEY CONTEXT','10':'GREAT DAM / STRUCTURAL STUDY','11':'SOUTHERN CONTINENT','12':'EASTERN CONTINENT'}
for v in views:
 name=v['name'];idx=name[:2];im=Image.open(B/'renders'/f'{name}.png').convert('RGBA');im.thumbnail((1800,1800))
 out=Image.new('RGB',(2600,2060),'#10191f');d=ImageDraw.Draw(out);offx=(1860-im.width)//2;offy=155+(1800-im.height)//2;out.paste(im,(offx,offy),im)
 d.text((55,40),'CATWORLD  /  '+titles[idx],font=font(42,True),fill='#f2ead8')
 sub='Local engineering concept · 1 unit = 1 km' if idx in ['09','10'] else f"View center {v['latitude']:.0f}° latitude / {v['longitude']:.0f}° longitude · relief 5×"
 d.text((55,100),sub,font=font(25),fill='#93acb7');d.line((1900,160,1900,1920),fill='#35505b',width=2)
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
d.text((40,30),'CATWORLD / PLANET REFERENCE ATLAS',font=font(48,True),fill='#f2ead8');d.text((40,95),'One globe · every hemisphere · two regional continents · crater and dam studies',font=font(25),fill='#9bb2be')
for i,v in enumerate(views):
 im=Image.open(B/'renders'/f"{v['name']}.png").convert('RGBA');im.thumbnail((690,680));x=(i%cols)*cw;y=(i//cols)*ch+160;cs.paste(im,(x+(cw-im.width)//2,y+(680-im.height)//2),im)
 d.text((x+25,y+705),titles[v['name'][:2]],font=font(23,True),fill='#f2ead8')
cs.save(B/'CATWORLD_Contact_Sheet.jpg',quality=93)
# Catalogue and statistics.
features=json.load(open(B/'source/features.json'))
with open(B/'guide/Landmark_Catalogue.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=['id','name','lon','lat','description']);w.writeheader();w.writerows({k:v for k,v in ff.items() if k!='sketch_xy'} for ff in features)
a=np.load(B/'source/terrain_fields.npz');h,w=a['land'].shape;la=90-(np.arange(h)+.5)*180/h;area=6100**2*(np.pi/h)*(2*np.pi/w)*np.cos(np.radians(la))[:,None]
stats={'land_area_km2':float((a['land']*area).sum()),'reservoir_area_km2':float((a['lake']*area).sum()),'peak_m':float(a['height'].max()),'radius_km':6100}
json.dump(stats,open(B/'source/statistics.json','w'),indent=2)
# Offline gallery is a file index, not an external service.
items='\n'.join(f'''<figure><a href="renders/{v['name']}.png"><img src="renders/{v['name']}.png" alt="{titles[v['name'][:2]]}"></a><figcaption>{titles[v['name'][:2]]} · <a href="annotated/{v['name']}_annotated.png">Annotations</a></figcaption></figure>''' for v in views)
(B/'OPEN_ATLAS.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><title>Catworld / Planet Atlas</title><style>body{background:#10191f;color:#e8e0d1;font:17px/1.5 system-ui;margin:40px}a{color:#a8d4dd}h1{letter-spacing:.06em}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:25px}figure{margin:0}img{width:100%;aspect-ratio:1;object-fit:contain}figcaption{padding:10px 0}p{max-width:900px}</style><h1>CATWORLD / TERRA</h1><p>Cloud-free references from one editable Blender globe. Click a view for the full-resolution PNG. The redline versions locate the landmarks. Radius 6,100 km; 23.4° tilt; 4,000 Earth years per orbit.</p><p><a href="guide/CATWORLD_Geography_Atlas.pdf">Illustrated geography guide</a> · <a href="model/CATWORLD_Terra.blend">Globe model</a> · <a href="model/CATWORLD_Dam_Study.blend">Dam study</a> · <a href="guide/Landmark_Catalogue.csv">Landmarks</a></p><main>'''+items+'</main></html>')
# PDF guide, readable prose followed by reference plates.
styles=getSampleStyleSheet();styles.add(ParagraphStyle(name='BodyCustom',fontName='Helvetica',fontSize=10.5,leading=15,spaceAfter=9,textColor=colors.HexColor('#26353b')));styles['Heading1'].textColor=colors.HexColor('#133e47');styles['Heading1'].fontSize=23;styles['Heading1'].keepWithNext=1;styles['Heading2'].keepWithNext=1;styles['Heading2'].fontSize=16;styles['Heading2'].spaceBefore=17;styles['Heading3'].fontSize=12;styles['Heading3'].spaceBefore=13
story=[]
md=(B/'guide/Geography_and_Design.md').read_text()
for para in re.split(r'\n\s*\n',md):
 if para.startswith('# '):style=styles['Title'];txt=para[2:]
 elif para.startswith('## '):style=styles['Heading1'];txt=para[3:]
 elif para.startswith('### '):style=styles['Heading2'];txt=para[4:]
 else:style=styles['BodyCustom'];txt=para
 txt=html.escape(txt).replace('`','').replace('\n','<br/>')
 txt=re.sub(r'(https://[^\s<]+)',lambda m:f'<link href="{m.group(1)}" color="#217081">{m.group(1)}</link>',txt)
 story.append(Paragraph(txt,style))
story.append(PageBreak());story.append(Paragraph('Tectonic framework',styles['Heading1']));story.append(RImage(str(B/'guide/Tectonic_Framework.png'),width=500,height=375));story.append(Spacer(1,15));story.append(Paragraph('The orange belt marks convergence. Blue lines identify proposed rifts. The impact basin predates this collision system. See the full-resolution PNG for the complete diagram.',styles['BodyCustom']));story.append(PageBreak());story.append(Paragraph('Landmark coordinates',styles['Heading1']))
for f in features:story.append(Paragraph(f"<b>{f['id']} / {html.escape(f['name'])}</b> — {f['lat']:.2f} latitude, {f['lon']:.2f} longitude<br/>{html.escape(f['description'])}",styles['BodyCustom']))
for v in views:
 story.append(PageBreak());story.append(Paragraph(titles[v['name'][:2]],styles['Heading1']));story.append(Spacer(1,12))
 im=B/'annotated'/f"{v['name']}_annotated.png";story.append(RImage(str(im),width=500,height=500*2060/2600));story.append(Spacer(1,15));story.append(Paragraph('Use the full-resolution PNG for detailed drawing. This page is an index and orientation reference. All numbered plates refer to the same editable geographic model; dam plates are a separate local inset.',styles['BodyCustom']))
def footer(c,d):
 c.saveState();c.setStrokeColor(colors.HexColor('#b7c6cb'));c.line(45,39,A4[0]-45,39);c.setFont('Helvetica',8);c.setFillColor(colors.HexColor('#5a737f'));c.drawString(45,26,'CATWORLD / GEOGRAPHY & DRAWING REFERENCE');c.drawRightString(A4[0]-45,26,str(d.page));c.restoreState()
doc=SimpleDocTemplate(str(B/'guide/CATWORLD_Geography_Atlas.pdf'),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=45,bottomMargin=55);doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('PACKAGED',len(views),'views',stats)
