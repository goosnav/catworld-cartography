import numpy as np, json, os
from PIL import Image, ImageDraw
from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter, distance_transform_edt, map_coordinates, zoom
from pathlib import Path
OUT=Path(__file__).resolve().parents[1]; W,H=4096,2048
rng=np.random.default_rng(49)
# Coordinates traced from map 5, in its 3614 x 2816 display frame.
main=[(945,1117),(1010,1060),(1050,992),(1110,955),(1170,925),(1130,900),(1105,867),(1100,830),(1070,805),(1065,779),(1095,772),(1125,794),(1155,775),(1190,768),(1220,775),(1260,751),(1300,746),(1350,752),(1395,750),(1405,737),(1400,678),(1370,654),(1355,620),(1350,575),(1360,539),(1400,515),(1420,493),(1470,489),(1510,488),(1565,498),(1500,522),(1460,550),(1445,594),(1458,638),(1480,663),(1535,680),(1575,690),(1625,680),(1670,663),(1694,625),(1706,580),(1670,540),(1668,527),(1710,540),(1755,542),(1780,565),(1804,580),(1770,608),(1762,650),(1750,690),(1720,703),(1668,718),(1675,745),(1720,775),(1670,816),(1680,850),(1720,870),(1760,878),(1800,910),(1850,904),(1870,878),(1910,870),(1948,880),(1980,868),(2015,875),(2070,860),(2110,850),(2150,855),(2190,865),(2230,852),(2280,858),(2320,880),(2380,885),(2430,865),(2480,870),(2500,896),(2494,927),(2535,936),(2546,975),(2580,966),(2630,992),(2680,974),(2720,948),(2760,936),(2800,970),(2820,1008),(2870,1032),(2920,1060),(2945,1130),(2947,1250),(2910,1380),(2845,1515),(2790,1547),(2730,1534),(2690,1510),(2660,1522),(2610,1530),(2570,1510),(2560,1470),(2540,1450),(2542,1400),(2568,1350),(2555,1320),(2510,1300),(2450,1280),(2390,1255),(2320,1250),(2260,1250),(2200,1265),(2160,1280),(2200,1235),(2240,1180),(2290,1140),(2330,1080),(2340,1040),(2320,1010),(2260,980),(2200,952),(2120,938),(2050,936),(1990,954),(1950,978),(1910,1017),(1870,1050),(1850,1110),(1850,1180),(1880,1190),(1892,1220),(1880,1244),(1895,1280),(1892,1310),(1860,1345),(1838,1370),(1825,1405),(1770,1380),(1740,1380),(1705,1400),(1660,1380),(1610,1384),(1570,1374),(1550,1350),(1540,1300),(1500,1270),(1450,1260),(1400,1237),(1380,1210),(1340,1180),(1290,1180),(1250,1192),(1220,1173),(1190,1165),(1175,1122),(1155,1095),(1120,1085),(1095,1104),(1065,1100),(1030,1110),(995,1115)]
# Southern peninsula below the central lake.
pen=[(1190,1160),(1230,1185),(1300,1180),(1390,1190),(1430,1250),(1535,1290),(1555,1350),(1600,1380),(1670,1380),(1680,1450),(1710,1570),(1625,1560),(1590,1580),(1600,1540),(1610,1510),(1580,1475),(1530,1450),(1480,1440),(1440,1440),(1400,1480),(1380,1520),(1340,1560),(1310,1530),(1300,1490),(1270,1470),(1240,1455),(1210,1440),(1220,1420),(1260,1400),(1300,1370),(1320,1340),(1310,1300),(1290,1270),(1280,1240),(1260,1220),(1220,1215),(1180,1240),(1140,1260),(1055,1300),(1095,1248),(1130,1230),(1160,1190)]
south=[(230,1395),(290,1385),(335,1350),(320,1390),(330,1430),(355,1455),(405,1468),(455,1470),(500,1460),(530,1440),(545,1465),(570,1475),(575,1510),(600,1530),(627,1510),(660,1518),(700,1540),(750,1550),(795,1572),(825,1545),(860,1490),(875,1494),(850,1540),(868,1590),(890,1630),(895,1655),(918,1650),(923,1615),(940,1630),(950,1680),(1000,1720),(968,1740),(940,1720),(905,1705),(870,1710),(850,1740),(842,1780),(844,1808),(790,1785),(720,1745),(660,1715),(600,1680),(540,1640),(480,1600),(420,1560),(360,1510),(300,1470),(260,1435)]
nw=[(350,634),(400,610),(460,570),(520,535),(600,490),(700,445),(800,415),(900,390),(978,380),(950,410),(914,435),(925,455),(953,466),(946,485),(910,502),(868,510),(875,560),(870,600),(902,641),(880,644),(840,624),(820,609),(780,600),(750,609),(728,580),(700,568),(680,568),(638,585),(600,576),(580,594),(555,630),(550,670),(530,700),(505,712),(475,710),(446,724),(430,747),(420,730),(416,701),(437,672),(399,662),(380,650)]
islands=[[(930,1460),(975,1490),(970,1520),(959,1550),(980,1580),(1010,1605),(1045,1640),(1000,1625),(960,1605),(930,1595),(918,1575),(923,1530),(935,1500)],[(1610,1605),(1650,1590),(1680,1610),(1670,1660),(1690,1675),(1650,1678),(1620,1660)],[(2490,1465),(2510,1500),(2530,1520),(2520,1540),(2570,1560),(2600,1585),(2570,1600),(2530,1605),(2490,1585),(2470,1540)],[(300,995),(320,966),(335,947),(337,930),(353,917),(373,945),(405,953),(420,990),(390,1005),(365,1020),(340,1014)],[(870,1120),(910,1097),(929,1120),(940,1140),(910,1130),(885,1138)],[(1552,585),(1574,567),(1600,570),(1592,587),(1579,596),(1586,609),(1570,613)],[(2190,1003),(2210,992),(2240,1004),(2260,1030),(2250,1060),(2247,1095),(2232,1099),(2220,1070),(2230,1048),(2210,1028)],[(1140,1270),(1190,1246),(1230,1255),(1260,1276),(1250,1294),(1220,1298),(1188,1285)]]
def ll(pt):
 x,y=pt
 # Revision: compact Panterra, retain hooked peninsulas and enlarge the impact bay.
 if 960<x<1950 and y>1000:
  weight=min((y-1000)/120,1)
  x=1450+(x-1450)*(1-.23*weight)
  y=1000+(y-1000)*.92
 cr=np.sqrt(((x-1560)/340)**2+((y-595)/260)**2)
 if y<800:
  weight=max(0,min(1,(1.5-cr)*2))
  x=1560+(x-1560)*(1+.22*weight)
  y=595+(y-595)*(1+.18*weight)
 s=np.clip((1145-y)/773,-.998,.998); theta=np.arcsin(s)
 lat=np.degrees(np.arcsin(np.clip((2*theta+np.sin(2*theta))/np.pi,-1,1)))
 lat += 17*np.cos(np.radians(lat))
 lon=np.clip((x-1550)/(1410*np.cos(theta))*180,-179.95,179.95)
 return [float(lon),float(lat)]
