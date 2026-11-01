"""Build an illustrated, bookmarked creator guide with a complete vector-labelled atlas."""
from pathlib import Path
import json,math,html,re,hashlib,sys,tempfile
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from creator_content import SECTIONS,SOURCES
B=Path(__file__).resolve().parents[1];G=B/'guide';W,H=A4;M=46;CW=W-2*M
INK='#18333f';GRAY='#62787b';TEAL='#247f86';BG='#f6f2e9';DARK='#10191f';RED='#c35f49'
for name,file in [('Guide','Arial.ttf'),('GuideBold','Arial Bold.ttf')]:pdfmetrics.registerFont(TTFont(name,'/System/Library/Fonts/Supplemental/'+file))
pdfmetrics.registerFontFamily('Guide',normal='Guide',bold='GuideBold',italic='Guide',boldItalic='GuideBold')
CACHE=Path(sys.argv[1]) if len(sys.argv)>1 else Path(tempfile.mkdtemp(prefix='catworld-pdf-'));CACHE.mkdir(parents=True,exist_ok=True)
P=G/'CATWORLD_Creator_Guide.pdf';c=canvas.Canvas(str(P),pagesize=A4,pageCompression=1);c.setTitle('Catworld / Terra - Creator and Showrunner World Guide - Revision 6');c.setAuthor('Catworld cartography development');page=0;layout=[]
def para(text,x,y,width=CW,size=10.5,leading=14.5,bold=False,col=INK):
 st=ParagraphStyle('p',fontName='GuideBold' if bold else 'Guide',fontSize=size,leading=leading,textColor=HexColor(col),splitLongWords=True)
 q=Paragraph(text,st);ww,hh=q.wrap(width,1000);q.drawOn(c,x,y-hh);return y-hh

def start(title,kicker='CATWORLD / WORLD MODEL',key=None):
 global page
 page+=1;c.setFillColor(HexColor(BG));c.rect(0,0,W,H,fill=1,stroke=0)
 c.setFillColor(HexColor(TEAL));c.setFont('GuideBold',8.5);c.drawString(M,H-36,kicker)
 y=para(html.escape(title),M,H-60,size=24,leading=28,bold=True)
 c.setStrokeColor(HexColor('#cbd3cc'));c.line(M,40,W-M,40);c.setFont('Guide',8);c.setFillColor(HexColor(GRAY));c.drawString(M,27,'CATWORLD / CREATOR GUIDE / R6');c.drawRightString(W-M,27,str(page))
 if key:c.bookmarkPage(key);c.addOutlineEntry(title,key,level=0,closed=False)
 return y-18

def image(path,x,y,w,h,dark=False):
 path=Path(path)
 if path.parent.name=='renders':
  cached=CACHE/(path.stem+'.jpg')
  if not cached.exists() or cached.stat().st_mtime<path.stat().st_mtime:
   pic=Image.open(path).convert('RGBA');flat=Image.new('RGB',pic.size,DARK);flat.paste(pic,mask=pic.getchannel('A'));flat.thumbnail((1600,1600),Image.Resampling.LANCZOS);flat.save(cached,quality=91,subsampling=0,optimize=True)
  path=cached
 if dark:c.setFillColor(HexColor(DARK));c.rect(x,y-h,w,h,fill=1,stroke=0)
 c.drawImage(str(path),x,y-h,width=w,height=h,preserveAspectRatio=True,anchor='c',mask='auto')

def figure(name,y,maxh=290):
 if name in ['overview','poles']:
  names=['01_panterra','04_far_side'] if name=='overview' else ['05_north_pole','06_south_pole'];fw=(CW-12)/2;fh=fw
  for j,n in enumerate(names):image(B/'renders'/f'{n}.png',M+j*(fw+12),y,fw,fh,True)
  y-=fh+7
  for j,label in enumerate(['PANTERRA / FRONT','FAR-SIDE HEMISPHERE'] if name=='overview' else ['NORTH / OCEAN + ISLANDS','SOUTH / ICE CONTINENT']):para(label,M+j*(fw+12),y,width=fw,size=8.5,leading=11,bold=True)
  return y-25
 p=B/name;i=Image.open(p);ratio=i.width/i.height
 fw=min(CW,maxh*ratio);fh=fw/ratio
 image(p,M+(CW-fw)/2,y,fw,fh,name.startswith('renders/'))
 return y-fh-16

def textblocks(paras,y,size=10.5):
 for title,body in paras:
  y=para(html.escape(title),M,y,size=size+.5,leading=15,bold=True)-4
  text=html.escape(body)
  text=re.sub(r'(https://[^\s]+)',lambda m:'<link href="'+m.group(1)+'" color="#247f86">'+m.group(1)+'</link>',text)
  y=para(text,M,y,size=size,leading=size*1.38)-12
 return y

def finish(y=60):
 assert y>=48,(page,'content below safe margin',y)
 layout.append({'page':page,'lowest_content_y':round(y,2)});c.showPage()
