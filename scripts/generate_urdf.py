"""生成 Touch R1 的七轴（含双 finger）运动学预览 URDF；用 FreeCAD Python 执行。"""
from pathlib import Path
import hashlib
import json
import struct
import xml.etree.ElementTree as ET
import FreeCAD as App
import Part
import MeshPart

ROOT = Path(__file__).resolve().parents[1]
HARDWARE = ROOT / 'hardware'
OUTPUT = HARDWARE / 'robot-description'
PACKAGE = OUTPUT / 'touch_r1_description'
COLORS = {'structure': '0.82 0.86 0.88 1', 'servo': '0.18 0.23 0.28 1',
          'horn': '0.62 0.68 0.73 1', 'hardware': '0.38 0.43 0.48 1', 'finger': '0.93 0.57 0.20 1'}
ASSEMBLY = OUTPUT / 'source/r1-hd-urdf-only.FCStd'
SOURCE_INFO = OUTPUT / 'source/assembly-source.json'
LINK_NAMES = ['base_link'] + [f'link_{i}' for i in range(1, 7)] + ['right_finger', 'left_finger']
# FCStd 对象标识，按基座到手柄排序；不再从含限位块的旧 BOM 回填零件。
SERVOS = [
    ('RP8_U45H_M_C028_STEP_ASM', 'rp8-u45h-m-c028'),
    ('_25_50KG_0001_ASM_ASM', 'rp8-u45h-m'),
    ('_25_50KG_0001_ASM_ASM001', 'rp8-u45h-m'),
    ('_25_50KG_0001_ASM_ASM002', 'rp8-u45h-m'),
    ('RP8_U45H_M_C028_STEP_ASM001', 'rp8-u45h-m-c028'),
    ('RP8_U45H_M_C028_STEP_ASM002', 'rp8-u45h-m-c028'),
    ('RP8_U45H_M_C028_STEP_ASM003', 'rp8-u45h-m-c028'),
]
STRUCTURES = ['Part__Feature', 'Part__Feature016', 'Part__Feature033',
              'Part__Feature048', 'Part__Feature063', 'Part__Feature078', 'Part__Feature098',
              'Part__Feature114']
ATTACHMENTS = {'Part__Feature015': (1, 'structure'),
               'Part__Feature017': (0, 'hardware'), 'Part__Feature018': (0, 'hardware'),
               'Part__Feature093': (5, 'hardware'),
               'Part__Feature095': (0, 'hardware'), 'Part__Feature096': (0, 'hardware'),
               'Part__Feature113': (8, 'finger')}


def leaves(obj):
    """只遍历装配的实体叶节点；App::Part 的缓存 Shape 不能重复计入。"""
    if obj.TypeId == 'App::Part':
        return [leaf for child in obj.Group for leaf in leaves(child)]
    if obj.TypeId == 'Part::Feature' and obj.Shape.Solids:
        return [obj]
    raise ValueError(f'未审核的装配对象：{obj.Name} ({obj.TypeId})')


def global_shape(obj):
    shape = obj.Shape.copy()
    shape.Placement = obj.getGlobalPlacement()
    assert shape.isValid(), obj.Name
    return shape


def values(v):
    return [round(x, 10) for x in v]


def vecstr(v):
    return ' '.join(f'{x:.10g}' for x in v)


def shaft(shape):
    """由半径 10 mm 的舵盘外圆识别轴线，保留舵盘与机壳的独立实体。"""
    horns, body, axes = [], [], []
    for solid in shape.Solids:
        circles = [f.Surface for f in solid.Faces
                   if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius - 10) < 1e-4]
        if circles:
            horns.append(solid)
            axes.extend(circles)
        else:
            body.append(solid)
    assert horns and body
    axis = axes[0].Axis
    if max(axis, key=abs) < 0:
        axis = -axis
    center = axes[0].Center
    for a in axes:
        assert axis.cross(a.Axis).Length < 1e-6
        assert (a.Center - center).cross(axis).Length < .001
    midpoint = sum((s.CenterOfMass for s in horns), App.Vector()) / len(horns)
    center = center + axis * (midpoint - center).dot(axis)
    return center, axis, horns, body