def pix(lon,lat): return ((lon+180)/360*W,(90-lat)/180*H)
def poly(points):
 return [pix(*ll(p)) for p in points]
mask=Image.new('L',(W,H)); d=ImageDraw.Draw(mask)
for p in [main,pen,south,nw]+islands: d.polygon(poly(p),fill=255)
# Small source islands and shelf fragments.
for x,y,r in [(302,942,12),(884,1458,17),(1510,1425,8),(1053,1555,10),(1110,1565,7),(1180,1605,10),(1715,1595,12),(1617,495,9),(1640,491,4),(818,1155,10),(786,1170,4)]:
 q=[(x+np.cos(t)*r,y+np.sin(t)*r*.7) for t in np.linspace(0,6.283,18)];d.polygon(poly(q),fill=255)
# Deep fault-guided bays break up the broad central silhouette.
for bay in [[(1890,1100),(1830,1105),(1790,1130),(1740,1138),(1775,1160),(1760,1190),(1815,1200),(1890,1220)],[(1135,1112),(1180,1118),(1225,1132),(1248,1165),(1205,1175),(1160,1190)],[(2030,1305),(1755,1318),(1722,1340),(1750,1368),(2030,1420)]]:
 d.polygon(poly(bay),fill=0)
# Rifted east coast: long fault-guided gulf and a separated island arc.
d.polygon(poly([(2450,1340),(2475,1265),(2510,1200),(2480,1150),(2495,1095),(2520,1130),(2540,1210),(2595,1300),(2630,1540)]),fill=0)
# Southern failed rift opens into the old island shelf, splitting capes from the desert shield.
d.polygon(poly([(845,1460),(810,1520),(750,1540),(710,1580),(740,1595),(780,1570),(830,1575),(875,1605),(910,1550)]),fill=0)
# An old glacial fjord province in the high-latitude remnant.
for fjord in [[(600,575),(645,540),(670,510),(650,550),(635,590)],[(745,610),(760,555),(800,510),(785,575),(780,620)]]:d.polygon(poly(fjord),fill=0)
# Revision 2: three continental cores joined by a continuous collision isthmus.
# Geographic polygons cross the date line by drawing unwrapped copies.
def geo_poly(points,fill=255,canvas=d):
 for shift in [-360,0,360]:canvas.polygon([pix(lo+shift,la) for lo,la in points],fill=fill)
def geo_line(points,width=2,fill=255,canvas=d):
 for shift in [-360,0,360]:canvas.line([pix(lo+shift,la) for lo,la in points],fill=fill,width=width,joint='curve')
