import bpy, numpy as np, math, json, sys, os
from pathlib import Path
from mathutils import Vector
BASE=Path(__file__).resolve().parents[1]
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for dat in list(bpy.data.materials): bpy.data.materials.remove(dat)
scene=bpy.context.scene;scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
scene.render.resolution_x=2048;scene.render.resolution_y=2048;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.world.color=(.12,.12,.12)
scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.09,.12,.17,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.5
scene.view_settings.view_transform='AgX'
scene.render.film_transparent=True
# Spherical mesh, UVs explicitly assigned; geographic north is +Z, zero longitude +X.
f=np.load(BASE/'source/terrain_fields.npz');height=f['surface'];H,W=height.shape
NU,NV=1536,768
lat=np.linspace(-np.pi/2,np.pi/2,NV+1);lon=np.linspace(-np.pi,np.pi,NU+1)
la,lo=np.meshgrid(lat,lon,indexing='ij')
yi=np.clip(np.round((np.pi/2-la)/np.pi*(H-1)).astype(int),0,H-1);xi=np.clip(np.round((lo+np.pi)/(2*np.pi)*(W-1)).astype(int),0,W-1)
r=10+height[yi,xi]/6100000*10*10
verts=np.stack([r*np.cos(la)*np.cos(lo),r*np.cos(la)*np.sin(lo),r*np.sin(la)],-1).reshape(-1,3)
a=np.arange(NV)[:,None]*(NU+1)+np.arange(NU)[None,:];faces=np.stack([a,a+1,a+NU+2,a+NU+1],-1).reshape(-1,4)
mesh=bpy.data.meshes.new('Geographic terrain | 10x relief');mesh.from_pydata(verts.tolist(),[],faces.tolist());mesh.update()
obj=bpy.data.objects.new('TERRA | radius 6100 km | 10x relief',mesh);scene.collection.objects.link(obj)
uv=mesh.uv_layers.new(name='Geographic UV')
uvs=np.stack([(lo+np.pi)/(2*np.pi),(la+np.pi/2)/np.pi],-1).reshape(-1,2)
uv.data.foreach_set('uv',uvs[faces.reshape(-1)].astype('f').ravel())
for p in mesh.polygons:p.use_smooth=True
mat=bpy.data.materials.new('Satellite surface | packed 4K maps');mat.use_nodes=True;n=mat.node_tree.nodes;l=mat.node_tree.links;p=n.get('Principled BSDF')
def tex(name,space='sRGB'):
 t=n.new('ShaderNodeTexImage');t.image=bpy.data.images.load(str(BASE/'textures'/name));t.image.colorspace_settings.name=space;t.image.pack();t.interpolation='Linear';return t
col=tex('albedo_4096.png');l.new(col.outputs['Color'],p.inputs['Base Color'])
rough=tex('roughness.png','Non-Color');l.new(rough.outputs['Color'],p.inputs['Roughness'])
h=tex('height_16bit.png','Non-Color');b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.6;b.inputs['Distance'].default_value=.16;l.new(h.outputs['Color'],b.inputs['Height']);l.new(b.outputs['Normal'],p.inputs['Normal'])
p.inputs['Specular IOR Level'].default_value=.035
obj.data.materials.append(mat)
# Fine surface irregularities, restrained enough to read at globe scale.
noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1400;noise.inputs['Detail'].default_value=3
b2=n.new('ShaderNodeBump');b2.inputs['Strength'].default_value=.08;b2.inputs['Distance'].default_value=.004;l.new(noise.outputs['Fac'],b2.inputs['Height']);l.new(b.outputs['Normal'],b2.inputs['Normal']);l.new(b2.outputs['Normal'],p.inputs['Normal'])
mask=tex('land_mask.png','Non-Color');mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.08;l.new(mask.outputs['Color'],mul.inputs[0]);l.new(mul.outputs[0],b2.inputs['Strength'])
# Thin atmospheric limb, transparent at the center so coasts stay unobscured.
bpy.ops.mesh.primitive_uv_sphere_add(segments=192,ring_count=96,radius=10.19)
at=bpy.context.object;at.name='Thin atmospheric limb';am=bpy.data.materials.new('Subtle blue limb');am.use_nodes=True
an=am.node_tree.nodes;al=am.node_tree.links;an.clear();out=an.new('ShaderNodeOutputMaterial');tr=an.new('ShaderNodeBsdfTransparent');em=an.new('ShaderNodeEmission');em.inputs[0].default_value=(.035,.16,.31,1);em.inputs[1].default_value=.28
fr=an.new('ShaderNodeFresnel');fr.inputs[0].default_value=1.014;mix=an.new('ShaderNodeMixShader');al.new(fr.outputs[0],mix.inputs[0]);al.new(tr.outputs[0],mix.inputs[1]);al.new(em.outputs[0],mix.inputs[2]);al.new(mix.outputs[0],out.inputs[0]);at.data.materials.append(am)
for pp in at.data.polygons:pp.use_smooth=True
# Non-rendering landmarks make the .blend useful as an editable atlas.
fc=bpy.data.collections.new('LANDMARKS | named geographic anchors');scene.collection.children.link(fc)
features=json.load(open(BASE/'source/features.json'))
def xyz(lon,lat,r=10.1):
 a,b=math.radians(lon),math.radians(lat);return Vector((r*math.cos(b)*math.cos(a),r*math.cos(b)*math.sin(a),r*math.sin(b)))
