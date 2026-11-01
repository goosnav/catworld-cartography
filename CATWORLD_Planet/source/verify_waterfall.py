import bpy,json
from pathlib import Path
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'model/CATWORLD_Waterfall_Study.blend'))
s=bpy.context.scene
water=bpy.data.objects['Continuous river, 250 m main fall and lower cascades']
heights=[v.co.z*1000 for v in water.data.vertices]
assert abs(max(heights)-1090)<1 and abs(min(heights)-690)<1
assert s.unit_settings.scale_length==1000
s['Atlas revision']=8
bpy.ops.wm.save_as_mainfile(filepath=str(B/'model/CATWORLD_Waterfall_Study.blend'))
json.dump(dict(revision=8,camera=s.camera.name,unit_scale_m=s.unit_settings.scale_length,upper_river_m=max(heights),reservoir_m=min(heights),drop_m=max(heights)-min(heights),water_vertices=len(heights),water_surface='Continuous mesh with irregular caprock lips; no fluid simulation'),open(B/'source/Waterfall_Model_Verification.json','w'),indent=2)
print('WATERFALL VERIFIED')