connector=[(157,27),(171,24),(182,16),(190,10),(199,1),(212,-13),(215,-22),(204,-27),(194,-18),(184,-9),(176,-1),(165,11),(155,18)]
geo_poly(connector)
# Two embayments expose the flanks of the collision neck without severing its spine.
geo_poly([(179,25),(190,24),(203,13),(207,3),(200,5),(193,12),(185,16)],0)
geo_poly([(156,-21),(161,-13),(159,-6),(161,1),(165,4),(168,1),(168,-5),(172,-8),(170,-12),(165,-20)],0)
# A wider buried impact apron ties the basin into the northern craton.
geo_poly([(-32,46),(-38,53),(-37,59),(-28,59),(-19,54),(0,51),(22,55),(38,59),(42,51),(30,45),(12,43),(-12,43)])
# A drowned continental shelf, with long tilted islands and narrow straits.
bridge=[(-118,-39),(-103,-33),(-86,-26),(-70,-21),(-57,-12),(-44,4)]
for i in range(37):
 t=i/36*(len(bridge)-1);k=min(int(t),len(bridge)-2);u=t-k
 lo=bridge[k][0]*(1-u)+bridge[k+1][0]*u;la=bridge[k][1]*(1-u)+bridge[k+1][1]*u
 lo+=rng.uniform(-1.5,1.5);la+=rng.uniform(-1.7,1.7)
 a=rng.uniform(.6,2.0)*(1.5 if i%7==0 else 1);b=a*rng.uniform(.3,.6)
 q=[]
 for t0 in np.linspace(0,2*np.pi,28,endpoint=False):
  rr=1+.17*np.sin(3*t0+i)+.09*np.cos(7*t0-i);xx=a*np.cos(t0)*rr;yy=b*np.sin(t0)*rr
  q.append((lo+xx*.86-yy*.5,la+xx*.5+yy*.86))
 geo_poly(q)
# Arctic islands: irregular bedrock and channels, not a circular white disk.
for q in [[(-125,72),(-111,74),(-103,80),(-110,84),(-128,81),(-143,77)], [(-89,76),(-77,73),(-67,78),(-61,83),(-75,86),(-91,83)],[(75,69),(93,67),(107,72),(110,78),(93,80),(80,76)],[(130,76),(148,73),(160,77),(159,82),(143,84),(130,80)]]:geo_poly(q)
# South polar land has an asymmetric ice sheet, two deep embayments and a peninsula.
boundary=[]
for lo in np.linspace(-180,180,721):
 a=np.radians(lo);edge=-68+5*np.sin(2*a+.5)+3*np.sin(3*a-1)+1.4*np.cos(7*a)
 edge-=6*np.exp(-(((lo+25+180)%360-180)/21)**2)
 edge+=8*np.exp(-(((lo-112+180)%360-180)/18)**2)
 boundary.append((lo,float(edge)))
geo_poly([(-180,-90)]+boundary+[(180,-90)])
base=np.array(mask)>0
Y,X=np.mgrid[0:H,0:W]; lat=90-(Y+.5)*180/H; lon=(X+.5)*360/W-180
# Periodic noise in longitude. Multi-octave value fields for continent detail.
def noise(scale):
 h=max(3,int(H/scale)); w=max(6,int(W/scale)); a=rng.normal(size=(h,w)).astype('f');a=np.pad(a,((2,2),(2,2)),mode='wrap')
 return map_coordinates(a,[Y/H*h+2,X/W*w+2],order=3,mode='wrap').astype('f')
n1=noise(130);n2=noise(42);n3=noise(13);n4=noise(4);n5=noise(1.6)
# Cartesian polar noise removes longitude pinching and radial spokes at the poles.
a0=np.radians(lon);rho0=90-np.abs(lat);px0=rho0*np.cos(a0);py0=rho0*np.sin(a0)
polarmix=np.clip((np.abs(lat)-58)/12,0,1).astype('f')
for name,scale in [('n1',.25),('n2',.8),('n3',2.3),('n4',6),('n5',13)]:
 grid=rng.normal(size=(256,256)).astype('f')
 pn0=map_coordinates(grid,[py0*scale+128+np.where(lat>0,30,-30),px0*scale+128],order=3,mode='wrap')
 globals()[name]=globals()[name]*(1-polarmix)+pn0*polarmix
sdf=distance_transform_edt(base)-distance_transform_edt(~base)
# Periodic coastline distance and continuous fine texture at the date line.
wrapped=np.pad(base,((0,0),(200,200)),mode='wrap')
sdf=(distance_transform_edt(wrapped)-distance_transform_edt(~wrapped))[:,200:-200]
# Reconcile the sketch's unmatched outer-edge coasts over a narrow seam corridor.
for j in range(72):
 xx=(W-36+j)%W;t=j/71;t=t*t*(3-2*t)
 sdf[:,xx]=(1-t)*sdf[:,W-37]+t*sdf[:,36]
land=(sdf + 2.8*n3+1.2*n4+.45*n5)>0
land[:2]=False
land[-2:]=True
coast=distance_transform_edt(land)
# Ridges traced from the same source; widths in texels.
ranges=[([(1000,1090),(1100,1020),(1220,985),(1375,950),(1490,915),(1600,920),(1710,940),(1830,936),(1950,913),(2100,902),(2230,904),(2360,932),(2480,980),(2620,1060),(2760,1160),(2910,1250)],18,5900), ([(365,1505),(470,1560),(600,1620),(750,1700),(840,1770)],15,3600), ([(1240,1435),(1300,1460),(1340,1525)],9,2700)]
def linefield(points,width):
 im=Image.new('L',(W,H));ImageDraw.Draw(im).line(poly(points),fill=255,width=2)
 a=np.array(im)>0;dist=distance_transform_edt(~a);return np.exp(-(dist/width)**2)
