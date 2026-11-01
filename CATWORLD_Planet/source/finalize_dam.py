import bpy,json
from pathlib import Path
from mathutils import Vector
B=Path(__file__).resolve().parents[1];bpy.ops.wm.open_mainfile(filepath=str(B/'model/CATWORLD_Dam_Study.blend'));s=bpy.context.scene
for marker in list(s.timeline_markers):s.timeline_markers.remove(marker)
for i,(name,loc,target,scale) in enumerate([('09_dam_valley',(4,-8,16),(0,1.8,.2),13),('10_dam_detail',(1,-6,6),(0,.3,.5),6.3)]):
 o=bpy.data.objects.get(name)
 if o is None:
  data=bpy.data.cameras.new(name);o=bpy.data.objects.new(name,data);s.collection.objects.link(o)
 o.location=loc;o.rotation_euler=(Vector(target)-o.location).to_track_quat('-Z','Y').to_euler();o.data.type='ORTHO';o.data.ortho_scale=scale;s.timeline_markers.new(name,frame=i+1).camera=o
s.frame_start=1;s.frame_end=2;s.frame_set(1);s.camera=bpy.data.objects['09_dam_valley'];s['Atlas revision']=6
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.overlay.show_overlays=False
bpy.ops.wm.save_as_mainfile(filepath=str(B/'model/CATWORLD_Dam_Study.blend'))
json.dump({'revision':6,'saved_cameras':['09_dam_valley','10_dam_detail'],'frames':[1,2],'unit_scale_m':s.unit_settings.scale_length,'default_camera':s.camera.name},open(B/'source/Dam_Model_Verification.json','w'),indent=2)
