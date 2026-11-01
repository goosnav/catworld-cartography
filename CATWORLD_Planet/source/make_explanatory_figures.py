"""Export creator-facing geography diagrams; all are conceptual, not simulations."""
from PIL import Image,ImageDraw,ImageFont
from pathlib import Path
import math
B=Path(__file__).resolve().parents[1];G=B/'guide';G.mkdir(exist_ok=True)
BG='#f4f0e7';INK='#18333f';TEAL='#207f89';RED='#b8523e';GOLD='#aa7d3c';GRAY='#64767a'
def font(n,b=False):return ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial'+(' Bold' if b else '')+'.ttf',n)
def canvas(title,sub,size=(2200,1050)):
 im=Image.new('RGB',size,BG);d=ImageDraw.Draw(im);d.text((65,40),title,font=font(58,True),fill=INK);d.text((65,120),sub,font=font(33),fill=GRAY);return im,d
def arrow(d,a,b,col=TEAL,width=8):
 d.line([a,b],fill=col,width=width);ang=math.atan2(b[1]-a[1],b[0]-a[0]);d.polygon([b,(b[0]-30*math.cos(ang-.5),b[1]-30*math.sin(ang-.5)),(b[0]-30*math.cos(ang+.5),b[1]-30*math.sin(ang+.5))],fill=col)
def label(d,p,text,b=False,col=INK):
 for j,t in enumerate(text.split('\n')):d.text((p[0],p[1]+44*j),t,font=font(36,b),fill=col)
im,d=canvas('THE MOUNTAINS ARE A CONTINENTAL COLLISION','North-to-south conceptual section through Panterra. Vertical scale is exaggerated.')
profile=[(80,720),(260,680),(410,710),(530,590),(620,480),(690,535),(760,310),(815,440),(870,230),(930,390),(1000,340),(1080,470),(1190,500),(1320,550),(1430,640),(1500,735),(1710,735),(1735,795),(1890,835),(2120,850)]
d.polygon(profile+[(2120,1000),(80,1000)],fill='#b8a180');d.line(profile,fill=INK,width=7);d.polygon([(590,800),(800,940),(1080,990),(1270,900),(1430,790),(1430,1000),(590,1000)],fill='#8c7362');d.line([(570,860),(820,930),(1090,960),(1350,860)],fill=RED,width=10)
for a,b in [((180,925),(570,925)),((2020,925),(1470,925))]:arrow(d,a,b,RED)
for a,b in [((1500,735),(1710,735)),((1735,795),(1890,835))]:d.line([a,b],fill=TEAL,width=12)
label(d,(100,500),'OLDER NORTHERN\nCRUST + IMPACT\nPROVINCE',True);label(d,(660,190),'FOLDED HIGH RANGES',True);label(d,(1090,350),'DISSECTED\nPLATEAU',True);label(d,(1460,560),'SUPER-LAKE\n690 m',True);label(d,(1770,655),'DAM + LOWER\nRIVER PLAIN',True);label(d,(750,1000),'Thickened crust supports uplift; erosion cuts connected valleys.',False)
im.save(G/'Mountain_Section.png')
im,d=canvas('THE WATERWAY HAS ONE CLEAR DIRECTION','Seattle is upstream of the lake. The large trading city is downstream of the dam.',(2200,940))
boxes=[(70,270,450,600,'SEATTLE','Timber city\nUpstream river\nMountain runoff'),(610,270,1040,600,'SUPER-LAKE','London / Rome\nFresh water + fisheries\nLevel: 690 m'),(1200,270,1580,600,'GREAT DAM','4.8 km crest\nPower + controlled flow\nLocal engineering inset'),(1740,270,2130,600,'DOWNSTREAM CITY','Amsterdam shorthand\nCanals + trade\nAlluvial lowlands')]
for x,y,x2,y2,title,body in boxes:
 d.rounded_rectangle((x,y,x2,y2),18,fill='#e3e7df',outline=TEAL,width=4);d.text((x+25,y+25),title,font=font(32,True),fill=INK)
 lines=[]
 for raw in body.split('\n'):
  line=''
  for word in raw.split():
   test=(line+' '+word).strip()
   if d.textlength(test,font=font(30))>x2-x-50 and line:lines.append(line);line=word
   else:line=test
  lines.append(line)
 for j,line in enumerate(lines):d.text((x+25,y+100+j*38),line,font=font(30),fill=INK)