mount=np.zeros((H,W),dtype='f')
for p,w,a in ranges[1:]: mount=np.maximum(mount,a*linefield(p,w*1.6))
# Himalaya DEM provides eroded subsidiary ridges, warped to the fictional suture.
# Data: Mapzen Terrain Tiles on AWS; USGS SRTM/GMTED. See attribution file.
dem=np.load(OUT/'source/mountain_analogue_dem.npy')
dh,dw=dem.shape
smoothdem=gaussian_filter(dem,35)
grad=-np.gradient(smoothdem,axis=0)
edge=np.argmax(grad[180:1250],axis=0)+180
edge=gaussian_filter(edge.astype('f'),45)-90
ridgepts=np.array([ll(p) for p in ranges[0][0]])
orderidx=np.argsort(ridgepts[:,0]);ridgepts=ridgepts[orderidx]
centerlat=np.interp(lon,ridgepts[:,0],ridgepts[:,1])
along=np.clip((lon-ridgepts[0,0])/(ridgepts[-1,0]-ridgepts[0,0]),0,1)
demx=along*(dw-1)
trans=lat-centerlat
edgemap=np.interp(demx,np.arange(dw),edge)
demy=edgemap-trans*46
realrelief=map_coordinates(dem-gaussian_filter(dem,70),[demy,demx],order=1,mode='reflect')
realheight=map_coordinates(dem,[demy,demx],order=1,mode='reflect')
envelope=np.exp(-(trans/8.3)**2)
ends=np.clip((lon-ridgepts[0,0]+2)/5,0,1)*np.clip((ridgepts[-1,0]+2-lon)/5,0,1)
belt=envelope*ends
mount=np.maximum(mount,belt*(4500+np.clip(realrelief,-1300,2600)*1.4+np.clip(realheight-3800,0,4500)*.65))
# Carry the great range across the far side onto the THIRD continental core.
def geofield(points,width):
 im=Image.new('L',(W,H));dd=ImageDraw.Draw(im);geo_line(points,2,255,dd)
 dist=distance_transform_edt(~np.pad(np.array(im)>0,((0,0),(180,180)),mode='wrap'))[:,180:-180]
 return np.exp(-(dist/width)**2)
backspine=[(145,27),(158,22),(171,16),(181,9),(190,1),(199,-8),(210,-18),(222,-29),(235,-39)]
back=geofield(backspine,74)
blon=np.where(lon<0,lon+360,lon);blat=np.interp(blon,np.array(backspine)[:,0],np.array(backspine)[:,1])
bx=np.clip((blon-140)/100,0,1)*(dw-1);by=np.interp(bx,np.arange(dw),edge)-(lat-blat)*39
bh=map_coordinates(dem-gaussian_filter(dem,70),[by,bx],order=1,mode='reflect')
mount=np.maximum(mount,back*(4800+np.clip(bh,-1500,2800)*1.5))
# A second, coast-parallel eastern wall puts the marked interior on the lee side.
eastwall=geofield([(174,9),(170,-3),(165,-16),(154,-23)],53)
mount=np.maximum(mount,eastwall*(4300+np.clip(realrelief,-1200,2300)*1.1))
# Supplement southern eastern barrier; source ridge remains present.
sr=linefield([(830,1510),(820,1580),(820,1650),(845,1740)],15)
# A separate southern convergent margin, with real parallel ridge/valley texture.
southridge=np.array([ll(p) for p in [(830,1510),(820,1580),(820,1650),(845,1740)]])
ss=np.argsort(southridge[:,1]);southridge=southridge[ss]
slon=np.interp(lat,southridge[:,1],southridge[:,0]);sx=np.clip((lat+52)/35,0,1)*(dw-1)
sy=np.interp(sx,np.arange(dw),edge)-(lon-slon)*np.cos(np.radians(lat))*45
srh=map_coordinates(dem-gaussian_filter(dem,70),[sy,sx],order=1,mode='reflect')
senv=np.exp(-(((lon-slon)*np.cos(np.radians(lat)))/4.2)**2)*np.clip((-lat-14)/7,0,1)*np.clip((lat+58)/8,0,1)
mount=np.maximum(mount,senv*(2300+np.clip(srh,-1200,2300)*.95))
# Older southern arc: broad foothills preserve the source sketch's oblique range.
mount=np.maximum(mount,1500*linefield(ranges[1][0],38))
# Plateau below the northern wall, fading to downstream alluvial lowlands.
plate=Image.new('L',(W,H));ImageDraw.Draw(plate).polygon(poly([(1090,1080),(1260,1020),(1500,990),(1770,1000),(1800,1180),(1720,1345),(1580,1350),(1400,1230),(1190,1170)]),fill=255)
plate=gaussian_filter(np.array(plate,dtype='f')/255,18)
ridges=(1-np.minimum(np.abs(.75*n3+.35*n4),1))**2
height=140+240*np.maximum(n1+.4,0)+60*n2+14*n4
detail=(.55*n3+.28*n4+.12*n5)
height+=plate*1250+mount+np.maximum(n2,0)*120
height+=np.maximum(height,400)*.025*detail
# Tectonic saddle passes: lower terrain, not gaps in coastline.
for p in [(1190,1000),(1720,940),(2200,910)]:
 lo,la=ll(p);g=np.exp(-(((lon-lo)*np.cos(np.radians(la))/1.2)**2+((lat-la)/1.1)**2));height-=g*height*.64
