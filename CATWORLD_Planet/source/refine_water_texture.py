"""An 8K colour map with antialiased vector waterways; elevation detail remains 4K."""
from pathlib import Path
import json
import numpy as np
from scipy.ndimage import distance_transform_edt,binary_dilation
from scipy.interpolate import PchipInterpolator
from PIL import Image,ImageDraw

def refine(root):
 B=Path(root);z=np.load(B/'source/terrain_fields.npz');H,W=z['land'].shape
 color=np.array(Image.open(B/'textures/albedo_4096.png'));river=z['river'];lake=z['lake'];small=z['small_lake'];land=z['land']
 erase=binary_dilation(river,iterations=2)&land&~lake&~small
 _,ix=distance_transform_edt(erase,return_indices=True)
 color[erase]=color[tuple(ix)][erase]
 # Reconstruct local ground colour beneath the former raster stroke before drawing precise curves.
 base=Image.fromarray(color).resize((W*4,H*4),Image.Resampling.BICUBIC)
 watermask=Image.new('L',base.size);d=ImageDraw.Draw(watermask)
 paths=json.load(open(B/'source/hydrology_paths.json'))
 for k,(name,pts) in enumerate(paths.items()):
  pp=np.array(pts);t=np.linspace(0,1,len(pp));tt=np.linspace(0,1,2400)
  curve=np.c_[PchipInterpolator(t,pp[:,0])(tt),PchipInterpolator(t,pp[:,1])(tt)]
  uv=np.c_[(curve[:,0]+180)/360*W*4,(90-curve[:,1])/180*H*4]
  for j in range(len(uv)-1):
   width=(1.3+1.2*tt[j] if k<3 else .65+.70*tt[j])*(1+.14*np.sin(tt[j]*35+k))
   d.line([tuple(uv[j]),tuple(uv[j+1])],fill=255,width=max(2,round(width*4)))
 # The material layer is antialiased separately from the deliberately coarser physical grid.
 wetcolour=Image.new('RGB',base.size,(7,33,40));base.paste(wetcolour,mask=watermask)
 base.resize((W*2,H*2),Image.Resampling.LANCZOS).save(B/'textures/albedo_8192.png')
 print('8K albedo, vector-refined rivers; 4K physical terrain retained',flush=True)
if __name__=='__main__':refine(Path(__file__).resolve().parents[1])