for i in range(3):arrow(d,(boxes[i][2]+15,435),(boxes[i+1][0]-20,435),TEAL,10)
label(d,(80,720),'Water, logs and cargo follow the corridor. Rapids, locks, canals and transshipment\nneed local design before the whole route can be treated as navigable.',False)
im.save(G/'Waterway_Logic.png')
im,d=canvas('RAIN SHADOW: FOLLOW THE AIR, NOT THE PAGE','Proposed moisture route across the eastern mountain wall; direction matters.')
profile=[(100,810),(370,810),(530,780),(650,680),(790,460),(900,340),(980,500),(1100,430),(1220,610),(1390,730),(1600,760),(1830,770),(2110,785)]
d.polygon(profile+[(2110,940),(100,940)],fill='#bc9d6a');d.polygon([(370,810),(530,780),(650,680),(790,460),(900,340),(980,500),(1100,430),(1100,940),(370,940)],fill='#68815d');d.rectangle((100,810,370,940),fill='#4c9aa4');d.line(profile,fill=INK,width=7)
for a,b in [((180,520),(520,520)),((540,510),(790,270)),((1100,265),(1470,490)),((1500,500),(1980,540))]:arrow(d,a,b,TEAL)
for x,y in [(600,580),(660,520),(730,450)]:
 for j in range(4):d.line([(x+j*28,y),(x-22+j*28,y+70)],fill=TEAL,width=5)
label(d,(110,250),'OCEAN MOISTURE',True);label(d,(480,200),'RISING AIR\nCOOLS + RAINS',True);label(d,(1490,250),'DESCENDING AIR\nWARMS + DRIES',True);label(d,(440,845),'WET WINDWARD SLOPES',True);label(d,(1370,845),'LEE DESERT + SALT BASINS',True)
label(d,(80,975),'Southern continent: wet eastern slopes, dry interior; southern westerlies moisten the southwest.',False)
im.save(G/'Rainshadow_Section.png')
im,d=canvas('A YEAR LASTS FOUR THOUSAND EARTH YEARS','Illustrative near-circular orbit: four approximately 1,000-year seasonal quarters.',(2200,940))
colors=['#95ae85','#c3aa5a','#bd805f','#a6bdcb'];titles=['NORTHERN SPRING','NORTHERN SUMMER','NORTHERN AUTUMN','NORTHERN WINTER'];bodies=['Forests advance\nIce retreats\nNew farmland','Long warmth\nHigh northern habitability\nMigration destinations shift','Cooling frontier\nSnow closes routes\nPresent: late autumn','Ice expansion\nSouthern refuge pressure\nOld routes become stories']
for j in range(4):
 x=70+j*530;d.rounded_rectangle((x,250,x+505,660),15,fill=colors[j]);d.text((x+25,280),titles[j],font=font(34,True),fill=INK);d.text((x+25,350),'~ 1,000 Earth years',font=font(33),fill=INK);label(d,(x+25,430),bodies[j])
label(d,(80,750),'The southern hemisphere has opposite seasons. Exact duration depends on orbital eccentricity.\nThe star / heat source remains unresolved; the map represents one epoch, not the full climate cycle.')
im.save(G/'Long_Seasons.png')
im,d=canvas('GEOGRAPHY CREATES THE STORY PRESSURES','The links below are narrative consequences of the model, not fixed political borders.',(2200,980))
rows=[('NORTHERN IRON','Ore + craft production','Mountain passes','Migration + bargaining power'),('WESTERN FOREST','Giant timber + sacred sites','Seattle river','Logging + contested land'),('LAKE + DAM','Food, water + electricity','Controlled outlet','Infrastructure + political power'),('SOUTHERN SHELF','Fish + sheltered harbours','Island straits','Merchants + migration memory')]
for j,row in enumerate(rows):
 y=235+j*165
 for k,t in enumerate(row):
  x=70+k*535;d.rounded_rectangle((x,y,x+480,y+120),12,fill='#e2e6dc' if k<3 else '#e8d1bb');d.text((x+20,y+36),t,font=font(30,k==0),fill=INK)
  if k<3:arrow(d,(x+485,y+60),(x+525,y+60),TEAL,6)
im.save(G/'Story_Geography.png')
print('EXPLANATORY FIGURES COMPLETE')