# Meteor basin centered inside northern horseshoe; impact rim plus weathered mineral apron.
clon,clat=ll((1560,595));dx=(lon-clon)*np.cos(np.radians(clat));dy=lat-clat;r=np.sqrt(dx*dx+dy*dy)
ring=np.exp(-((r-13.2)/2.1)**2)*2200*(.6+.4*ridges)
height+=ring
# Ice-sheet domes and coastal bedrock, all part of the same displacement field.
polar=np.clip((-lat-61)/22,0,1)*land
height+=polar*(2600+320*n1)+900*geofield([(80,-69),(102,-76),(145,-81),(185,-76),(214,-67)],35)*land
height+=np.clip((lat-69)/12,0,1)*land*(750+350*np.maximum(n1,0))
height=np.minimum(height,10800)
height=np.maximum(height,35)*np.minimum(coast/5,1)
# Reservoir shoreline traced from map; branched drowned valleys refined at full resolution.
lakep=[(1397,1218),(1384,1190),(1405,1168),(1440,1155),(1470,1168),(1500,1180),(1530,1210),(1550,1245),(1570,1270),(1560,1292),(1532,1300),(1490,1280),(1460,1250),(1415,1245)]
lm=Image.new('L',(W,H));dl=ImageDraw.Draw(lm);dl.polygon(poly(lakep),fill=255)
for path in [[(1420,1170),(1405,1135),(1415,1100)],[(1465,1170),(1500,1130),(1510,1090)],[(1530,1210),(1570,1180),(1590,1140)],[(1398,1215),(1360,1225)]]:dl.line(poly(path),fill=255,width=5)
lakebase=np.array(lm)>0
lsdf=distance_transform_edt(lakebase)-distance_transform_edt(~lakebase)
lake=(lsdf+1.7*n3+.6*n4)>0
lakelevel=690
distlake=distance_transform_edt(~lake)
shorebench=(lakelevel+70+50*ridges)*np.exp(-(distlake/40)**4)
height=np.maximum(height,shorebench*land)
height[lake]=lakelevel-90
json.dump({'seattle_to_lake':[ll(p0) for p0 in [(1200,1025),(1220,1060),(1230,1100),(1240,1118),(1270,1129),(1290,1146),(1310,1137),(1330,1152),(1352,1148),(1370,1168),(1395,1187)]],'dam_to_city':[ll(p0) for p0 in [(1555,1290),(1550,1325),(1570,1360),(1610,1375),(1640,1370),(1680,1390)]]},open(OUT/'source/hydrology_paths.json','w'),indent=2)
# Planetary water surfaces. Rivers are texture-width exaggerated for drawing reference.
river_paths=[[(1200,1025),(1220,1060),(1230,1100),(1240,1118),(1270,1129),(1290,1146),(1310,1137),(1330,1152),(1352,1148),(1370,1168),(1395,1187)],[(1510,1000),(1495,1040),(1510,1090),(1500,1130),(1465,1170)],[(1710,1000),(1690,1045),(1650,1080),(1640,1120),(1590,1140),(1570,1180),(1530,1210)],[(1555,1290),(1550,1325),(1570,1360),(1610,1375),(1640,1370),(1680,1390)],[(1635,1450),(1600,1470),(1570,1490),(1550,1510)],[(1210,1060),(1190,1090),(1193,1140)],[(2320,960),(2370,1020),(2410,1070),(2440,1130),(2490,1180),(2515,1250)],[(2660,1110),(2670,1170),(2700,1225),(2700,1300),(2740,1400),(2760,1500)],[(790,1580),(740,1570),(710,1550)]]
river_im=Image.new('L',(W,H));dr=ImageDraw.Draw(river_im)
for k,p in enumerate(river_paths):
 pp=np.array(poly(p));tt=np.arange(len(pp));qq=np.linspace(0,len(pp)-1,len(pp)*18)
 curve=CubicSpline(tt,pp,bc_type='natural')(qq)
 for j in range(1,len(curve)-1):curve[j]+=np.sin(j*.7)*.6
 if k==0:primarycurve=curve.copy()
 dr.line([tuple(q) for q in curve],fill=255,width=7 if k==0 else (5 if k==3 else 2))
riv=(np.array(river_im)/255).astype('f')*land*(~lake)
# Seattle is an upstream inland city. The primary valley descends INTO the lake.
mainriver=Image.new('L',(W,H));ImageDraw.Draw(mainriver).line(poly(river_paths[0]),fill=255,width=9)
mainriver=np.array(mainriver,dtype='f')/255
valley=gaussian_filter(mainriver,8);valley=np.clip(valley*7,0,1)*land
for i,p0 in enumerate(river_paths[0]):
 lo,la=ll(p0);g=np.exp(-(((lon-lo)*np.cos(np.radians(la))/1.05)**2+((lat-la)/1.05)**2))
 target=2450*(1-i/(len(river_paths[0])-1))+lakelevel
 height=height*(1-g)+target*g
# Height graded on outlet corridor so reservoir has a single descending outlet.
for i,p in enumerate(river_paths[3]):
 lo,la=ll(p);g=np.exp(-(((lon-lo)*np.cos(np.radians(la))/.7)**2+((lat-la)/.7)**2));target=650*(1-i/(len(river_paths[3])-1))+15;height=height*(1-g)+target*g
