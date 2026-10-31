import bpy, math, random, json
from mathutils import Vector, noise
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];random.seed(81)
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.samples=32;s.cycles.use_denoising=True;s.render.resolution_x=2400;s.render.resolution_y=1600;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.view_settings.view_transform='AgX';s.render.film_transparent=False
s.world.use_nodes=True;s.world.node_tree.nodes['Background'].inputs[0].default_value=(.45,.58,.70,1);s.world.node_tree.nodes['Background'].inputs[1].default_value=.5
s.unit_settings.system='METRIC';s.unit_settings.scale_length=1000
s['purpose']='Conceptual terrain inset of landmark 05, oriented north upstream; 1 Blender unit = 1 km. Fictional engineering, not a construction design.'
def mat(name,col,rough=.7):
 m=bpy.data.materials.new(name);m.diffuse_color=(*col,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*col,1);p.inputs['Roughness'].default_value=rough;return m
stone=mat('Warm weathered mass concrete',(.42,.40,.33));dark=mat('Oxidized bronze gates',(.12,.18,.16),.35);water=mat('Fresh reservoir water',(.025,.17,.19),.24);roof=mat('Patinated copper roofs',(.15,.25,.21),.5);white=mat('Aerated spillway water',(.62,.79,.79),.4);earth=mat('Layered bedrock',(.24,.23,.18));leaves=mat('Forest canopy',(.055,.12,.045));road=mat('Pale crushed stone road',(.36,.33,.25))
# Material texture distinguishes stone from green slopes.
terrainmat=mat('Bedrock and forest slope mosaic',(.18,.25,.10));nt=terrainmat.node_tree;n=nt.nodes;l=nt.links;p=n.get('Principled BSDF');tex=n.new('ShaderNodeTexNoise');tex.inputs['Scale'].default_value=3;tex.inputs['Detail'].default_value=7;tex.inputs['Roughness'].default_value=.72
coords=n.new('ShaderNodeTexCoord');l.new(coords.outputs['Object'],tex.inputs['Vector'])
ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.25;ramp.color_ramp.elements[0].color=(.035,.065,.018,1);ramp.color_ramp.elements[1].position=.76;ramp.color_ramp.elements[1].color=(.37,.32,.22,1);e=ramp.color_ramp.elements.new(.52);e.color=(.14,.20,.06,1);l.new(tex.outputs['Fac'],ramp.inputs[0]);l.new(ramp.outputs[0],p.inputs['Base Color']);bum=n.new('ShaderNodeBump');bum.inputs['Strength'].default_value=.4;bum.inputs['Distance'].default_value=.05;l.new(tex.outputs['Fac'],bum.inputs['Height']);l.new(bum.outputs[0],p.inputs['Normal'])
geom=n.new('ShaderNodeNewGeometry');sep=n.new('ShaderNodeSeparateXYZ');albedo=n.new('ShaderNodeMixRGB');albedo.blend_type='MIX';albedo.inputs[1].default_value=(.27,.25,.20,1);l.new(geom.outputs['Normal'],sep.inputs[0]);l.new(sep.outputs['Z'],albedo.inputs[0]);l.new(ramp.outputs[0],albedo.inputs[2]);l.new(albedo.outputs[0],p.inputs['Base Color'])
# Concrete fine grain.
n=stone.node_tree.nodes;l=stone.node_tree.links;t=n.new('ShaderNodeTexNoise');t.inputs['Scale'].default_value=85;t.inputs['Detail'].default_value=3;b=n.new('ShaderNodeBump');b.inputs['Strength'].default_value=.2;b.inputs['Distance'].default_value=.004;l.new(t.outputs['Fac'],b.inputs['Height']);l.new(b.outputs[0],n.get('Principled BSDF').inputs['Normal'])
def terrain(x,y):
 width=2.4+max(y,0)*.22 if y>=0 else .55+1.85*math.exp(y/1.3)
 center=.16*math.sin(y*.65)*(1-math.exp(-abs(y)))
 q=abs(x-center)/width
 h=.21+.62*min(q**3.6,2.8)
 amp=min(max(q-.45,0),1)*.28
 h+=amp*noise.fractal(Vector((x*.8,y*.8,2)),1,2,5)
 h+=.05*min(q,1)*noise.noise(Vector((x*6,y*6,1)))
 return h
