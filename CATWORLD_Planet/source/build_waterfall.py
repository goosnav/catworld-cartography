"""Editable regional waterfall study: kilometre units; no vertical exaggeration."""
import bpy,math,random,json
from mathutils import Vector,noise
from pathlib import Path
B=Path(__file__).resolve().parents[1];random.seed(606)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=24;s.cycles.use_denoising=True;s.render.resolution_x=2400;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.unit_settings.system='METRIC';s.unit_settings.scale_length=1000
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.5,.64,.8,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.65
s['Atlas revision']=6
s['Reference']='Northern plateau falls, northwest of reservoir; upper river 1090 m, reservoir 690 m. Local design proposal; units km, true relief.'
def material(name,col,rough=.65):
 m=bpy.data.materials.new(name);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
rock=material('Stratified plateau bedrock',(.30,.28,.20));water=material('Freshwater',(.025,.18,.20),.18);foam=material('Aerated falling water',(.73,.84,.85),.3);green=material('Riparian shrubs',(.13,.20,.06))
n=rock.node_tree.nodes;l=rock.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');nt=n.new('ShaderNodeTexNoise');nt.inputs['Scale'].default_value=4;nt.inputs['Detail'].default_value=6;l.new(tc.outputs['Object'],nt.inputs['Vector']);ra=n.new('ShaderNodeValToRGB');ra.color_ramp.elements[0].color=(.12,.13,.06,1);ra.color_ramp.elements[1].color=(.48,.40,.24,1);l.new(nt.outputs['Fac'],ra.inputs[0]);l.new(ra.outputs[0],p.inputs['Base Color']);bu=n.new('ShaderNodeBump');bu.inputs['Distance'].default_value=.025;bu.inputs['Strength'].default_value=.35;l.new(nt.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs[0],p.inputs['Normal'])
# Geographic north is upstream (+Y). Steppe remains above the incised river gorge.
def bed(y):
 if y>.08:return 1.071
 if y>-.06:return 1.071-(.08-y)/.14*.25
 if y>-.65:return .821
 if y>-.84:return .821-(-.65-y)/.19*.08
 if y>-1.35:return .741
 if y>-1.55:return .741-(-1.35-y)/.2*.07
 return .671

def terrain(x,y):
 cx=.055*math.sin(y*2);width=.22 if y>.12 else (.48+max(-y,0)*.13)
 q=abs(x-cx)/width;t=min(1,max(0,(q-.70)/.8));t=(t*t*(3-2*t))**.65
 crest=max(1.20,1.28+.065*math.sin(x*2+y)+.045*noise.fractal(Vector((x*1.2,y*.7,1)),1,2,4))
 z=bed(y)*(1-t)+crest*t
 z+=t*.018*noise.noise(Vector((x*19,y*18,4)))
 return z

