"""用 Blender 从实际 URDF / STL 渲染预览；支持 --j7 25 --closeup。"""
from pathlib import Path
import argparse
import math
import struct
import sys
import xml.etree.ElementTree as ET
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1] / 'hardware/robot-description'
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--j7', type=float, default=0)
parser.add_argument('--closeup', action='store_true')
parser.add_argument('--output', default='preview.png')
args = parser.parse_args(sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else [])
urdf = ROOT/'touch_r1_description/urdf/touch-r1.urdf'
robot = ET.parse(urdf).getroot()
transforms = {'base_link': Matrix.Identity(4)}
angles = {'joint_7': math.radians(args.j7)}
for joint in robot.findall('joint'):
    parent, child = (joint.find(tag).attrib['link'] for tag in ['parent', 'child'])
    name = joint.attrib['name']; mimic = joint.find('mimic')
    angle = angles.get(name,0)
    if mimic is not None:
        angle = angles[mimic.attrib['joint']] * float(mimic.attrib.get('multiplier',1)) + float(mimic.attrib.get('offset',0))
    angles[name] = angle
    xyz = tuple(map(float,joint.find('origin').attrib['xyz'].split()))
    axis = Vector(tuple(map(float,joint.find('axis').attrib['xyz'].split())))
    transforms[child] = transforms[parent] @ Matrix.Translation(xyz) @ Matrix.Rotation(angle,4,axis)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
scene = bpy.context.scene; scene.render.engine = 'CYCLES'; scene.cycles.samples = 32
scene.cycles.use_denoising = True; scene.cycles.seed = 0
scene.render.resolution_x = 1100; scene.render.resolution_y = 1000
scene.render.resolution_percentage = 100; scene.render.image_settings.file_format = 'PNG'
scene.render.image_settings.color_mode = 'RGB'; scene.view_settings.view_transform = 'Standard'
scene.world.use_nodes = True
scene.world.node_tree.nodes['Background'].inputs[0].default_value = (.85,.90,.94,1)
scene.world.node_tree.nodes['Background'].inputs[1].default_value = .7
all_points=[]; focus_points=[]; objects=[]
for link in robot.findall('link'):
    name = link.attrib['name']
    for visual in link.findall('visual'):
        path = (urdf.parent/visual.find('geometry/mesh').attrib['filename']).resolve()
        data = path.read_bytes(); vertices=[]; triangles=[]
        for facet in struct.iter_unpack('<12fH',data[84:]):
            start=len(vertices)
            vertices.extend([transforms[name] @ Vector(facet[i:i+3]) for i in [3,6,9]])
            triangles.append((start,start+1,start+2))
        mesh=bpy.data.meshes.new(path.stem); mesh.from_pydata(vertices,[],triangles); mesh.update()
        obj=bpy.data.objects.new(path.stem,mesh);scene.collection.objects.link(obj);objects.append(obj)
        material=bpy.data.materials.new(path.stem); material.use_nodes=True
        rgba=tuple(map(float,visual.find('material/color').attrib['rgba'].split()))
        bsdf=material.node_tree.nodes.get('Principled BSDF');bsdf.inputs['Base Color'].default_value=rgba
        bsdf.inputs['Roughness'].default_value=.55;bsdf.inputs['Metallic'].default_value=.05
        obj.data.materials.append(material)
        all_points.extend(vertices)
        if name in {'link_6','right_finger','left_finger'}:focus_points.extend(vertices)
points=focus_points if args.closeup else all_points
lo=Vector([min(v[i] for v in points) for i in range(3)])
hi=Vector([max(v[i] for v in points) for i in range(3)])
center=(lo+hi)/2; scale=2.8/max(hi-lo)
for obj in objects:
    for v in obj.data.vertices:v.co=(v.co-center)*scale
for loc,power in [((3,4,6),220),((-4,2,3),120),((2,-4,3),140)]:
    light=bpy.data.lights.new('Softbox','AREA');light.energy=power;light.shape='DISK';light.size=4
    obj=bpy.data.objects.new('Softbox',light);scene.collection.objects.link(obj);obj.location=loc
    obj.rotation_euler=(-obj.location).to_track_quat('-Z','Y').to_euler()
cam=bpy.data.objects.new('Camera',bpy.data.cameras.new('Camera'));scene.collection.objects.link(cam)
cam.location=(4,7,4);cam.rotation_euler=(-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO';scene.camera=cam
rot=cam.rotation_euler.to_quaternion()
projected=[rot.inverted() @ ((v-center)*scale) for v in points]
bounds=[(min(v[i] for v in projected),max(v[i] for v in projected)) for i in range(2)]
shift=rot @ Vector([(a+b)/2 for a,b in bounds]+[0])
cam.location+=shift
cam.data.ortho_scale=max(bounds[0][1]-bounds[0][0],(bounds[1][1]-bounds[1][0])*1.1)*1.18
scene.render.filepath=str(ROOT/'images'/args.output)
bpy.ops.render.render(write_still=True)
print('已从 URDF 渲染',scene.render.filepath,flush=True)