N=340;verts=[]
for iy in range(N+1):
 y=-12+28*iy/N
 for ix in range(N+1):
  x=-12+24*ix/N;verts.append((x,y,terrain(x,y)))
faces=[]
for iy in range(N):
 for ix in range(N):
  a=iy*(N+1)+ix;faces.append((a,a+1,a+N+2,a+N+1))
me=bpy.data.meshes.new('Incised bedrock valley');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new('Outlet gorge and plateau',me);s.collection.objects.link(ob);ob.data.materials.append(terrainmat)
for p in me.polygons:p.use_smooth=True
def cube(name,loc,scale,ma):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.data.materials.append(ma);return o
def meshobj(name,vs,fs,ma):
 me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();o=bpy.data.objects.new(name,me);s.collection.objects.link(o);o.data.materials.append(ma);return o
def path(name,pts,r,ma):
 if ma in [water,white,road]:
  vv=[]
  for q in pts:vv.extend([(q[0]-r,q[1],q[2]+.002),(q[0]+r,q[1],q[2]+.002)])
  return meshobj(name,vv,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(len(pts)-1)],ma)
 c=bpy.data.curves.new(name,'CURVE');c.dimensions='3D';c.bevel_depth=r;c.bevel_resolution=2;sp=c.splines.new('POLY');sp.points.add(len(pts)-1)
 for p,co in zip(sp.points,pts):p.co=(*co,1)
 o=bpy.data.objects.new(name,c);s.collection.objects.link(o);o.data.materials.append(ma);return o
# Reservoir is a level plane terminating against the upstream face.
cube('Reservoir | level 690 m',(0,8.02,.688),(24,16,.004),water)
# The downstream river follows the narrow valley floor.
vs=[]
for i in range(250):
 y=-.25-i*12/249;cx=.16*math.sin(y*.65)*(1-math.exp(-abs(y)));w=.20+.12*math.exp(y/2)
 for x in [cx-w,cx+w]:vs.append((x,y,.266-max(-y-1,0)*.0025))
meshobj('Tailwater and downstream river',vs,[(2*i,2*i+1,2*i+3,2*i+2) for i in range(249)],water)
# Broad gravity arch: each section has a thick base and narrow service crest.
vs=[];seg=160
for i in range(seg+1):
 x=-2.4+4.8*i/seg;y=.20*(1-(x/2.4)**2)
 vs.extend([(x,y+.025,.715),(x,y-.065,.715),(x,y-.31,.245),(x,y+.025,.245)])
fs=[]
for i in range(seg):
 for j in range(4):fs.append((4*i+j,4*(i+1)+j,4*(i+1)+(j+1)%4,4*i+(j+1)%4))
fs += [(0,3,2,1),(4*seg,4*seg+1,4*seg+2,4*seg+3)]
meshobj('Great Panterran Dam | 4.8 km crest | 470 m structural height',vs,fs,stone)
for i in range(41):
 x=-2.30+i*4.60/40;y=.20*(1-(x/2.4)**2)
 # Face expansion joints and buttress ribs.
 path('Gravity face rib',[(x,y-.067,.705),(x,y-.31,.25)],.008,stone)
 if i%2==0:
  cube('Intake tower',(x,y+.07,.725),(.045,.08,.095),stone)
  cube('Bronze intake roof',(x,y+.07,.779),(.058,.095,.012),roof)
# Central gated spillway with flowing whitewater chutes.
for i in range(8):
 x=-.50+i/7;y=.20*(1-(x/2.4)**2)
 cube('Bronze spillway gate',(x,y-.075,.681),(.082,.018,.055),dark)
 pts=[(x,y-.115,.66),(x,y-.195,.51),(x,y-.30,.31),(x,y-.45,.27),(x,y-.8,.267)]
 path('Spillway release',pts,.035,white)
 cube('Spillway pier',(x-.05,y-.04,.74),(.019,.10,.085),stone)