def write_stl(path, shapes, origin, rotation, floor):
    triangles = []
    def convert(p):
        return (rotation.multVec(p) + App.Vector(0, 0, floor) - origin) / 1000
    low = [float('inf')] * 3
    high = [-float('inf')] * 3
    for shape in shapes:
        mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=.12, AngularDeflection=.35, Relative=False)
        points, faces = mesh.Topology
        points = [convert(p) for p in points]
        for p in points:
            for i in range(3):
                low[i] = min(low[i], p[i]); high[i] = max(high[i], p[i])
        for a, b, c in faces:
            p, q, r = points[a], points[b], points[c]
            normal = (q-p).cross(r-p)
            if normal.Length < 1e-15:
                continue
            normal.normalize()
            triangles.append((*normal, *p, *q, *r))
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('wb') as f:
        f.write(b'Touch R1 CAD mesh; coordinates in meters'.ljust(80, b' '))
        f.write(struct.pack('<I', len(triangles)))
        for triangle in triangles:
            f.write(struct.pack('<12fH', *triangle, 0))
    return {'triangles': len(triangles), 'bounds_m': [low, high],
            'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}


def main():
    source_info = json.loads(SOURCE_INFO.read_text())
    assert source_info['revision'] == 'V3.2'
    assert hashlib.sha256(ASSEMBLY.read_bytes()).hexdigest() == source_info['snapshot_sha256'], '源装配已变化，请复核零件映射'
    doc = App.openDocument(str(ASSEMBLY))
    root = doc.getObject('_45_X2_535551FA8235673A_X0__ASM')
    assert root is not None
    leaf_objects = leaves(root)
    leaf_names = [obj.Name for obj in leaf_objects]
    assert len(leaf_names) == len(set(leaf_names)) == 113
    assert not any(obj.Label in {'A000', 'B000'} for obj in leaf_objects)
    shapes = {obj.Name: global_shape(obj) for obj in leaf_objects}
    assert sum(len(shape.Solids) for shape in shapes.values()) == 113
    models = {model: Part.read(str(HARDWARE/f'step/components/{model}.step'))
              for model in sorted({model for _, model in SERVOS})}
    source_paths = [ASSEMBLY, SOURCE_INFO] + [HARDWARE/f'step/components/{model}.step' for model in models]
    sources = [{'file': str(path.relative_to(HARDWARE)),
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest()} for path in source_paths]
    replacements, used = [], set()
    rotation = App.Rotation(App.Vector(1,0,0), 90)
    floor = -shapes[STRUCTURES[0]].BoundBox.YMin
    convert = lambda p: rotation.multVec(p) + App.Vector(0,0,floor)
    groups = [{category: [] for category in COLORS} for _ in range(len(LINK_NAMES))]
    origins = [App.Vector()]
    joints, mapping = [], []
    for index, (object_name, model) in enumerate(SERVOS, 1):
        obj = doc.getObject(object_name)
        servo_leaves = leaves(obj)
        original = Part.makeCompound([shapes[leaf.Name] for leaf in servo_leaves])
        shape = models[model].copy()
        shape.Placement = obj.getGlobalPlacement()
        assert shape.isValid()
        p, axis, horns, body = shaft(shape)
        op, od, _, _ = shaft(original)
        mismatch = (p-op).cross(axis).Length
        bb, ob = shape.BoundBox, original.BoundBox
        bbox_delta = max(abs(getattr(bb,k)-getattr(ob,k)) for k in
                         ['XMin','YMin','ZMin','XMax','YMax','ZMax'])
        assert mismatch < .01 and axis.cross(od).Length < 1e-6 and bbox_delta < .02
        replacements.append({'source_object': object_name, 'model': model,
                             'axis_offset_mm': mismatch, 'bbox_max_difference_mm': bbox_delta,
                             'original_solids': len(original.Solids), 'replacement_solids': len(shape.Solids),
                             'relative_volume_difference': abs(shape.Volume-original.Volume)/original.Volume})
        # 用下游结构件的同轴圆柱面再次核对轴线。
        structural = shapes[STRUCTURES[index]]
        matches = []
        for face in structural.Faces:
            cylinder = face.Surface
            if not isinstance(cylinder, Part.Cylinder) or cylinder.Radius < 4:
                continue
            if cylinder.Axis.cross(axis).Length < 1e-5:
                matches.append((cylinder.Center-p).cross(axis).Length)
        error = min(matches)
        assert error < .02, (index, error)
        origin = convert(p)
        converted_axis = rotation.multVec(axis)
        joints.append({'name': f'joint_{index}', 'parent': LINK_NAMES[index-1],
                       'child': LINK_NAMES[index], 'origin_xyz': values((origin-origins[-1])/1000),
                       'axis': values(converted_axis), 'cad_axis_point_mm': values(p),
                       'cad_axis_direction': values(axis), 'coaxial_error_mm': error,
                       'source_object': object_name, 'servo_model': model,
                       'preview_range_deg': [0,25] if index==7 else [-90,90], 'status_zh': 'CAD 推导轴线及连接关系，实物方向与限位待确认'})
        origins.append(origin)
        groups[index-1]['servo'].extend(body)
        groups[index]['horn'].extend(horns)
        names = [leaf.Name for leaf in servo_leaves]
        assert not used.intersection(names)
        used.update(names)
        mapping.append({'source_object': object_name, 'source_leaf_objects': names,
                        'body_link': index-1, 'horn_link': index,
                        'body_solids': len(body), 'horn_solids': len(horns)})
    # 左 finger 的轴由自身 1.65 mm 孔及手柄 1.6 mm 孔交叉定位。
    left = shapes['Part__Feature113']
    holes = [f.Surface for f in left.Faces if isinstance(f.Surface, Part.Cylinder)
             and abs(f.Surface.Radius-1.65) < 1e-4]
    assert holes
    axis = App.Vector(*joints[-1]['cad_axis_direction'])
    p = holes[0].Center
    driven = App.Vector(*joints[-1]['cad_axis_point_mm'])
    p += axis * (driven-p).dot(axis)
    assert holes[0].Axis.cross(axis).Length < 1e-6
    handle_holes = [f.Surface for f in shapes['Part__Feature098'].Faces
                    if isinstance(f.Surface, Part.Cylinder) and abs(f.Surface.Radius-1.6)<1e-4]
    error = min((h.Center-p).cross(axis).Length for h in handle_holes if h.Axis.cross(axis).Length<1e-6)
    assert error < .02 and abs((p-driven).Length-22) < .001
    # 两侧同轴齿根/齿顶圆半径相同，支持 1:1 反向啮合的运动学推定。
    for shape, center in [(left,p),(shapes['Part__Feature114'],driven)]:
        for radius in (9.75,12.0):
            assert any(isinstance(f.Surface,Part.Cylinder) and abs(f.Surface.Radius-radius)<1e-4
                       and f.Surface.Axis.cross(axis).Length<1e-6
                       and (f.Surface.Center-center).cross(axis).Length<.001 for f in shape.Faces)
    origin = convert(p)
    joints.append({'name':'left_finger_joint', 'parent':'link_6', 'child':'left_finger',
                   'origin_xyz':values((origin-origins[6])/1000), 'axis':values(rotation.multVec(axis)),
                   'cad_axis_point_mm':values(p), 'cad_axis_direction':values(axis),
                   'coaxial_error_mm':error, 'source_object':'Part__Feature113',
                   'mimic':{'joint':'joint_7','multiplier':-1.0,'offset':0.0},
                   'status_zh':'按 CAD 齿形推定 1:1 反向联动，传动关系与实际行程待实物复核'})
    origins.append(origin)
    attachments = {name: (index, 'finger' if index==7 else 'structure') for index, name in enumerate(STRUCTURES)}
    attachments.update(ATTACHMENTS)
    for name, (link, category) in attachments.items():
        assert name not in used
        used.add(name)
        shape = shapes[name]
        groups[link][category].extend(shape.Solids)
        mapping.append({'source_object': name, 'source_label': doc.getObject(name).Label, 'link': link,
                        'solids': len(shape.Solids),
                        'status_zh': '按结构顺序归属' if name in STRUCTURES else '垫片／紧固件固定归属待装配工程复核'})
    assert used == set(leaf_names), ('存在未归属或重复零件', used.symmetric_difference(leaf_names))
    count = sum(len(s) for g in groups for s in g.values())
    assert count == 116  # 113 个保留源实体，三个双出轴舵机替换后各增加一个实体。
    # 仅清理本生成器管理的旧网格，防止下载包保留已不被 URDF 引用的几何。
    for old_mesh in (PACKAGE/'meshes').glob('*.stl'):
        old_mesh.unlink()
    robot = ET.Element('robot', name='touch_r1_leader_arm_preview')
    robot.append(ET.Comment('运动学预览草案：continuous 仅为无已知限位时的可视化表示；不是实机无限旋转声明。未提供惯量、碰撞模型或控制接口。'))
    meshes = []
    for index, group in enumerate(groups):
        name = LINK_NAMES[index]
        link = ET.SubElement(robot,'link',name=name)
        for category, solids in group.items():
            if not solids:
                continue
            filename = f'{name}-{category}.stl'
            metrics = write_stl(PACKAGE/'meshes'/filename, solids, origins[index], rotation, floor)
            visual = ET.SubElement(link, 'visual', name=f'{name}_{category}')
            ET.SubElement(visual,'origin',xyz='0 0 0',rpy='0 0 0')
            geometry = ET.SubElement(visual,'geometry')
            ET.SubElement(geometry,'mesh',filename=f'../meshes/{filename}')
            material = ET.SubElement(visual,'material',name=category)
            ET.SubElement(material,'color',rgba=COLORS[category])
            meshes.append({'link': name, 'file': f'meshes/{filename}', 'category': category, **metrics})
    for info in joints:
        joint = ET.SubElement(robot,'joint',name=info['name'],type='continuous')
        ET.SubElement(joint,'parent',link=info['parent']);ET.SubElement(joint,'child',link=info['child'])
        ET.SubElement(joint,'origin',xyz=vecstr(info['origin_xyz']),rpy='0 0 0')
        ET.SubElement(joint,'axis',xyz=vecstr(info['axis']))
        if 'mimic' in info:
            ET.SubElement(joint,'mimic',**{k:str(v) for k,v in info['mimic'].items()})
    PACKAGE.joinpath('urdf').mkdir(parents=True,exist_ok=True)
    ET.indent(robot,space='  ')
    ET.ElementTree(robot).write(PACKAGE/'urdf/touch-r1.urdf',encoding='utf-8',xml_declaration=True)
    manifest = {'model': 'Touch R1 Leader Arm V3.2', 'status_zh': '七轴运动学预览草案（双 finger 联动待实物确认）',
                'source_assembly': str(ASSEMBLY.relative_to(HARDWARE)),
                'source_assembly_sha256': sources[0]['sha256'], 'source_format': 'FCStd', 'original_step': source_info,
                'source_length_unit': 'mm', 'urdf_length_unit': 'm',
                'cad_to_urdf_zh': f'绕 X 轴 +90°（Y 向上改为 Z 向上），再沿 Z 平移 {floor:.6f} mm，使基座底面为 Z=0。',
                'floor_offset_mm': floor, 'servo_replacements': replacements, 'sources': sources,
                'zero_pose_zh': '源 FCStd 装配姿态，不是实机编码器零位。',
                'joint_limits_zh': '未确认；URDF 使用 continuous 供可视化；J1–J6 ±90°、J7 0–25° 均仅为演示范围。',
                'removed_parts_zh': 'V3.2 STEP 导入时排除 A000、B000 两个限位块，不从旧 BOM 回填。',
                'auxiliary_parts_zh': '保留当前源文件中的垫片和五个紧固件，固定归属待实物复核。',
                'inertia_collision_control_zh': '未提供质量、惯量、碰撞模型、驱动参数或控制接口；仅用于可视化。',
                'original_assembly_solids': 113, 'replacement_assembly_solids': count,
                'source_leaf_objects': leaf_names,
                'links': len(LINK_NAMES), 'independent_joints': 7, 'joints': joints, 'meshes': meshes, 'source_mapping': mapping}
    (OUTPUT/'kinematics.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated 9 links, 7 independent joints + 1 mimic joint, {len(meshes)} meshes, {count} solids.', flush=True)
    print(json.dumps(replacements,ensure_ascii=False,indent=2),flush=True)
    App.closeDocument(doc.Name)


if __name__ == '__main__':
    main()