height-=riv*np.minimum(height*.1,80)
# A continuous graded water surface carries Seattle flow into the lake.
watergrade=Image.new('F',(W,H));wg=ImageDraw.Draw(watergrade)
arclen=np.r_[0,np.cumsum(np.linalg.norm(np.diff(primarycurve,axis=0),axis=1))];levels=lakelevel+2450*(1-arclen/arclen[-1])
for j in range(len(primarycurve)-1):wg.line([tuple(primarycurve[j]),tuple(primarycurve[j+1])],fill=float(levels[j+1]),width=7)
mainwater=np.array(watergrade,dtype='f');mainmask=(mainwater>0)&land&(~lake)
height[mainmask]=mainwater[mainmask]-12
json.dump(dict(direction='Seattle -> Great Reservoir -> Dam -> downstream metropolis',main_river_upstream_water_m=float(levels[0]),main_river_lake_inlet_water_m=float(levels[-1]),monotonic_water_profile=bool(np.all(np.diff(levels)<=0)),river_width_is_exaggerated=True),open(OUT/'source/Hydrology_Verification.json','w'),indent=2)
# Route a tributary network through the relief with a priority-flood drainage tree.
# Water bodies are sinks; the hand-set reservoir outlet remains the controlled release.
import heapq
from scipy.ndimage import binary_erosion
step=4;hh=height[::step,::step].copy();lland=land[::step,::step];llake=lake[::step,::step]
water=(~lland)|llake; hh[water]=-2000
ny,nx=hh.shape; visited=water.copy(); par=np.full(ny*nx,-1,dtype=np.int32);order=[];heap=[]
border=(~binary_erosion(water))&water
for yy,xx in zip(*np.where(border)):heapq.heappush(heap,(float(hh[yy,xx]),int(yy*nx+xx)))
while heap:
 h0,j=heapq.heappop(heap);yy,xx=divmod(j,nx);order.append(j)
 for dy0,dx0 in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
  y0=yy+dy0;x0=(xx+dx0)%nx
  if y0<0 or y0>=ny or visited[y0,x0]:continue
  visited[y0,x0]=True;k=y0*nx+x0;par[k]=j;hh[y0,x0]=max(hh[y0,x0],h0+.005);heapq.heappush(heap,(float(hh[y0,x0]),k))
acc=np.ones(ny*nx,dtype=np.float32)
for j in reversed(order):
 if par[j]>=0:acc[par[j]]+=acc[j]
acc=acc.reshape(ny,nx);net=(acc>35)&lland&(~llake)
ni=Image.new('L',(W,H));nd=ImageDraw.Draw(ni)
for yy,xx in zip(*np.where(net)):
 j=yy*nx+xx;k=par[j]
 if k<0:continue
 y0,x0=divmod(int(k),nx)
 if abs(x0-xx)>5:continue
 nd.line([(xx*step,yy*step),(x0*step,y0*step)],fill=int(min(190,65+np.log(acc[yy,xx])*16)),width=1 if acc[yy,xx]<200 else 2)
