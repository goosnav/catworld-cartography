"""R5: detached southern continent, continental shelf migration route, late-autumn epoch.
Run once after the R4 reshape stage. The fields are art-directed, not a climate simulation.
"""
from pathlib import Path
import json,heapq
import numpy as np
from PIL import Image,ImageDraw
from scipy.ndimage import zoom,gaussian_filter,map_coordinates,distance_transform_edt,label,binary_dilation,gaussian_filter1d
CORE=[(207.0, -27), (212.75, -22), (218.5, -21), (224.25, -15), (227.7, -16), (228.85, -23), (235.75, -22), (242.65, -20), (251.85, -22), (256.45, -26), (253.0, -29), (254.15, -35), (247.25, -33), (243.8, -35), (244.95, -40), (251.85, -44), (248.4, -48), (243.8, -47), (239.2, -43), (235.75, -46), (232.3, -51), (227.7, -53), (224.25, -48), (224.25, -42), (217.35, -44), (212.75, -40), (213.9, -35), (208.15, -34), (203.55, -31)]
SPINE=[(247, -23), (248, -28), (244, -33), (240, -38), (235, -44), (230, -48)]
CHAIN=[(253, -25), (263, -25), (273, -21), (284, -17), (294, -10), (304, -2), (313, 12)]
# Latest creator correction: closer to Panterra and farther south.
SOUTH_EAST_SHIFT=16
SOUTH_LAT_SHIFT=-5
CORE=[(lo+SOUTH_EAST_SHIFT,la+SOUTH_LAT_SHIFT) for lo,la in CORE]
SPINE=[(lo+SOUTH_EAST_SHIFT,la+SOUTH_LAT_SHIFT) for lo,la in SPINE]
def shorten_shelf(points):
 return [(lo+16*float(np.clip((313-lo)/60,0,1)),la-5*float(np.clip((313-lo)/60,0,1))) for lo,la in points]
