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
im,d=canvas('TWO RIVER CORRIDORS / A LAKE WITH TWO OUTLETS','Conceptual map and elevations. Arrows show flow; positions and distances are schematic.',(2200,1320))
def box(x,y,w,h,title,lines):
 d.rounded_rectangle((x,y,x+w,y+h),18,fill='#e3e7df',outline=TEAL,width=4)
 d.text((x+22,y+20),title,font=font(32,True),fill=INK)
 for j,t in enumerate(lines):d.text((x+22,y+77+j*39),t,font=font(29),fill=INK)
box(1390,205,680,210,'NORTHERN MOUNTAIN RIVER',['Upper plateau: ~1,090 m near falls','High river supplies the lake'])
box(830,520,610,225,'DROWNED VALLEY / SUPER-LAKE',['Water surface: ~690 m','Surrounding plateau is higher','London / Rome: lakeshore districts'])
box(70,650,570,245,'SEATTLE / WESTERN FORESTS',['Natural high sill: ~685 m','River falls toward the coast','Forest country and estuary port'])
box(1500,870,620,245,'EASTERN DAM + DOWNSTREAM CITY',['Crest 715 m / local tailwater 266 m','Dam blocks the lower valley route','Managed discharge toward the sea'])
arrow(d,(1500,420),(1320,505),TEAL,10);label(d,(1290,435),'FALLS: ~400 m',True)
arrow(d,(815,640),(655,725),TEAL,10);label(d,(610,525),'WESTERN\nOVERFLOW',True)
arrow(d,(1370,755),(1550,855),TEAL,10)
label(d,(80,1000),'The northern feeder follows the marked route northwest of the lake.\nThe western Seattle outlet lies below it.\nTheir local bends vary; the redline controls placement.')
label(d,(80,1210),'One naturally overflowing lake and one controlled eastern outlet. No second western dam.',False)
im.save(G/'Waterway_Logic.png')
im,d=canvas('A DROWNED VALLEY WITHIN THE PLATEAU','Conceptual section along the northern feeder, reservoir and lower eastern valley.',(2200,1100))
profile=[(80,310),(300,330),(520,350),(650,330),(720,350),(760,520),(850,550),(920,640),(1110,650),(1310,655),(1490,660),(1600,665),(1640,860),(1840,905),(2120,955)]
d.polygon(profile+[(2120,1040),(80,1040)],fill='#b8a180');d.line(profile,fill=INK,width=6)
d.line([(80,316),(680,340),(750,355),(790,525),(900,570),(950,615)],fill=TEAL,width=13)
d.polygon([(950,615),(1600,615),(1600,665),(1310,655),(1110,650),(920,640)],fill='#6aa9b1')
d.polygon([(1585,600),(1630,600),(1690,870),(1600,870)],fill='#738087');d.line([(1690,860),(1850,900),(2110,945)],fill=TEAL,width=11)
label(d,(80,200),'UPPER PLATEAU RIVER',True);label(d,(770,250),'FALLS\n1,090 to 690 m',True);label(d,(1070,470),'DROWNED VALLEY\n690 m WATER',True);label(d,(1640,390),'EASTERN DAM\n715 m CREST',True);label(d,(1720,740),'LOWER VALLEY\n+ CITY',True)
label(d,(90,800),'A high western side saddle (not in this section)\nallows natural overflow toward Seattle.\nThe dam closes the former deeper eastern exit.')
im.save(G/'Plateau_Valley_Section.png')
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