# Cover.
page=1;c.setFillColor(HexColor(DARK));c.rect(0,0,W,H,fill=1,stroke=0);c.setFillColor(HexColor('#ece5d6'));c.setFont('GuideBold',40);c.drawString(M,H-83,'CATWORLD');c.setFont('GuideBold',28);c.drawString(M,H-120,'THE WORLD MODEL');c.setFont('Guide',14);c.drawString(M,H-151,'Creator & showrunner field guide')
image(B/'renders/01_panterra.png',M,H-185,CW,CW,True)
para('A planet to draw from. A geography to tell stories in.',M,120,size=14,leading=18,bold=True,col='#ece5d6');para('Revision 6 / 31 October 2026<br/>A separate southern continent and its eastern archipelago.<br/>Northern autumn, southern spring, and an ancient crossing.',M,89,size=10.5,leading=15,col='#a9bec7');c.bookmarkPage('cover');c.addOutlineEntry('Cover','cover',0);finish(48)
# Contents.
y=start('A guide to the model','READING ROUTE','contents');y=para('Read the geography first, then use the reference plates. Established creator facts, draft-deck material and new cartographic proposals are distinguished throughout. Square-bracket source keys point to the reference notes.',M,y,size=11,leading=16)-22
for i,s in enumerate(SECTIONS):
 yy=y;para(f'<link href="#section{i}">{html.escape(s["title"])}</link>',M,yy,width=CW-30,size=10.3,leading=15);c.setFont('Guide',10.3);c.setFillColor(HexColor(TEAL));c.drawRightString(W-M,yy-11,str(i+3));y-=21
base=3+len(SECTIONS)
for title,pg,key in [('Sources and reference notes',base,'sources0'),('Landmark catalogue',base+2,'catalogue0'),('Model specifications and camera index',base+6,'specs'),('Sixteen drawing-reference plates',base+7,'plate01')]:
 para(f'<link href="#{key}">{title}</link>',M,y,width=CW-30,size=10.3,leading=15,bold=True);c.drawRightString(W-M,y-11,str(pg));y-=22
finish(y)
# Main chapters.
for i,s in enumerate(SECTIONS):
 y=start(s['title'],s['kicker'],f'section{i}')
 if s['figure']:
  # Reserve a legible paragraph block before allocating the figure height.
  size=10.1 if s['figure']=='guide/Revision_Comparison.jpg' else 10.5
  estimated=0
  for a,b in s['paras']:
   for txt,sz,lead in [(a,size+.5,15),(b,size,size*1.38)]:
    q=Paragraph(html.escape(txt),ParagraphStyle('m',fontName='Guide',fontSize=sz,leading=lead));estimated+=q.wrap(CW,1000)[1]
   estimated+=16
  maxh=min(400 if s['figure']=='guide/Revision_Comparison.jpg' else 340,y-60-estimated-16)
  y=figure(s['figure'],y,maxh=maxh);y=textblocks(s['paras'],y,size=size)
 else:y=textblocks(s['paras'],y)
 finish(y)
# Sources in two pages, so long URLs remain readable.
for j,entries in enumerate([SOURCES[:7],SOURCES[7:]]):
 y=start('Sources and reference notes'+(' / continued' if j else ''),'PROVENANCE',f'sources{j}');y=textblocks(entries,y,size=10);finish(y)
features=json.load(open(B/'source/features.json'))
for j in range(4):
 y=start(f'Landmark catalogue / {j+1} of 4','COORDINATES + WORKING NAMES',f'catalogue{j}')
 for f in features[j*10:(j+1)*10]:
  y=para(f"<b>{f['id']} / {html.escape(f['name'])}</b>",M,y,size=10.5,leading=15)-3
  y=para(f"{f['lat']:.3f} latitude, {f['lon']:.3f} longitude. {html.escape(f['description'])}",M,y,size=9.5,leading=13)-13
 finish(y)
# Specifications and camera index.
y=start('Specifications and camera index','USING THE FILES','specs');stats=json.load(open(B/'source/statistics.json'));model=json.load(open(B/'source/Model_Verification.json'))
y=textblocks([('Model scale','Radius 6,100 km; axial tilt 35 degrees; orbital period 4,000 Earth years; assumed rotation 24 hours. Globe radius in Blender is 10 units. Physical elevation is separate from 10x display relief. The dam model uses 1 unit = 1 km.'),('Resolution',f"{model['globe_vertices']:,} globe vertices and {model['globe_quads']:,} quads. Four packed 4096 x 2048 maps. Thirteen 2048 x 2048 globe renders, two dam renders and one waterfall render at 2400 x 1600. Thirty-six named geographic anchors. Reservoir footprint: {stats['reservoir_area_km2']:,.0f} km2. Peak physical elevation: {stats['peak_m']/1000:.2f} km."),('Validation','Panterra and the east are connected; the southern core is separate. The designed shelf connects at -65 m sea level; polar land remains separate. The northern feeder and both reservoir outlets descend. Named city sites are checked against land and reservoir masks. Source scripts, image sizes, gallery links and packed textures are checked. These checks do not replace tectonic, climate, erosion or hydraulic simulation.')],y,size=10)
views=json.load(open(B/'source/views.json'));dam=json.load(open(B/'source/dam_views.json'))+json.load(open(B/'source/waterfall_views.json'));y-=5
for idx,v in enumerate(views):
 y=para(f"<b>Frame {idx+1:02d}</b> - {v['name']} - center {v['latitude']:.0f} lat / {v['longitude']:.0f} lon",M,y,size=9,leading=12)-3
