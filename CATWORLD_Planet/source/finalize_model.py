import bpy,json,math
from mathutils import Vector
from pathlib import Path
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'model/CATWORLD_Terra.blend'))
s=bpy.context.scene;key=bpy.data.objects['Broad daylight'];fill=bpy.data.objects['Soft atmospheric fill'];vs=json.load(open(B/'source/views.json'))
for i,v in enumerate(vs):
 c=bpy.data.objects[v['name']];direction=c.location.normalized();right=c.rotation_euler.to_matrix()@Vector((1,0,0));up=c.rotation_euler.to_matrix()@Vector((0,1,0))
 key.location=direction*20-right*10+up*13;key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler();fill.location=direction*16+right*12-up*3;fill.rotation_euler=(-fill.location).to_track_quat('-Z','Y').to_euler()
 for o in [key,fill]:
  o.keyframe_insert(data_path='location',frame=i+1);o.keyframe_insert(data_path='rotation_euler',frame=i+1)
s.frame_start=1;s.frame_end=len(vs);s.frame_set(1);s.camera=bpy.data.objects['01_panterra'];bpy.context.view_layer.update()
# Keep the atlas easy to inspect; select the surface, not one of the lights.
bpy.ops.object.select_all(action='DESELECT');globe=bpy.data.objects['TERRA | radius 6100 km | 5x relief'];globe.select_set(True);bpy.context.view_layer.objects.active=globe
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL';a.spaces.active.overlay.show_overlays=False
s['World radius km']=6100;s['Orbital period Earth years']=4000;s['Axial tilt degrees']=23.4;s['Render relief exaggeration']=5;s['Source']='Map 5, hand reconstruction, revised silhouette and all-continent terrain';s['Cameras']='Frames 1-10 select the ten globe views, with matching lights.'
# A plain-text start note travels inside the blend.
t=bpy.data.texts.get('READ ME') or bpy.data.texts.new('READ ME');t.clear();t.write('CATWORLD TERRA\n\nFrames 1-10 select atlas cameras and their lighting. Numpad 0 toggles camera view. Orbit normally for other angles.\n\nSurface texture is packed. Radius 6100 km. Display sphere radius 10 units. Radial relief exaggerated 5x.\n\nThe dam is below globe resolution; open CATWORLD_Dam_Study.blend for the local inset.\n\nSee Geography_and_Design.md and the PDF for provenance, proposed tectonics, 4000-year seasons and limitations.\n')
report={'globe_vertices':len(globe.data.vertices),'globe_quads':len(globe.data.polygons),'geographic_landmarks':len(bpy.data.collections['LANDMARKS | named geographic anchors'].objects),'atlas_cameras':len(vs),'timeline_markers':len(s.timeline_markers),'packed_images':[{ 'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.type=='IMAGE'],'default_camera':s.camera.name,'default_frame':s.frame_current}
assert report['atlas_cameras']==10 and report['geographic_landmarks']==23
assert all(i['packed'] for i in report['packed_images'])
json.dump(report,open(B/'source/Model_Verification.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=str(B/'model/CATWORLD_Terra.blend'))
print(report)