# Turbine galleries and repeating roof bays.
for side in [-1,1]:
 cx=side*1.27;cube('Powerhouse turbine hall',(cx,-.30,.30),(1.12,.18,.11),stone)
 for j in range(12):
  x=cx-.5+j*.09;cube('Copper turbine roof',(x,-.30,.363),(.075,.19,.018),roof)
  cube('Generator window',(x,-.396,.325),(.038,.003,.038),dark)
 pass
for side in [-1,1]:
 path('Powerhouse tailrace',[(side*1.05,-.40,.268),(side*.85,-.65,.268),(side*.5,-.95,.267),(side*.2,-1.4,.266)],.10,water)
# Crest parapets, access roads and two abutment checkpoints.
for off in [-.055,.017]:path('Crest parapet',[(x,.20*(1-(x/2.4)**2)+off,.73) for x in [-2.4+4.8*j/180 for j in range(181)]],.008,stone)
for side in [-1,1]:
 pts=[]
 for j in range(100):
  y=-4+j*4/99;x=side*(2.6+.2*math.sin(y));pts.append((x,y,terrain(x,y)+.015))
 path('Abutment access road',pts,.025,road)
 x=side*2.55;y=-.14;z=terrain(x,y)
 cube('Abutment checkpoint',(x,y,z+.07),(.14,.18,.14),stone);cube('Checkpoint roof',(x,y,z+.148),(.17,.21,.025),roof)
# Fishing village on a stable terrace beside the upstream cove (inset proposal).
for i in range(55):
 x=random.uniform(3.1,3.7);y=random.uniform(.7,2.5);z=terrain(x,y)
 o=cube('Village house',(x,y,z+.014),(.035,.025,.028),stone);o.rotation_euler.z=random.uniform(-.3,.3)
 cube('Copper roof',(x,y,z+.03),(.039,.029,.008),roof)
# Sparse tree stands provide a scale cue; canopy detail is mostly material at this altitude.
bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);proto=bpy.context.object;proto.name='Canopy prototype';proto.data.materials.append(leaves)
for i in range(1800):
 x=random.uniform(-7,7);y=random.uniform(-5,9);z=terrain(x,y)
 if z<.74 or z>1.6 or abs(y)<.35:continue
 o=bpy.data.objects.new('Forest canopy',proto.data);s.collection.objects.link(o);o.location=(x,y,z+.025);r=random.uniform(.018,.04);o.scale=(r,r,r*1.3)
bpy.data.objects.remove(proto,do_unlink=True)
bpy.ops.object.light_add(type='SUN',location=(0,0,10));sun=bpy.context.object;sun.rotation_euler=(math.radians(24),math.radians(-20),math.radians(-35));sun.data.energy=3;sun.data.angle=.15
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.type='ORTHO'
metadata=[]
from bpy_extras.object_utils import world_to_camera_view
landmarks=[('A','Great Reservoir',(0,4,.69)),('B','Gravity dam / service crest',(0,.2,.72)),('C','Gated spillway',(0,-.25,.45)),('D','Turbine galleries',(1.3,-.3,.36)),('E','Tailwater / river',(0,-2,.26)),('F','Abutment checkpoint',(2.55,-.14,terrain(2.55,-.14)+.2)),('G','Fishing village',(3.4,1.5,terrain(3.4,1.5)+.1))]
for name,loc,target,scale in [('09_dam_valley',(4,-8,16),(0,1.8,.2),13),('10_dam_detail',(1,-6,6),(0,.3,.5),6.3)]:
 cam.location=loc;cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=scale
 s.render.filepath=str(BASE/'renders'/f'{name}.png');bpy.ops.render.render(write_still=True)
 pp=[]
 for i,label,co in landmarks:
  v=world_to_camera_view(s,cam,Vector(co));pp.append(dict(id=i,name=label,x=v.x,y=1-v.y,visible=bool(0<v.x<1 and 0<v.y<1)))
 metadata.append(dict(name=name,features=pp))
json.dump(metadata,open(BASE/'source/dam_views.json','w'),indent=2)
for a in bpy.context.screen.areas:
 if a.type=='VIEW_3D':a.spaces.active.region_3d.view_perspective='CAMERA';a.spaces.active.shading.type='MATERIAL'
bpy.ops.wm.save_as_mainfile(filepath=str(BASE/'model/CATWORLD_Dam_Study.blend'))
print('DAM_COMPLETE')
