"""Rigid spherical eastern-plate placement and reconstructed continuous orogen.
Input: R8 terrain. R9 ocean islands are regenerated without its elastic eastern warp.
Physical heights are metres; generated orogen is a landform design, not an erosion simulation.
"""
from pathlib import Path
import json
import numpy as np
from PIL import Image
from scipy.ndimage import map_coordinates, gaussian_filter, distance_transform_edt, binary_dilation, zoom
from scipy.interpolate import PchipInterpolator
B=Path(__file__).resolve().parents[1]
ANGLE=-23.0
PIVOT=(30.,37.)
def smooth(x):
 x=np.clip(x,0,1);return x*x*(3-2*x)
def rotation_matrix():
 lo,la=np.radians(PIVOT);k=np.array([np.cos(la)*np.cos(lo),np.cos(la)*np.sin(lo),np.sin(la)])
 a=np.radians(ANGLE);K=np.array([[0,-k[2],k[1]],[k[2],0,-k[0]],[-k[1],k[0],0]])
 return np.eye(3)*np.cos(a)+(1-np.cos(a))*np.outer(k,k)+np.sin(a)*K
R=rotation_matrix()
def east_forward(lo,la,inverse=False):
 a,b=np.radians(lo),np.radians(la);v=np.stack([np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)],-1)
 q=v@(R if inverse else R.T)
 return np.degrees(np.arctan2(q[...,1],q[...,0])),np.degrees(np.arcsin(np.clip(q[...,2],-1,1)))
def spine():
 from revise_r6 import east_transform
 p=[(20.,37.),(30.,37.)]
 for lo,la in [(45,37),(55,37),(72,35),(95,30),(122,27),(145,23)]:
  if lo>54.58:lo,la=east_transform(lo,la)
  x,y=east_forward(lo,la);p.append((float(x),float(y)))
 return p