for ftr in features:
 e=bpy.data.objects.new(f"{ftr['id']} | {ftr['name']}",None);fc.objects.link(e);e.location=xyz(ftr['lon'],ftr['lat']);e.empty_display_size=.08;e['description']=ftr['description'];e['longitude']=ftr['lon'];e['latitude']=ftr['lat']
# Camera, key and fill follow viewing direction to show geography in every reference.
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='ATLAS camera';scene.camera=cam;cam.data.type='ORTHO';cam.data.ortho_scale=22.2;cam.data.lens=50
bpy.ops.object.light_add(type='AREA');key=bpy.context.object;key.name='Broad daylight';key.data.energy=7500;key.data.shape='DISK';key.data.size=14
bpy.ops.object.light_add(type='AREA');fill=bpy.context.object;fill.name='Soft atmospheric fill';fill.data.energy=3400;fill.data.size=20
views=[('01_panterra',0,22,22.2),('02_eastern',90,0,22.2),('03_western',-90,0,22.2),('04_far_side',180,0,22.2),('05_north_pole',0,90,22.2),('06_south_pole',0,-90,22.2),('07_panterra_close',-8,15,12.5),('08_impact_close',features[0]['lon'],features[0]['lat'],10.3),('11_southern_continent',-140,-29,13.0),('12_eastern_continent',135,5,15.0),('13_seattle_waterway',-25,16,6.7),('14_archipelago',-83,-24,14.0)]
metadata=[]
for name,lon,lat,scale in views:
 direction=xyz(lon,lat,1);target=Vector((0,0,0)) if scale>20 else direction*8.7
 cam.location=direction*35;cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 right=cam.rotation_euler.to_matrix()@Vector((1,0,0));up=cam.rotation_euler.to_matrix()@Vector((0,1,0))
 key.location=direction*20-right*10+up*13;key.rotation_euler=(-key.location).to_track_quat('-Z','Y').to_euler()
 fill.location=direction*16+right*12-up*3;fill.rotation_euler=(-fill.location).to_track_quat('-Z','Y').to_euler()
 # Store all exact camera states in timeline markers for easy reuse.
 cdata=cam.data.copy();c=bpy.data.objects.new(name,cdata);scene.collection.objects.link(c);c.location=cam.location;c.rotation_euler=cam.rotation_euler;c.data.ortho_scale=scale
 bpy.context.view_layer.update()
 from bpy_extras.object_utils import world_to_camera_view
 projected=[]
 for ff in features:
  pt=xyz(ff['lon'],ff['lat']);vis=pt.normalized().dot(direction)>.10
  v=world_to_camera_view(scene,cam,pt);projected.append(dict(**ff,x=v.x,y=1-v.y,visible=bool(vis and 0<v.x<1 and 0<v.y<1)))
 flowpaths={}
 for label,points in json.load(open(BASE/'source/hydrology_paths.json')).items():
  flowpaths[label]=[]
  for lo1,la1 in points:
   v=world_to_camera_view(scene,cam,xyz(lo1,la1));flowpaths[label].append([v.x,1-v.y])
 metadata.append(dict(name=name,longitude=lon,latitude=lat,ortho_scale=scale,features=projected,flowpaths=flowpaths))
 scene.render.filepath=str(BASE/('review_draft' if '--draft' in sys.argv else 'renders')/f'{name}.png')
 if '--draft' in sys.argv:
  scene.cycles.samples=8;scene.render.resolution_percentage=40
  if name not in ['01_panterra','04_far_side','05_north_pole','06_south_pole','13_seattle_waterway','14_archipelago']:continue
 if '--preview' in sys.argv:
  scene.render.resolution_percentage=45;bpy.ops.render.render(write_still=True);break
 bpy.ops.render.render(write_still=True)
json.dump(metadata,open(BASE/'source'/('draft_views.json' if '--draft' in sys.argv else 'views.json'),'w'),indent=2)
for idx,v in enumerate(metadata):
 marker=scene.timeline_markers.new(v['name'],frame=idx+1);marker.camera=bpy.data.objects.get(v['name'])
# Opening view has Panterra facing the viewer and all texture data packed.
scene.camera=bpy.data.objects.get('01_panterra',cam)
for area in bpy.context.screen.areas:
 if area.type=='VIEW_3D':
  area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/('review_draft/CATWORLD_review.blend' if '--draft' in sys.argv else 'model/CATWORLD_Terra.blend')))
print('GLOBE_COMPLETE')