def mesh(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(ma)
 for p in me.polygons:p.use_smooth=True
 return o
N=420;vs=[(-6+12*i/N,-8+18*j/N,terrain(-6+12*i/N,-8+18*j/N)) for j in range(N+1) for i in range(N+1)];fs=[]
for j in range(N):
 for i in range(N):
  a=j*(N+1)+i;fs.append((a,a+1,a+N+2,a+N+1))
mesh('Dissected steppe plateau and layered gorge',vs,fs,rock)
# One continuous water surface follows the exact bed profile. Its edges meet the banks.
for ma in [water,foam]:
 n=ma.node_tree.nodes;l=ma.node_tree.links;p=n.get('Principled BSDF');tc=n.new('ShaderNodeTexCoord');sc=n.new('ShaderNodeVectorMath');sc.operation='MULTIPLY';sc.inputs[1].default_value=(240,100,20);l.new(tc.outputs['Object'],sc.inputs[0]);nt=n.new('ShaderNodeTexNoise');nt.inputs['Scale'].default_value=1;nt.inputs['Detail'].default_value=4;l.new(sc.outputs[0],nt.inputs['Vector']);bu=n.new('ShaderNodeBump');bu.inputs['Strength'].default_value=.3;bu.inputs['Distance'].default_value=.001;l.new(nt.outputs['Fac'],bu.inputs['Height']);l.new(bu.outputs[0],p.inputs['Normal'])
 if ma==foam:
  ra=n.new('ShaderNodeValToRGB');ra.color_ramp.elements[0].position=.25;ra.color_ramp.elements[0].color=(.12,.34,.38,1);ra.color_ramp.elements[1].position=.7;ra.color_ramp.elements[1].color=(.85,.94,.95,1);l.new(nt.outputs['Fac'],ra.inputs[0]);l.new(ra.outputs[0],p.inputs['Base Color'])
vv=[];rows=1800;cols=16;levels=[]
for j in range(rows+1):
 y=6-12*j/rows;z=bed(y)+.019;cx=.055*math.sin(y*2);ends=[]
 for side in [-1,1]:
  lo=0;hi=2.6
  for k in range(18):
   mid=(lo+hi)/2
   if terrain(cx+side*mid,y)>z:hi=mid
   else:lo=mid
  ends.append(cx+side*(lo+hi)/2)
 for i in range(cols+1):
  x=ends[0]+(ends[1]-ends[0])*i/cols;vv.append((x,y,z+.0003*math.sin(i*1.3+j*.23)))
 levels.append(z)
ff=[]
for j in range(rows):
 for i in range(cols):
  k=j*(cols+1)+i;ff.append((k,k+1,k+cols+2,k+cols+1))
o=mesh('Continuous river, 250 m main fall and lower cascades',vv,ff,water);o.data.materials.append(foam)
for j in range(rows):
 if abs(levels[j+1]-levels[j])>.001:
  for i in range(cols):o.data.polygons[j*cols+i].material_index=1
for i in range(120):
 x=random.choice([-1,1])*random.uniform(.35,.7);y=random.uniform(-2.5,2.5);z=terrain(x,y)
 if z>1.12:continue
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=random.uniform(.008,.018),location=(x,y,z+.012));bpy.context.object.name='Sparse riparian shrub';bpy.context.object.data.materials.append(green)
# Local mist occupies only the plunge pool.
m=bpy.data.materials.new('Plunge mist');m.use_nodes=True;n=m.node_tree.nodes;n.clear();o=n.new('ShaderNodeOutputMaterial');v=n.new('ShaderNodeVolumePrincipled');v.inputs['Density'].default_value=2.5;v.inputs['Color'].default_value=(.8,.87,.9,1);m.node_tree.links.new(v.outputs['Volume'],o.inputs['Volume'])
bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=1,location=(0,-.16,.90));mist=bpy.context.object;mist.name='Local waterfall spray';mist.scale=(.28,.22,.10);mist.data.materials.append(m)
bpy.ops.object.light_add(type='SUN');sun=bpy.context.object;sun.rotation_euler=(.4,-.45,-.5);sun.data.energy=2.6;sun.data.angle=.12
bpy.ops.object.camera_add(location=(3,-4.5,3.8));cam=bpy.context.object;cam.rotation_euler=(Vector((0,-.2,.95))-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.type='ORTHO';cam.data.ortho_scale=3.5;s.camera=cam
from bpy_extras.object_utils import world_to_camera_view
bpy.context.view_layer.update()
features=[]
for i,name,co in [('A','Upper plateau river / 1090 m',(0,1.1,1.09)),('B','Main waterfall / 250 m',(0,-.03,.98)),('C','Plunge pool / 840 m',(0,-.35,.84)),('D','Lower cascades',(0,-1.0,.76)),('E','Reservoir valley / 690 m',(0,-1.9,.69)),('F','Steppe plateau',(1,1,1.2))]:
 p=world_to_camera_view(s,cam,Vector(co));features.append(dict(id=i,name=name,x=p.x,y=1-p.y,visible=0<p.x<1 and 0<p.y<1,description='Local study; true vertical scale'))
json.dump([dict(name='16_plateau_falls',features=features)],open(B/'source/waterfall_views.json','w'),indent=2)
s.render.filepath=str(B/'renders/16_plateau_falls.png');bpy.ops.wm.save_as_mainfile(filepath=str(B/'model/CATWORLD_Waterfall_Study.blend'));bpy.ops.render.render(write_still=True)
print('WATERFALL COMPLETE')
