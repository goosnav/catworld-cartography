"""Geographic acceptance checks for the whole-plate correction, using delivered terrain."""
from pathlib import Path
import numpy as np,json
from scipy.ndimage import map_coordinates,label
from scipy.interpolate import PchipInterpolator
from revise_r10 import R,east_forward,spine
B=Path(__file__).resolve().parents[1];z=np.load(B/'source/terrain_fields.npz');H,W=z['land'].shape
p=np.array(spine());x=np.linspace(22,125,240);y=PchipInterpolator(p[:,0],p[:,1])(x)
assert np.all(np.diff(y)<=1e-8),'Orogen reverses northward'
coords=[(90-y)/180*H-.5,(x+180)/360*W-.5]
assert map_coordinates(z['land'],coords,order=0).all(),'Mountain connection crosses open water'
cross=[]
for offset in np.linspace(-3.5,3.5,81):cross.append(map_coordinates(z['surface'],[(90-y-offset)/180*H-.5,(x+180)/360*W-.5],order=1))
maxima=np.max(cross,axis=0);assert maxima.min()>4000,('Break in high range',maxima.min())
assert np.max(abs(R.T@R-np.eye(3)))<1e-12
# Pairwise geodesic distances across far-separated points must remain invariant.
q=np.array([[50,34],[80,25],[115,15],[130,-8],[110,-25],[75,-8]],float);lo,la=east_forward(q[:,0],q[:,1]);rot=np.c_[lo,la]
def dist(p):
 a,b=np.radians(p).T;v=np.c_[np.cos(b)*np.cos(a),np.cos(b)*np.sin(a),np.sin(b)];return np.arccos(np.clip(v@v.T,-1,1))*6100
mask=~np.eye(len(q),dtype=bool);error=float(np.max(abs(dist(q)-dist(rot))[mask]));assert error<1e-7
# The ridge centerline is one connected land component, independent of the mesh/camera setup.
lab,_=label(z['land']);ids=map_coordinates(lab,coords,order=0);assert len(set(ids))==1 and ids[0]>0
r=dict(revision=10,rigid_rotation_degrees=23,pairwise_geodesic_error_km=error,range_reverses_north=False,suture_land_fraction=1.,minimum_cross_section_peak_m=float(maxima.min()),minimum_sampled_centerline_m=float(map_coordinates(z['surface'],coords,order=1).min()),continuous_land_component=int(ids[0]))
# If the development baseline is present, verify protected story terrain was retained exactly.
old=B.parent/'CATWORLD_Planet_R9/source/terrain_fields.npz'
if old.exists():
 original=np.load(old);yy,xx=np.mgrid[:H,:W];lat=90-(yy+.5)*180/H;lon=(xx+.5)*360/W-180
 protect=original['land']&(lon>-60)&(lon<19)&(lat>-35)&(lat<58)
 delta=float(abs(z['surface'][protect]-original['surface'][protect]).max());assert delta==0;r['protected_panterra_max_elevation_change_m']=delta
baseline=B.parent/'CATWORLD_Planet_R8/source/terrain_fields.npz'
if baseline.exists():
 original=np.load(baseline);lat=90-(np.arange(H)[:,None]+.5)*180/H;polar=np.broadcast_to(lat<-60,(H,W))
 assert np.array_equal(z['land'][polar],original['land'][polar]),'Polar coastline changed outside the eastern edit'
 polarland=polar&original['land'];delta=float(abs(z['surface'][polarland]-original['surface'][polarland]).max());assert delta==0
 r['southern_polar_coast_unchanged']=True;r['southern_polar_max_elevation_change_m']=delta
json.dump(r,open(B/'source/Eastern_Plate_Verification.json','w'),indent=2);print(json.dumps(r,indent=2))
