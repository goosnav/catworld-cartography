"""Remove the residual southern island arc off the eastern continent.
Only the southern mainland's EASTERN shelf route toward Panterra remains.
"""
import numpy as np
from scipy.ndimage import label,distance_transform_edt

def open_ocean(z,color,lon,lat):
 h,w=z['land'].shape;labs,_=label(z['land']);main=labs[int((90-5)/180*h),int((120+180)/360*w)];ux=lon%360
 region=(ux>85)&(ux<171)&(lat<-18)&(lat>-60)
 remove=region&z['land']&(labs!=main)
 z['land'][remove]=False;z['lake'][remove]=False;z['surface'][remove]=0;z['wet'][remove]=0
 ocean=region&~z['land'];z['height'][ocean]=-3800
 coast=distance_transform_edt(~np.pad(z['land'],((0,0),(128,128)),mode='wrap'))[:,128:-128]
 sea=np.zeros_like(color)+[.012,.052,.095];sea+=np.exp(-coast/10)[...,None]*[.014,.12,.12];color[ocean]=sea[ocean]
 return color,int(remove.sum())
