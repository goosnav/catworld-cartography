"""Planar polar texture fields avoid longitude pinching in the Arctic sea ice."""
import numpy as np
from scipy.ndimage import map_coordinates,gaussian_filter,zoom,distance_transform_edt

def northern_ice(z,color,reference,lon,lat):
 land=z['land'];ocean=~land&~z['lake'];redwater=ocean&(lat>50)&(np.abs(lon)<40)&(reference[...,0]>.06)&(reference[...,0]>reference[...,1]*1.4)
 # Restore the entire mineral basin, not a circular approximation that cuts wedges into it.
 color[redwater]=reference[redwater]
 coast=distance_transform_edt(~np.pad(land,((0,0),(128,128)),mode='wrap'))[:,128:-128]
 sea=np.zeros_like(color)+[.012,.052,.095];sea+=np.exp(-coast/10)[...,None]*[.014,.12,.12]
 clear=ocean&(lat>65)&~redwater;color[clear]=sea[clear]
 px=np.cos(np.radians(lat))*np.cos(np.radians(lon));py=np.cos(np.radians(lat))*np.sin(np.radians(lon));coords=[256+py*650,256+px*650]
 rng=np.random.default_rng(5059)
 def field(n):
  a=zoom(rng.standard_normal((n,n)).astype('f'),512/n,order=3);a=(a-a.mean())/a.std();return map_coordinates(a,coords,order=1,mode='reflect')
 coarse=field(18);fine=field(110);micro=field(230)
 edge=73+2.3*np.sin(np.radians(lon)*2)+1.4*np.cos(np.radians(lon)*3)+.7*coarse
 amount=np.clip((lat-edge)/2,0,1);amount=amount*amount*(3-2*amount)
 # Interlocking floes with narrow irregular leads, mapped in polar Cartesian coordinates.
 lead=np.clip(1-np.abs(fine+.35*coarse)/.10,0,1)
 ice=np.zeros_like(color)+[.72,.80,.83];ice+=(.025*coarse+.017*micro)[...,None]
 mix=amount*(.89-.65*lead);pack=ocean&(lat>edge)&~redwater;color[pack]=color[pack]*(1-mix[pack,None])+ice[pack]*mix[pack,None]
 shore=redwater&(coast<5)&(lat>62)&(fine>-.5);color[shore]=[.66,.72,.75]
 return color