tributaries=np.array(ni,dtype='f')/255
riv=np.maximum(riv,tributaries*.38)*land*(~lake)
# Biomes: present northern autumn, southern spring. Humid east -> dry southwest.
wet=.65+.13*n1+.10*n2
wet-=.30*np.exp(-((np.abs(lat)-28)/10)**2)
wet+=.15*np.exp(-(lat/15)**2)
# Correct the marked far-side biomes: left/interior dry, right maritime core wet.
sm=(lon<-90)&(lat<10)&(lat>-60)&land
maritime=np.exp(-((((lon+145+180)%360)-180)/60)**6)*np.clip((12-lat)/15,0,1)*np.clip((lat+65)/15,0,1)
wet=wet*(1-maritime)+(.76+.10*n1+.05*n2)*maritime
eastern=np.exp(-(((((lon-143+180)%360)-180)/53)**8))*np.clip((34-lat)/8,0,1)*np.clip((lat+27)/8,0,1)
lee=np.clip((blat-lat+1)/7,0,1)*np.clip((197-blon)/24,0,1)*eastern
wet=wet*(1-lee)+(.075+.035*n2)*lee
# Wet coastal margins and the marine island bridge supply the greener right-hand core.
bridgefield=geofield(bridge,23)
wet=np.maximum(wet,bridgefield*.84)
wet=np.maximum(wet,valley*.80)
# Northern continental interior dries behind Himalayan wall; cool mineral steppe.
wet-=.29*np.exp(-((lat-48)/12)**4-((lon-12)/65)**6)
wet=np.clip(wet,0,1)
dry=np.clip((.48-wet)*2.6,0,1)
forest=np.stack([.13+.04*n2,.23+.045*n2,.12+.025*n2],-1)
grass=np.stack([.31+.025*n3,.35+.025*n3,.18+.018*n3],-1)
color=forest*(np.clip(wet,.0,.8)/.8)[...,None]+grass*(1-np.clip(wet,.0,.8)/.8)[...,None]
sand=np.stack([.66+.045*n2+.015*n4,.49+.035*n2,.29+.025*n2],-1)
color=color*(1-dry[...,None])+sand*dry[...,None]
rock=np.clip((height-2100)/3000,0,.9)
rockcol=np.stack([.43+.04*n3,.40+.035*n3,.33+.03*n3],-1)
color=color*(1-rock[...,None])+rockcol*rock[...,None]
# Regional southern desert landforms: dune corridors, gravel fans and pale endorheic pans.
dunes=(.5+.5*np.sin(X*.52+3*n2+1.5*n3))*.018
color+=sm[...,None]*dry[...,None]*dunes[...,None]*np.array([1,.8,.45])
pans=sm&(wet<.2)&(height<600)&(n1<-.55)&(n2<-.4)
color[pans]=color[pans]*.35+np.array([.64,.60,.46])*.65
# Oxidized ejecta mixed into land, concentrated inside impact district.
oxide=np.exp(-(r/18)**4)*.7
color=color*(1-oxide[...,None])+np.array([.38,.20,.115])*oxide[...,None]
snowline=5950-24*np.abs(lat)-8*np.maximum(lat,0)
snow=np.clip((height-snowline+150*n3)/600,0,1)*land
snow=np.maximum(snow,np.clip((lat-67+2*n1)/7,0,1)*land)
snow=np.maximum(snow,np.clip((-lat-60+.7*n1)/7,0,1)*land)
color=color*(1-snow[...,None])+np.array([.84,.88,.88])*snow[...,None]
# Bathymetry / continental shelves.
sea_dist=distance_transform_edt(~land)
shelf=np.maximum(np.exp(-sea_dist/9),bridgefield*.36)
sea=np.zeros_like(color)+[.012,.052,.095];sea+=shelf[...,None]*[.016,.14,.14]
sea+=n1[...,None]*.002
# Ferruginous inland sea (sediment plume, not literally metallic water).
redwater=np.exp(-(r/12.0)**6)*(~land)
redwater*=np.clip(.85+.12*n2+.04*n3,.5,1)
sea=sea*(1-redwater[...,None]*.85)+np.array([.24,.073,.040])*redwater[...,None]*.85
color=np.where(land[...,None],color,sea)
color[lake]=[.035,.16,.18]
color=color*(1-riv[...,None]*.88)+np.array([.025,.19,.235])*riv[...,None]*.88
# Tiny arable patchwork in lowlands; no giant city lights on daylight reference.
farm=(land & (height<850)&(wet>.4)&(lat>-28)&(lat<20)&(lon>-45)&(lon<35)&(~lake))
fields=(np.sin(X*.45+n3)*np.sin(Y*.32+n2)>0).astype('f')*.009
color+=farm[...,None]*fields[...,None]*np.array([1,.8,.1])
# Arctic pack ice and Antarctic shelves have separate geography and materials.
# Polar noise uses Cartesian coordinates so it remains continuous at the pole.
a=np.radians(lon);rho=90-np.abs(lat);px=rho*np.cos(a);py=rho*np.sin(a)
pnoise=rng.normal(size=(128,128)).astype('f')
pn=map_coordinates(pnoise,[py*.8+64,px*.8+64],order=3,mode='reflect')
margin=73+4*np.sin(a+.7)+2*np.cos(3*a-1)
ice=np.clip((lat-margin+1.8*pn)/3.5,0,1)*(~land)
from scipy.spatial import cKDTree
floes=rng.uniform(-38,38,size=(42000,2));tree=cKDTree(floes)
pm=lat>62;co=np.column_stack((px[pm]+.3*np.sin(py[pm]*1.4),py[pm]+.3*np.sin(px[pm]*1.1)))
dd,_=tree.query(co,k=2);pack=np.ones((H,W),dtype='f')
pack[pm]=np.clip((dd[:,1]-dd[:,0]-.006)/.06,.72,1)
ice*=pack
# Broken seasonal pack hugs the asymmetric southern coast, leaving large polynyas.
southice=(lat<-61)*(~land)*np.exp(-distance_transform_edt(~land)/22)
southice*=np.clip(.70+.35*pn,0,1)
ice=np.maximum(ice,southice*.85)
icecol=np.stack([.65+.06*pn,.76+.045*pn,.81+.03*pn],-1)
color=color*(1-ice[...,None])+icecol*ice[...,None]
# Ice-sheet flow bands and blue outlet glaciers reveal the polar terrain.
glaciated=land&(lat<-62)
flow=.012*np.sin(rho*5+2*np.sin(a*4)+pn)
color+=glaciated[...,None]*flow[...,None]*np.array([.4,.7,1])
nunataks=glaciated&(geofield([(80,-66),(105,-70),(140,-75),(173,-71)],20)>.55)&(n3>.7)
color[nunataks]=color[nunataks]*.5+np.array([.30,.34,.37])*.5
# Multi-scale drainage texture and shaded relief: finite hills, incised ridge flanks.
fine=.016*n3+.012*n4+.009*n5
color+=fine[...,None]*(land&(~lake))[...,None]*np.array([.8,.75,.55])
gy,gx=np.gradient(height)
shade=np.clip((1-.009*gx+.013*gy)/np.sqrt(1+(.018*gx)**2+(.018*gy)**2),.4,1.20)
shade=1+(shade-1)*np.clip(height/5500,.08,.8)*(land&(~lake))
color*=shade[...,None]
color=np.clip(color,0,1)
Image.fromarray((color*255).astype('uint8')).save(OUT/'textures/albedo_4096.png')
# Bump encodes topography; lake water is at a fixed elevation.
height[~land]=-1500*(1-np.exp(-sea_dist[~land]/25))-50
height=np.where((bridgefield>.22)&(~land),-65-65*(1-bridgefield),height)
surface=height.copy();surface[~land]=0;surface[lake]=lakelevel;surface[mainmask]=mainwater[mainmask]
np.savez_compressed(OUT/'source/terrain_fields.npz',height=height.astype('f'),surface=surface.astype('f'),land=land,lake=lake,wet=wet.astype('f'))
Image.fromarray(np.uint16(np.clip((surface+100)/11100,0,1)*65535)).save(OUT/'textures/height_16bit.png')
rough=np.where(land,.86,.30);rough[lake]=.25;Image.fromarray(np.uint8(rough*255)).save(OUT/'textures/roughness.png')
landimg=Image.fromarray(np.uint8(land)*255);landimg.save(OUT/'textures/land_mask.png')
features=[('01','Ferric Sea / impact basin',(1560,595),'Ancient impact; iron-rich sediment and central uplift'),('02','Northern Divide',(1500,925),'Enormous folded belt; multiple spines and high plateaus'),('03','Panterran Plateau',(1615,1110),'Dissected upland below the mountain wall'),('04','Great Reservoir',(1470,1220),'Flooded continental basin, maintained by the dam'),('05','Great Panterran Dam',(1555,1290),'Reservoir outlet at a bedrock gorge'),('06','Alluvial trade outlet',(1680,1390),'Amsterdam shorthand; delta, canals and commerce'),('07','Old-growth refuge',(1200,1110),'Wet uplands, giant trees and logging frontier'),('08','Western Gate',(1190,1000),'Lower mountain saddle; migration checkpoint'),('09','Central Gate',(1720,940),'Second low passage through Northern Divide'),('10','Eastern Gate',(2200,910),'Eastern coastal and ridge crossing'),('11','Maritime southern lowlands',(600,1550),'Wet right-hand core in the marked far-side view'),('12','Southern great range',(825,1610),'Third continental core joins the global collision belt'),('13','Drowned land bridge',(1060,1530),'Island chain and former low-sea-level migration route'),('14','Pieter’s fishing village',(1530,1308),'Proposed site beside the outlet reach'),('15','Ancient avian cliff ruins',(1135,1080),'Ruins above the western forest corridor'),('16','London / lakeshore country',(1450,1302),'Proposed lake-side city and agricultural hinterland'),('17','Merchant island',(1640,1640),'Milan shorthand; trade controls in southern strait'),('18','Great leeward desert',(2700,1320),'Dry interior on the left of the marked far-side view'),('19','Eastern rift gulf',(2510,1200),'Fault-bounded gulf opening into the southern sea'),('20','Southern shelf gulf',(775,1550),'Drowned failed-rift basin and broken capes'),('21','Old southern shield',(530,1515),'Old shield with deeply weathered forests and river plains'),('22','Eastern collision knot',(2310,970),'Broad transpressional uplands joining eastern terranes'),('23','Northern fjord remnant',(730,530),'Glacial valleys cut into the high-latitude remnant')]
features=[dict(id=i,name=n,lon=ll(p)[0],lat=ll(p)[1],description=t,sketch_xy=p) for i,n,p,t in features]
features.extend([
 dict(id='24',name='Seattle / upstream timber city',lon=ll((1240,1118))[0],lat=ll((1240,1118))[1],description='Primary river flows from here INTO the super-lake'),
 dict(id='25',name='Rome / eastern lake shore',lon=-2.5927734375,lat=10.6787109375,description='Proposed high-bank city overlooking the lake; distinct from the downstream metropolis'),
 dict(id='26',name='Far-side collision isthmus',lon=-172,lat=0,description='Continuous mountain land link between second and third cores'),
 dict(id='27',name='Long drowned-shelf archipelago',lon=-87,lat=-26,description='Former land bridge toward Panterra; submerged saddle chain'),
 dict(id='28',name='Arctic crown islands',lon=-80,lat=80,description='Glaciated bedrock islands and straits amid broken pack ice'),
 dict(id='29',name='South polar ice continent',lon=105,lat=-77,description='Asymmetric land ice, coastal mountains and outlet glaciers'),
 dict(id='30',name='Southern embayment',lon=-25,lat=-76,description='Deep marine inlet interrupts the south polar ice sheet')
])
next(f for f in features if f['id']=='16').update(lon=-13.9306640625,lat=8.3056640625,description='Proposed city on the southwestern lake shore; elevated above the reservoir')
json.dump(features,open(OUT/'source/features.json','w'),indent=2)
json.dump(dict(radius_km=6100,tilt_deg=23.4,orbital_year_earth_years=4000,relief_exaggeration=10,seed=49,crater_center=[clon,clat],projection='Interpretive inverse Mollweide fit to map 5; hand sketch has no defined graticule'),open(OUT/'source/planet.json','w'),indent=2)
print('Built terrain',W,H,'land fraction',land.mean(),'max elevation',height.max());print('features',[(f['id'],round(f['lon'],1),round(f['lat'],1)) for f in features])

# Revision 4 reconstructs the far-side core after the original sketch fit.
from reshape_geography import reshape
reshape(OUT)

from revise_southern_r6 import revise
revise(OUT)

from revise_r6 import revise_r6
revise_r6(OUT)

from revise_r7 import revise as natural_landforms
natural_landforms(OUT)