def revise():
 # Snapshot intact R8 terrain, before the rejected warp. Rotate coordinates once.
 original=dict(np.load(B/'source/terrain_fields.npz'));fs=json.load(open(B/'source/features.json'))
 import revise_r9
 revise_r9.revise(apply_east=False)
 z=dict(np.load(B/'source/terrain_fields.npz'));c=np.array(Image.open(B/'textures/albedo_4096.png'),dtype='f')/255
 H,W=z['land'].shape;gy,gx=np.mgrid[:H,:W];lats=(90-(gy+.5)*180/H).astype('f');lons=((gx+.5)*360/W-180).astype('f')
 # Crop a work window, keeping Panterra's drainage, the crater, other continents and islands intact.
 ys=slice(int((90-55)/180*H),int((90+72)/180*H));xs=slice(int((20+180)/360*W),int((164+180)/360*W))
 lo=lons[ys,xs];la=lats[ys,xs];sh=lo.shape
 slo,sla=east_forward(lo,la,inverse=True);coords=[(90-sla)/180*H-.5,(slo+180)/360*W-.5]
 select=(slo>44)&(slo<165)&(sla<49)&(sla>-60)
 rotated={k:map_coordinates(v,coords,order=0 if v.dtype==bool else 1,mode='nearest') for k,v in original.items()}
 moved=rotated['land']&select
 # Erase only the old plate and old neck footprint, not a rectangular patch of the map.
 oldplate=original['land'][ys,xs]&(lo>44)&(la<49)&(la>-60)
 # Keep existing neck relief until the blended coast mask is evaluated.
 # Clearing it first created an artificial meridian seam in both height and colour.
 erase=oldplate.copy()
 for k in ['land','lake','small_lake','river']:z[k][ys,xs][erase]=False
 z['height'][ys,xs][erase]=-2200;z['surface'][ys,xs][erase]=0;c[ys,xs][erase]=[.015,.066,.105]
 for k in z:z[k][ys,xs][moved]=rotated[k][moved]
 # Smoothly descending suture. The plate does not fold, shear or change its scale.
 p=np.array(spine());center=PchipInterpolator(p[:,0],p[:,1],extrapolate=True)(lo)
 cross=la-center
 rng=np.random.default_rng(10010)
 def noise(scale):
  a=rng.normal(size=(max(4,sh[0]//scale),max(4,sh[1]//scale))).astype('f')
  return zoom(a,(sh[0]/a.shape[0],sh[1]/a.shape[1]),order=3)[:sh[0],:sh[1]]
 n0,n1,n2,n3=[noise(s) for s in [85,27,8,3]]
 # Irregular coastal foothills grow around the new suture and merge into both plates.
 width=6.0+.6*np.sin((lo-28)/8)+.32*n1+.13*n2
 neck=(abs(cross)<width)&(lo>20)&(lo<61)
 patch=z['land'][ys,xs];patch|=neck
 # Morph signed coast distances across the join, avoiding a clipped meridian edge.
 goal=moved|neck
 oldmask=original['land'][ys,xs]
 sd0=distance_transform_edt(oldmask)-distance_transform_edt(~oldmask)
 sd1=distance_transform_edt(goal)-distance_transform_edt(~goal)
 blend=smooth((lo-20)/24)
 coastmix=gaussian_filter(sd0*(1-blend)+sd1*blend,1.0)+.45*n2+.2*n3
 joinzone=(lo<61)&(lo>20)&(la<44)&(la>12)
 patch[joinzone]=coastmix[joinzone]>0
 erase|=oldmask&~patch
 for k in ['lake','small_lake','river']:z[k][ys,xs][~patch]=False
 z['height'][ys,xs][erase&~patch]=-2200
 new=patch&~(moved|(~erase&original['land'][ys,xs]))
 coast=distance_transform_edt(patch)
 dem=np.load(B/'source/mountain_analogue_dem.npy').astype('f');dh,dw=dem.shape;dr=dem-gaussian_filter(dem,75)
 # Bounded physical relief samples. Coordinates have uniform along/across-range scales;
 # they are not the inverse of an elastic deformation of the old mountains.
 # Follow the rugged Himalayan front within the DEM instead of sampling its flat foreland.
 dc=np.array([90,256,512,768,1024,1280,1536,1792,2048,2304,2460.])
 dridge=np.array([75,165,405,610,790,905,935,910,815,660,510.])
 midcol=100+(lo-20)/117*2300;curve=PchipInterpolator(dc,dridge);midrow=curve(midcol);slope_dem=curve.derivative()(midcol);normal=np.sqrt(1+slope_dem*slope_dem)
 row=midrow-cross*23/normal;col=midcol+cross*23*slope_dem/normal
 rough=map_coordinates(dr,[np.clip(row,1,dh-2),np.clip(col,1,dw-2)],order=1,mode='nearest')
 old=z['height'][ys,xs].copy();old[new]=400
 base=np.maximum(old,25)
 band=np.exp(-(cross/(5.4+.45*n0))**4)
 strength=smooth((lo-18)/22)*smooth((133-lo)/8)*band
 target=4800+2.8*rough+380*n0+210*n1+60*n2
 target=np.clip(target,1400,10000)
 mountain=base*(1-strength)+target*strength
 # Newly joined slopes rise from coastal lowlands through hills into the same high range.
 joinfresh=new
 bridge=380+np.maximum(0,target-380)*np.exp(-(cross/5.2)**2)
 mountain[joinfresh]=bridge[joinfresh]
 mountain=np.clip(mountain,25,10300)*smooth(coast/7)+15*(1-smooth(coast/7))
 change=(moved|neck|new|(strength>.02))&patch
 # Blend the rebuilt range into Panterra over a broad transition, without modifying its rivers.
 amount=np.maximum(moved.astype('f'),np.maximum(neck.astype('f'),strength))*smooth((lo-18)/22)
 amount=np.where(new,1,amount)*change
 final=old*(1-amount)+mountain*amount
 z['height'][ys,xs][change]=final[change];z['surface'][ys,xs][change]=final[change]
 for k in ['lake','small_lake','river']:z[k][ys,xs][change]=False
 # Recompute ground colour, relief lighting and snow at the NEW latitude; no rotated baked white smear.
 wet=np.where(moved,rotated['wet'],.32)+.035*n0+.025*n1
 wet=np.clip(wet,.12,.86);z['wet'][ys,xs][change]=wet[change]
 green=smooth((wet-.28)/.34);sand=np.array([.46,.355,.225]);grass=np.array([.29,.345,.19]);steppe=np.array([.40,.385,.265])
 mix=smooth((wet-.15)/.20);color=sand*(1-mix[...,None])+steppe*mix[...,None];color=color*(1-green[...,None])+grass*green[...,None]
 forest=smooth((wet-.58)/.20)*smooth((3000-final)/1800);color=color*(1-forest[...,None])+np.array([.10,.23,.13])*forest[...,None]
 color+=(.016*n0+.012*n1+.006*n2)[...,None]*[1,.9,.65]
 rock=smooth((final-2200)/2700)*.86;color=color*(1-rock[...,None])+np.array([.385,.365,.31])*rock[...,None]
 dy,dx=np.gradient(gaussian_filter(np.maximum(final,0),.75));slope=np.hypot(dx,dy)
 snowline=np.where(la>=0,5100-75*np.maximum(la-25,0),5350-90*np.maximum(-la-42,0))+180*n0+130*n1
 snow=smooth((final-snowline)/1100)*(1-.65*smooth((slope-170)/430))
 color=color*(1-snow[...,None])+np.array([.79,.84,.86])*snow[...,None]
 shade=np.clip(1-.00055*dx+.00075*dy,.61,1.18);color*=shade[...,None];color+=(.005*n2+.003*n3)[...,None]
 oldcolor=c[ys,xs].copy();paint=amount
 painted=oldcolor*(1-paint[...,None])+color*paint[...,None];c[ys,xs][change]=painted[change]
 # Uniform ocean material near both old and new coasts, with a broad feather at the work boundary.
 sea=np.zeros_like(color)+[.015,.066,.105];off=distance_transform_edt(~patch)
 sea+=np.exp(-off/5)[...,None]*[.025,.09,.08]
 ocean=~patch;near=(binary_dilation(erase|moved|neck,iterations=25)|erase)&ocean
 c[ys,xs][near]=sea[near];z['surface'][ys,xs][ocean]=0
 apron=(off<12)&ocean&(lo>25);z['height'][ys,xs][apron]=-60-18*off[apron]**2
 polar=lats < -60
 assert np.array_equal(z['land'][polar],original['land'][polar]),'Southern polar coast changed'
 polarland=polar&original['land']
 assert np.array_equal(z['surface'][polarland],original['surface'][polarland]),'Southern polar relief changed'
 np.savez_compressed(B/'source/terrain_fields.npz',**z)
 aquatic=z['river']|z['lake']|z['small_lake']
 for name,a in [('albedo_4096.png',np.uint8(np.clip(c,0,1)*255)),('height_16bit.png',np.uint16(np.clip((z['surface']+100)/11100,0,1)*65535)),('land_mask.png',np.uint8(z['land'])*255),('roughness.png',np.uint8(np.where(aquatic,.25,np.where(z['land'],.86,.30))*255))]:Image.fromarray(a).save(B/'textures'/name)
 features=json.load(open(B/'source/features.json'));orig={f['id']:f for f in fs}
 for f in features:
  q=orig.get(f['id'])
  if q and q['id'] in ['10','18','19','22']:f['lon'],f['lat']=map(float,east_forward(q['lon'],q['lat']))
 json.dump(features,open(B/'source/features.json','w'),indent=2)
 planet=json.load(open(B/'source/planet.json'));planet.update(revision=10,geographic_revision='Rigid spherical rotation of entire eastern plate and continuous reconstructed orogen');json.dump(planet,open(B/'source/planet.json','w'),indent=2)
 # A true rotation is orthonormal and preserves all geodesic pairwise distances.
 assert np.allclose(R.T@R,np.eye(3),atol=1e-12) and abs(np.linalg.det(R)-1)<1e-12
 report=dict(revision=10,angle_degrees=ANGLE,pivot_lon_lat=PIVOT,rotation_matrix=R.tolist(),orthonormal_error=float(abs(R.T@R-np.eye(3)).max()),suture_lon_lat=spine(),method='Rigid spherical plate rotation; fresh bounded DEM relief, cross-range foothills and latitude-aware materials at junction',source='Intact R8 terrain, with R9 ocean additions retained',new_continental_cells=int(new.sum()))
 json.dump(report,open(B/'source/Eastern_Plate_R10.json','w'),indent=2)
 print('R10 EASTERN PLATE COMPLETE',flush=True)
if __name__=='__main__':revise()