CHAIN=shorten_shelf(CHAIN)
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def revise(root):
 B=Path(root);z=dict(np.load(B/'source/terrain_fields.npz'));h,w=z['land'].shape;Y,X=np.mgrid[:h,:w];lat=90-(Y+.5)*180/h;lon=(X+.5)*360/w-180;ux=lon%360
 color=np.asarray(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255;initial_color=color.copy()
 rng=np.random.default_rng(5005)
 def noise(s):
  a=rng.standard_normal((max(4,h//s),max(8,w//s))).astype('f');return zoom(a,(h/a.shape[0],w/a.shape[1]),order=3,mode='wrap')[:h,:w]
 n1=noise(70);n2=noise(22);n3=noise(6);n4=noise(2)
 def polygon(pts,rough=1):
  im=Image.new('L',(w,h));d=ImageDraw.Draw(im)
  for sh in [-360,0,360]:d.polygon([((lo+sh+180)/360*w,(90-la)/180*h) for lo,la in pts],fill=255)
  a=np.asarray(im)>0;sd=distance_transform_edt(a)-distance_transform_edt(~a);return sd+rough*(3*n2+1.4*n3)>0
 # Remove the whole former northern maritime core and its two mountain necks.
 edge=150+4*np.sin(lat*.19)+1.6*np.sin(lat*.65)+.8*np.sin(lat*1.7)
 clear=(ux>edge)&(ux<300)&(lat>-62)&(lat<65)&((ux<250)|(lat<15))
 # Remove inherited offshore islands before drawing the shorter, tapered chain.
 old_labels,_=label(z['land']);main_label=old_labels[int((90-20)/180*h),w//2]
 inherited=(ux>295)&(ux<322)&(lat>-30)&(lat<15)&(old_labels!=main_label)
 clear|=inherited
 for k in ['land','lake']:z[k][clear]=False
 z['height'][clear]=-3100;z['surface'][clear]=0;z['wet'][clear]=0
 color[clear]=[.012,.052,.095]
 core=polygon(CORE,1.3);new=core.copy()
 # Continental fragments: long fault-aligned islands, gulf islands and an outer arc.
 outlines=[[(266.328, -23.4481), (265.8803, -22.9606), (265.2393, -22.5652), (264.1424, -22.6559), (263.0153, -23.4461), (262.1002, -23.6607), (261.1281, -24.1129), (260.2794, -24.7666), (259.2056, -25.6018), (259.6961, -26.1994), (260.4014, -26.5033), (260.8487, -26.8692), (261.7302, -26.8069), (262.4201, -27.2194), (263.6038, -27.0913), (264.5519, -26.2764), (265.4077, -25.6011), (265.455, -24.8883), (265.5667, -24.3267)], [(276.5501, -19.5277), (276.1421, -19.1948), (275.2496, -19.3985), (274.6124, -19.4439), (273.9198, -19.8623), (273.2424, -20.0663), (272.2785, -20.3785), (271.8818, -21.0199), (271.5783, -21.6165), (271.8314, -22.0131), (272.4554, -22.0799), (272.4603, -22.5787), (272.9652, -22.7539), (273.6979, -22.6876), (274.5613, -22.4664), (275.0672, -21.7207), (275.4617, -21.2189), (275.9608, -20.7256), (276.0837, -20.2466)], [(286.4599, -15.2776), (286.096, -15.0964), (285.1295, -15.6011), (284.6303, -15.6757), (283.987, -15.8313), (283.2298, -16.297), (282.2731, -16.8436), (281.9484, -17.4768), (282.0779, -17.8424), (281.9053, -18.2818), (282.2249, -18.4138), (282.2501, -18.8333), (282.6878, -19.0142), (283.6233, -18.4234), (284.3944, -17.9573), (284.9598, -17.3615), (285.346, -16.8715), (286.2608, -16.2251), (286.5158, -15.6761)], [(295.5176, -8.7266), (295.2657, -8.5986), (294.7856, -8.7676), (294.3786, -8.8499), (293.8408, -8.863), (293.2506, -9.4054), (292.7797, -9.9425), (292.5311, -10.4286), (292.7243, -10.6682), (292.4123, -11.1593), (292.3879, -11.5494), (292.7474, -11.6239), (293.1817, -11.6582), (293.863, -11.0697), (294.3368, -10.6221), (294.8732, -10.2832), (295.2495, -9.8195), (295.8519, -9.2324), (296.0222, -8.732)], [(304.0521, -0.9479), (303.8732, -0.8578), (303.7127, -0.6686), (303.2885, -0.8631), (302.7991, -1.0488), (302.3455, -1.5754), (302.1821, -2.0492), (301.878, -2.4556), (301.8131, -2.7742), (301.6333, -3.2001), (301.5528, -3.648), (302.0763, -3.4161), (302.5092, -3.2089), (302.948, -2.8656), (303.3065, -2.4725), (303.8451, -2.1785), (304.2578, -1.6809), (304.4241, -1.2377), (304.5028, -0.8512)], [(310.8381, 6.9988), (310.6839, 7.0601), (310.5913, 7.3237), (310.1973, 7.0442), (309.8222, 6.647), (309.503, 6.2561), (309.4036, 5.8937), (309.1108, 5.5216), (308.8422, 5.0699), (308.9009, 4.8418), (308.9645, 4.6005), (309.3759, 4.8636), (309.7274, 5.175), (309.9986, 5.2543), (310.3248, 5.5731), (310.7274, 5.9316), (311.0639, 6.402), (310.9603, 6.6495), (310.964, 6.8934)], [(259.3552, -28.4927), (259.2407, -28.451), (259.1122, -28.3996), (258.9422, -28.5123), (258.8379, -28.7359), (258.717, -28.8563), (258.6373, -29.0123), (258.555, -29.1856), (258.4569, -29.4164), (258.5897, -29.4794), (258.7207, -29.4949), (258.8478, -29.4835), (258.9825, -29.3807), (259.1303, -29.3996), (259.2988, -29.2795), (259.3882, -29.0792), (259.4681, -28.8899), (259.3799, -28.7755), (259.3396, -28.6757)], [(267.3788, -23.344), (267.2579, -23.3281), (267.0979, -23.4578), (266.9604, -23.5683), (266.8642, -23.7762), (266.7434, -23.9075), (266.5851, -24.0999), (266.5563, -24.2923), (266.5285, -24.4879), (266.6407, -24.5246), (266.7839, -24.4511), (266.8467, -24.5354), (266.9716, -24.4822), (267.1184, -24.4007), (267.2831, -24.239), (267.3149, -24.0069), (267.3525, -23.8374), (267.3722, -23.685), (267.3436, -23.5758)], [(270.2423, -21.4804), (270.1331, -21.4708), (270.0091, -21.6398), (269.9148, -21.6949), (269.8186, -21.7889), (269.7327, -21.9204), (269.6094, -22.0907), (269.6427, -22.2381), (269.7158, -22.3172), (269.7681, -22.3962), (269.866, -22.3751), (269.9333, -22.4661), (270.0517, -22.4677), (270.1567, -22.3086), (270.2534, -22.1672), (270.2604, -22.003), (270.2591, -21.8825), (270.3347, -21.7044), (270.298, -21.5881)], [(279.2038, -17.4401), (279.1013, -17.4404), (278.9909, -17.5869), (278.8919, -17.6555), (278.7459, -17.7288), (278.6753, -17.9393), (278.6172, -18.1489), (278.6498, -18.3097), (278.7578, -18.344), (278.7681, -18.5026), (278.8424, -18.579), (278.9499, -18.5891), (279.0836, -18.5586), (279.1696, -18.3093), (279.2277, -18.1284), (279.296, -17.9644), (279.3069, -17.804), (279.384, -17.5624), (279.338, -17.4084)], [(289.1095, -12.5915), (289.0375, -12.5922), (288.9556, -12.5956), (288.8707, -12.6868), (288.7538, -12.7794), (288.7214, -12.9727), (288.7535, -13.1216), (288.7536, -13.2595), (288.8115, -13.3246), (288.8326, -13.4656), (288.8939, -13.588), (289.0012, -13.4844), (289.0947, -13.3942), (289.1522, -13.2279), (289.1783, -13.0809), (289.2748, -12.9423), (289.2952, -12.7729), (289.2805, -12.6176), (289.2294, -12.5022)], [(298.0876, -5.5034), (298.0022, -5.5083), (297.8864, -5.4297), (297.7889, -5.5932), (297.7146, -5.786), (297.6887, -5.9968), (297.7591, -6.1462), (297.7374, -6.33), (297.7584, -6.5148), (297.8384, -6.6131), (297.9343, -6.7177), (298.0483, -6.5373), (298.1226, -6.3661), (298.2119, -6.2641), (298.2557, -6.0901), (298.3499, -5.8939), (298.3673, -5.6625), (298.2594, -5.5727), (298.1887, -5.474)], [(307.0385, 2.4401), (306.9567, 2.4262), (306.8541, 2.4389), (306.7879, 2.2987), (306.7948, 2.1161), (306.7685, 1.9859), (306.7928, 1.8639), (306.7952, 1.7192), (306.8134, 1.5319), (306.9145, 1.5292), (307.0024, 1.5438), (307.0775, 1.6268), (307.1206, 1.754), (307.2167, 1.7958), (307.2721, 1.9348), (307.2756, 2.0976), (307.2626, 2.2592), (307.1586, 2.2936), (307.0974, 2.3443)], [(312.0, 9.6269), (311.908, 9.5898), (311.8362, 9.4629), (311.7833, 9.3115), (311.8106, 9.1055), (311.7789, 8.9597), (311.7558, 8.7643), (311.8046, 8.6043), (311.8576, 8.4211), (311.9584, 8.4512), (312.0334, 8.5596), (312.1106, 8.5505), (312.1685, 8.6588), (312.2509, 8.7579), (312.3052, 8.9444), (312.2385, 9.1329), (312.1981, 9.2847), (312.1332, 9.3765), (312.0683, 9.4377)]]
 # Large rifted fragments near the mainland, smaller arc remnants toward Panterra.
 for j,pts in enumerate(outlines):
  pts=np.asarray(shorten_shelf(pts));c=pts.mean(axis=0)
  if j<6:
   scale=[1.22,1.05,.72,.48,.34,.28][j];angle=np.radians([-12,15,-9,12,-15,8][j])
   rot=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
   pts=c+(pts-c)@rot.T*scale
  else:
   # Stagger small islands across the arc rather than placing every peak on one line.
   offsets=[(.25,-.6),(-.35,.8),(.65,-.3),(-.55,.6),(.5,-.8),(-.6,.65),(.7,-.5),(-.25,.6)]
   pts=c+(pts-c)*(.90 if j<10 else .65)+np.array(offsets[j-6])
  new|=polygon(pts.tolist(),.6 if j<3 else .25)
 # Smaller asymmetric islands aligned with a remnant continental ribbon.
 for j in range(0):
  t=rng.uniform(.4,6.5);k=int(t);v=np.array(CHAIN[k+1])-CHAIN[k];p=np.array(CHAIN[k])+(t-k)*v+rng.normal(0,1.8,2);a=rng.uniform(.45,1.25);b=rng.uniform(.2,.6);ang=np.arctan2(v[1],v[0]);xx=(ux-p[0])*np.cos(ang)+(lat-p[1])*np.sin(ang);yy=-(ux-p[0])*np.sin(ang)+(lat-p[1])*np.cos(ang);th=np.arctan2(yy/b,xx/a);r=((xx/a)**2+(yy/b)**2)/(1+.24*np.sin(3*th+j)+.12*np.cos(7*th))**2;new|=r<1
 # A small northern remnant, not another northern continental mass.
 remnant=polygon([(194,54),(197,57),(201,58),(204,55),(202,52),(198,51),(196,53)],.9);new|=remnant
 z['land']|=new;z['lake'][new]=False;coast=distance_transform_edt(new)
 shore=distance_transform_edt(z['land']);easternedge=(ux>139)&(ux<165)&(lat>10)&(lat<45)&z['land'];taper=np.minimum(shore/6,1);z['height'][easternedge]*=taper[easternedge];z['surface'][easternedge]*=taper[easternedge]
 # Ancient shield, sandstone basins and rejuvenated eastern escarpment.
 center=np.interp(-lat,[-q[1] for q in SPINE],[q[0] for q in SPINE]);trans=ux-center
 dem=np.load(B/'source/mountain_analogue_dem.npy');dh,dw=dem.shape;relief=dem-gaussian_filter(dem,60)
 detail=map_coordinates(relief,[(trans*43+dh*.5).ravel(),((-lat-15)/48*(dw-1)).ravel()],order=1,mode='reflect').reshape(h,w)
 belt=np.exp(-(trans/2.7)**2)*smooth((-lat-18)/8)*smooth((58+lat)/9)
 elev=230+140*n1+75*n2+28*n3+9*n4
 elev+=700*np.exp(-((ux-242)/9)**2-((lat+34)/10)**2)+420*np.exp(-((ux-253)/9)**2-((lat+39)/6)**2)
 elev+=belt*(2200+np.clip(detail,-850,1600)*1.1)
 islandridge=np.exp(-((lat-(-30+(ux-251)*.30))/4.2)**2)
 elev+=(1250+np.clip(detail,-500,1300)*.65)*islandridge*(~core)*(ux>246)*(ux<306)
 elev+=350*np.exp(-((ux-266)/9)**2-((lat+30)/12)**2)*(~core)
 elev=np.maximum(elev,35)*np.minimum(coast/5,1);elev[remnant]=500+300*np.maximum(n2[remnant],0)
 z['height'][new]=elev[new];z['surface'][new]=elev[new]
 # Recessed shelf joins the old mainland to the surviving archipelago and Panterra.
 dist=np.full((h,w),1000.,dtype='f')
 for a,b in zip(CHAIN[:-1],CHAIN[1:]):
  vx,vy=np.array(b)-a;t=np.clip(((ux-a[0])*vx+(lat-a[1])*vy)/(vx*vx+vy*vy),0,1);dist=np.minimum(dist,np.hypot((ux-a[0]-t*vx)*.82,lat-a[1]-t*vy))
 shelf=(dist<2.1)&~z['land'];bed=-38-14*smooth(dist/2.1)+4*np.sin(ux*.63)+2*n3
 z['height'][shelf]=np.maximum(z['height'][shelf],bed[shelf]);z['surface'][shelf]=0
 # Regional climates: dry subtropical west/interior, rainy eastern seaboard, cool wet southwest.
 wet=.22+.045*n1+.04*n2
 wet+=.52*smooth((ux-center+4)/7)*core
 wet+=.42*smooth((-lat-36)/9)*np.exp(-coast/75)*core
 wet+=.34*(~core);wet+=.12*np.exp(-coast/35);wet=np.clip(wet,.12,.92)
 z['wet'][new]=wet[new]
 sand=np.stack([.61+.035*n2,.405+.032*n2,.23+.023*n2],-1);forest=np.stack([.11+.018*n3,.245+.026*n3,.12+.015*n3],-1);grass=np.stack([.36+.02*n3,.38+.02*n3,.19+.02*n3],-1)
 g=smooth((wet-.23)/.24);f=smooth((wet-.48)/.3);nc=sand*(1-g[...,None])+grass*g[...,None];nc=nc*(1-f[...,None])+forest*f[...,None]
 # Interior ergs, pale endorheic pans and weathered stony ranges.
 erg=np.exp(-((ux-245)/9)**2-((lat+33)/6)**2)*core
 nc+=(.012*np.sin(X*.6+n2*5)*erg)[...,None]*np.array([1,.8,.5])
 for pts in [[(227,-31),(230,-30),(232,-32),(231,-35),(228,-34)],[(218,-28),(220,-26),(222,-28),(221,-30)]]:
  pan=polygon([(lo+16,la-5) for lo,la in pts],.5)&core;amount=np.clip(distance_transform_edt(pan)/6,0,.75);nc=nc*(1-amount[...,None])+np.array([.71,.66,.5])*amount[...,None]
 rock=np.clip((elev-1350)/2200,0,.8);nc=nc*(1-rock[...,None])+np.array([.40,.39,.33])*rock[...,None]
 snowline=3900-smooth((-lat-30)/25)*2400;snow=smooth((elev-snowline+70*n3)/500);nc=nc*(1-snow[...,None])+np.array([.86,.9,.92])*snow[...,None]
 gy,gx=np.gradient(elev);shade=np.clip((1-.008*gx+.013*gy)/np.sqrt(1+(.02*gx)**2+(.02*gy)**2),.55,1.2);nc*=1+(shade[...,None]-1)*np.clip(elev[...,None]/3500,.12,.9)
 nc+=(.009*n3+.007*n4)[...,None]
 # Priority-flood drainage for the new continental surface.
 step=3;hm=np.roll(z['surface'],w//2,axis=1)[::step,::step].copy();nm=np.roll(new,w//2,axis=1)[::step,::step];lm=np.roll(z['land'],w//2,axis=1)[::step,::step];ny,nx=hm.shape;visited=~nm;parent=np.full(ny*nx,-1,dtype='i');order=[];heap=[]
 for yy,xx in zip(*np.where(nm&binary_dilation(~lm,structure=np.ones((3,3))))):visited[yy,xx]=True;heapq.heappush(heap,(float(hm[yy,xx]),yy*nx+xx))
 while heap:
  hh,j=heapq.heappop(heap);order.append(j);yy,xx=divmod(j,nx)
  for ddy,ddx in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]:
   sy,sx=yy+ddy,xx+ddx
   if sy<0 or sy>=ny or sx<0 or sx>=nx or visited[sy,sx]:continue
   visited[sy,sx]=True;k=sy*nx+sx;parent[k]=j;hm[sy,sx]=max(hm[sy,sx],hh+.04);heapq.heappush(heap,(float(hm[sy,sx]),k))
 acc=np.ones(ny*nx,dtype='f')
 for j in reversed(order):
  if parent[j]>=0:acc[parent[j]]+=acc[j]
 im=Image.new('L',(w,h));d=ImageDraw.Draw(im);active=(acc>=65)&(parent>=0)&nm.ravel();incoming=np.zeros(ny*nx,dtype='i')
 for j in np.where(active)[0]:incoming[parent[j]]+=1
 for start in np.where(active&(incoming!=1))[0]:
  route=[int(start)];j=int(start)
  while parent[j]>=0:
   j=int(parent[j]);route.append(j)
   if incoming[j]!=1 or not active[j]:break
  if len(route)<2:continue
  pts=np.array([(((j%nx)*step-w//2)%w,(j//nx)*step) for j in route],dtype='f')
  if np.any(np.abs(np.diff(pts[:,0]))>w/2):continue
  if len(pts)>4:
   old=pts.copy();pts=gaussian_filter1d(pts,1.4,axis=0,mode='nearest');pts[0]=old[0];pts[-1]=old[-1]
  d.line([tuple(q) for q in pts],fill=140,width=2 if acc[start]>1000 else 1)
 rivers=np.asarray(im,dtype='f')/255*new
 # Arid channels are dry washes; permanent blue is confined to humid coastal catchments.
 stream=np.where((wet>.47)[...,None],np.array([.025,.12,.15]),np.array([.35,.28,.18]));nc=nc*(1-rivers[...,None]*.5)+stream*rivers[...,None]*.5;color[new]=nc[new]
 # Present epoch: Ls=255 deg, northern late autumn / southern late spring.
 northern=z['land']&(lat>38)&~z['lake'];snowline_n=np.interp(lat,[38,45,55,65,75,90],[3800,2500,1100,200,0,0]);frost=smooth((z['surface']-snowline_n+180*n2)/550)*northern
 seasonal=smooth((lat-39)/17)*.18*northern;color=color*(1-seasonal[...,None])+np.array([.34,.30,.21])*seasonal[...,None]
 color=color*(1-frost[...,None]*.86)+np.array([.81,.86,.90])*frost[...,None]*.86
 # Preserve the red lake's open centre while adding broken shore ice.
 blood=(np.hypot((lon-1.8)*.43,lat-65)<8)&~z['land'];distland=distance_transform_edt(~z['land']);lakeice=blood&(distland<5)&(lat>62)&(n3>-.2);color[lakeice]=[.65,.71,.73]
 ocean=~z['land']&~z['lake'];coastsea=distance_transform_edt(~np.pad(z['land'],((0,0),(128,128)),mode='wrap'))[:,128:-128];shallow=np.exp(-coastsea/10);sea=np.zeros_like(color)+[.012,.052,.095];sea+=shallow[...,None]*[.014,.12,.12]
 redistrict=clear|((lat<-60)&ocean)|((lat>65)&ocean&~blood);color[redistrict&ocean]=sea[redistrict&ocean]
 weight=np.clip(1-dist/2.2,0,1)*shelf;color=color*(1-weight[...,None]*.22)+np.array([.026,.16,.19])*weight[...,None]*.22
 # Northern pack expands, southern pack retreats; grounded southern ice survives spring.
 from seasonal_ice import northern_ice
 color=northern_ice(z,color,initial_color,lon,lat)
 southpack=ocean&(lat<-79+2*n1)&(n3>.3);color[southpack]=[.57,.7,.77]
 from open_eastern_ocean import open_ocean
 color,removed_arc_pixels=open_ocean(z,color,lon,lat)
 for k in ['height','surface','wet']:z[k]=z[k].astype('f')
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 Image.fromarray(np.uint8(np.clip(color,0,1)*255)).save(B/'textures/albedo_4096.png');Image.fromarray(np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)).save(B/'textures/height_16bit.png');Image.fromarray(np.uint8(np.where(z['lake'],.25,np.where(z['land'],.86,.30))*255)).save(B/'textures/roughness.png');Image.fromarray(np.uint8(z['land'])*255).save(B/'textures/land_mask.png')
 features=json.load(open(B/'source/features.json'))
 anchors={'11':(-140,-30,'Southern coastal river country','Warm eastern coastal catchments; southern late spring'),'12':(-139,-34,'Eastern escarpment','Rejuvenated old margin; distinct from the northern collision belt'),'20':(-125,-24,'Eastern shelf archipelago','Large continental fragments, drowned valleys and narrow sounds'),'21':(-163,-28,'Old southern shield','Dry sandstone basins, weathered uplands and salt pans'),'26':(169,-5,'Deep separating ocean','Open water separates the eastern core from the southern continent'),'27':(-100,-18,'Drowned migration shelf','Former dry crossing at illustrative sea level 65 m lower'),'13':(-57,-1,'Panterran shelf approach','Flooded final approach of the proposed cat migration route'),'23':(-161,55,'Northern remnant island','Small isolated glacial remnant; cooling into winter')}
 for f in features:
  if f['id'] in anchors:
   lo,la,name,desc=anchors[f['id']];f.update(lon=lo,lat=la,name=name,description=desc)
 json.dump(features,open(B/'source/features.json','w'),indent=2)
 p=json.load(open(B/'source/planet.json'));p.update(revision=5,geographic_revision='Detached southern continent and eastern shelf archipelago; main/eastern mountain link retained',seasonal_epoch={'solar_longitude_deg':255,'north':'late autumn; early winter conditions at high latitude','south':'late spring; approaching summer','years_since_northern_autumn_equinox':833,'years_until_northern_winter_solstice':167,'assumptions':'near-circular orbit, 24-hour rotation, habitable heat source unresolved'},migration_scenario={'old_homeland':'southern continent, proposed identification','lowstand_m':-65,'illustrative_crossing_years_before_present':1100,'mechanism':'southern grounded-ice storage; later net loss floods shelf','not_simulated':'ice mass, global sea level history and climate require further validation'})
 json.dump(p,open(B/'source/planet.json','w'),indent=2)
 shift=0
 def components(mask):
  labs,count=label(mask);parent=np.arange(count+1)
  def find(i):
   while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
   return i
  for a,b in zip(labs[:,0],labs[:,-1]):
   if a and b:parent[find(b)]=find(a)
  table=np.array([find(i) for i in range(count+1)]);return table[labs]
 def val(a,lo,la):return int(a[int((90-la)/180*h),(int((lo+180)/360*w)+shift)%w])
 points=[(0,20),(120,5),(-114,-38)];lab=components(z['land']);ids=[val(lab,*q) for q in points];assert ids[0]==ids[1] and ids[2]>0 and ids[2]!=ids[0],ids
 low=components(z['land']|(z['height']>=-65));lowids=[val(low,*q) for q in points];assert len(set(lowids))==1 and lowids[0]>0,lowids
 area=6100**2*np.pi/h*2*np.pi/w*np.cos(np.radians(lat));report={'revision':5,'panterra_western_coast_preserved':True,'eastern_southern_ocean_has_no_island_arc':True,'removed_eastern_arc_pixels':removed_arc_pixels,'core_anchors':[dict(lon=lo,lat=la,component=i) for (lo,la),i in zip(points,ids)],'main_and_east_connected':True,'southern_core_separate':True,'south_polar_land_separate':val(lab,105,-77) not in ids,'historical_shelf_connected_at_minus65m':True,'lowstand_components':lowids,'southern_mainland_area_km2':float(area[core].sum()),'core_polygon':CORE,'eastern_range_spine':SPINE,'historical_shelf_centerline':CHAIN,'seasonal_epoch':p['seasonal_epoch'],'new_drainage_routed_cells':len(order)}
 json.dump(report,open(B/'source/Geography_Verification.json','w'),indent=2);print(json.dumps(report,indent=2))
if __name__=='__main__':revise(Path(__file__).resolve().parents[1])
