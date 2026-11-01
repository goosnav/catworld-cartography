import bpy,json,math
from mathutils import Vector
from pathlib import Path
B=Path(__file__).resolve().parents[1]
bpy.ops.wm.open_mainfile(filepath=str(B/'model/CATWORLD_Terra.blend'))
s=bpy.context.scene;key=bpy.data.objects['Broad daylight'];fill=bpy.data.objects['Soft atmospheric fill'];vs=json.load(open(B/'source/views.json'))
features=json.load(open(B/'source/features.json'))
def xyz(lo,la):
 a,b=math.radians(lo),math.radians(la);return Vector((10.1*math.cos(b)*math.cos(a),10.1*math.cos(b)*math.sin(a),10.1*math.sin(b)))
for f in features:
 e=next(o for o in bpy.data.collections['LANDMARKS | named geographic anchors'].objects if o.name.startswith(f['id']+' |'));e.location=xyz(f['lon'],f['lat']);e['longitude']=f['lon'];e['latitude']=f['lat']
for i,v in enumerate(vs):
 c=bpy.data.objects[v['name']]
 from bpy_extras.object_utils import world_to_camera_view
 v['flowpaths']={}
 for name,points in json.load(open(B/'source/hydrology_paths.json')).items():
  v['flowpaths'][name]=[]
  for lo,la in points:
   a,b=math.radians(lo),math.radians(la);pt=Vector((10.1*math.cos(b)*math.cos(a),10.1*math.cos(b)*math.sin(a),10.1*math.sin(b)));uv=world_to_camera_view(s,c,pt);v['flowpaths'][name].append([uv.x,1-uv.y])
 v['features']=[]
 for f in features:
  pt=xyz(f['lon'],f['lat']);uv=world_to_camera_view(s,c,pt);visible=pt.normalized().dot(c.location.normalized())>.10 and 0<uv.x<1 and 0<uv.y<1;v['features'].append(dict(**f,x=uv.x,y=1-uv.y,visible=bool(visible)))
 direction=c.location.normalized();right=c.rotation_euler.to_matrix()@Vector((1,0,0));up=c.rotation_euler.to_matrix()@Vector((0,1,0))
 key.location=direction*20-right*10+up*13;key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler();fill.location=direction*16+right*12-up*3;fill.rotation_euler=(-fill.location).to_track_quat('-Z','Y').to_euler()
 for o in [key,fill]:
  o.keyframe_insert(data_path='location',frame=i+1);o.keyframe_insert(data_path='rotation_euler',frame=i+1)
json.dump(vs,open(B/'source/views.json','w'),indent=2)
s.frame_start=1;s.frame_end=len(vs);s.frame_set(1);s.camera=bpy.data.objects['01_panterra'];bpy.context.view_layer.update()
# Keep the atlas easy to inspect; select the surface, not one of the lights.
bpy.ops.object.select_all(action='DESELECT');globe=bpy.data.objects['TERRA | radius 6100 km | 10x relief'];globe.select_set(True);bpy.context.view_layer.objects.active=globe
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':
  a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL';a.spaces.active.overlay.show_overlays=False
s['Atlas revision']=9;s['World radius km']=6100;s['Orbital period Earth years']=4000;s['Axial tilt degrees']=35;s['Render relief exaggeration']=10;s['Source']='Map 5, hand reconstruction, revised silhouette and all-continent terrain';s['Cameras']='Frames 1-13 select the thirteen globe views, with matching lights.'
# A plain-text start note travels inside the blend.
t=bpy.data.texts.get('READ ME') or bpy.data.texts.new('READ ME');t.clear();t.write('CATWORLD TERRA\n\nFrames 1-13 select atlas cameras and their lighting. Numpad 0 toggles camera view. Orbit normally for other angles.\n\nSurface texture is packed. Radius 6100 km. Display sphere radius 10 units. Radial relief exaggerated 10x.\n\nThe dam is below globe resolution; open CATWORLD_Dam_Study.blend for the local inset.\n\nSee Geography_and_Design.md and the PDF for provenance, proposed tectonics, 4000-year seasons and limitations.\n')
report={'globe_vertices':len(globe.data.vertices),'globe_quads':len(globe.data.polygons),'geographic_landmarks':len(bpy.data.collections['LANDMARKS | named geographic anchors'].objects),'atlas_cameras':len(vs),'timeline_markers':len(s.timeline_markers),'packed_images':[{ 'name':i.name,'packed':bool(i.packed_file),'size':list(i.size)} for i in bpy.data.images if i.type=='IMAGE'],'default_camera':s.camera.name,'default_frame':s.frame_current}
assert report['atlas_cameras']==13 and report['geographic_landmarks']==39
assert all(i['packed'] for i in report['packed_images'])
json.dump(report,open(B/'source/Model_Verification.json','w'),indent=2)
bpy.ops.wm.save_as_mainfile(filepath=str(B/'model/CATWORLD_Terra.blend'))
print(report)