y-=8;y=para('Dam file: frame 1 = valley context; frame 2 = structural detail. Clean PNGs, annotated PNGs, editable models, textures, source scripts, CSV landmarks and this guide are included in the full archive.',M,y,size=9.5,leading=13);finish(y)
# Reference plates: vector numbers and readable vector legends, not tiny baked legends.
select={'01':['01','02','03','04','05','06','07','24','16','25'],'02':['02','10','18','19','22','26'],'03':['07','08','11','12','13','20','21','24','27'],'04':['11','12','18','19','21','26','27','23'],'05':['01','02','09','10','23','28'],'06':['11','12','13','17','29','30'],'07':['02','03','04','05','06','07','16','24','25'],'08':['01','02','09','28'],'11':['11','12','20','21','26','27'],'12':['10','18','19','22','26'],'13':['04','07','24','16','25'],'14':['11','12','13','20','27']}
titles={'01':'Panterra / front hemisphere','02':'Eastern hemisphere','03':'Western hemisphere','04':'Far-side hemisphere','05':'North polar view','06':'South polar view','07':'Panterra / regional study','08':'Northern impact basin','09':'Great dam / valley context','10':'Great dam / structural study','11':'Southern continent','12':'Eastern continent','13':'Seattle / primary waterway','14':'Eastern archipelago'}
titles.update({'15':'PLATEAU / RIVER SYSTEM','16':'NORTHERN PLATEAU FALLS'})
select.update({'01':['01','02','33','34','04','07','05','24'],'07':['04','07','24','31','32','35','36'],'13':['04','07','24','32'],'15':['02','03','04','05','24','31','32']})
for v in sorted(views+dam,key=lambda q:q['name']):
 idx=v['name'][:2];y=start(titles[idx],f'REFERENCE PLATE {idx}',f'plate{idx}');ff=[f for f in v['features'] if f['visible'] and (idx not in select or f['id'] in select[idx])]
 im=Image.open(B/'renders'/f"{v['name']}.png");fw=450 if idx in ['09','10','16'] else 400;fh=fw*im.height/im.width;x=M+(CW-fw)/2;top=y
 image(B/'renders'/f"{v['name']}.png",x,top,fw,fh,True)
 for f in ff:
  px=x+f['x']*fw;py=top-f['y']*fh;c.setFillColor(HexColor(RED));c.setStrokeColor(HexColor('#f5d2a8'));c.circle(px,py,7,fill=1,stroke=1);c.setFillColor(HexColor('#ffffff'));c.setFont('GuideBold',7.5);c.drawCentredString(px,py-2.7,f['id'])
 y=top-fh-12
 label='Local landform blockout. True vertical scale; 1 unit = 1 km. Water is not fluid-simulated.' if idx=='16' else 'Local engineering concept. Scale: 1 unit = 1 km.' if idx in ['09','10'] else f"Center {v['latitude']:.0f} latitude / {v['longitude']:.0f} longitude. Orthographic view; relief displayed at 10x."
 y=para(label,M,y,size=8.5,leading=11,col=GRAY)-14
 if idx in ['07','13','15']:y=para('FLOW: Northern feeder -> falls -> lake; west -> Seattle; east -> dam',M,y,size=9,leading=12,bold=True,col=TEAL)-12
 colw=(CW-20)/2;ys=[y,y]
 for j,f in enumerate(ff):
  col=j%2;xx=M+col*(colw+20);yy=ys[col];yy=para(f"<b>{f['id']} / {html.escape(f['name'])}</b>",xx,yy,width=colw,size=8.7,leading=11.5)-2
  if f.get('description'):yy=para(html.escape(f['description']),xx,yy,width=colw,size=8.1,leading=10.5,col=GRAY)-7
  else:yy-=8
  ys[col]=yy
 finish(min(ys))
c.save();json.dump({'pages':page,'sections':len(SECTIONS),'layout':layout},open(G/'PDF_Layout_Verification.json','w'),indent=2)
md=['# CATWORLD / TERRA - CREATOR & SHOWRUNNER GUIDE','Revision 6. Prepared 31 October 2026.']
for s in SECTIONS:
 md+=['## '+s['title']]
 for h,t in s['paras']:md+=['### '+h,t]
md+=['## Sources and reference notes']
for h,t in SOURCES:md+=['### '+h,t]
(G/'Creator_Guide.md').write_text('\n\n'.join(md)+'\n');print('CREATOR GUIDE',page,'pages',P)
