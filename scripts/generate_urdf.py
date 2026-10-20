"""生成 Touch R1 的六轴运动学预览 URDF；用 FreeCAD Python 执行。"""
from pathlib import Path
import hashlib
import json
import math
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
          'horn': '0.62 0.68 0.73 1', 'hardware': '0.38 0.43 0.48 1'}
# (BOM 序号, 实例索引)：沿基座到手柄的六轴顺序。
SERVOS = [(1, 0), (2, 0), (2, 1), (2, 2), (1, 1), (1, 2)]
# 非舵机件所属 link；辅助夹持件暂固定到基座，不虚构额外活动轴。
ATTACHMENTS = {3: 0, 4: 1, 5: 2, 6: 3, 7: 4, 8: 5, 9: 6,
               10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 5, 16: 0}


def vector(values):
    return App.Vector(*values)


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
    bom = json.loads((HARDWARE / 'bom.json').read_text())
    assembly = HARDWARE / bom['source_file']
    assert hashlib.sha256(assembly.read_bytes()).hexdigest() == bom['source_sha256']
    items = {x['no']: x for x in bom['items']}
    models = {1: HARDWARE / 'step/components/rp8-u45h-m-c028.step',
              2: HARDWARE / 'step/components/rp8-u45h-m.step'}
    sources, replacements, shapes = [], [], {}
    for number, item in items.items():
        path = models.get(number, HARDWARE / item['step_file'])
        shape = Part.read(str(path))
        assert shape.isValid()
        sources.append({'file': str(path.relative_to(HARDWARE)),
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
        if number in models:
            original = Part.read(str(HARDWARE / item['step_file']))
            p, d, _, _ = shaft(shape); op, od, _, _ = shaft(original)
            mismatch = (p-op).cross(d).Length
            bb, ob = shape.BoundBox, original.BoundBox
            bbox_delta = max(abs(getattr(bb,k)-getattr(ob,k)) for k in
                             ['XMin','YMin','ZMin','XMax','YMax','ZMax'])
            assert mismatch < .01 and d.cross(od).Length < 1e-6 and bbox_delta < .02
            replacements.append({'bom_no': number, 'model': path.stem,
                                 'axis_offset_mm': mismatch, 'bbox_max_difference_mm': bbox_delta,
                                 'original_solids': len(original.Solids), 'replacement_solids': len(shape.Solids),
                                 'relative_volume_difference': abs(shape.Volume-original.Volume)/original.Volume})
        for index, occurrence in enumerate(item['occurrences']):
            placed = shape.copy()
            placed.Placement = App.Placement(App.Matrix(*occurrence['placement_matrix']))
            shapes[number, index] = placed
    rotation = App.Rotation(App.Vector(1,0,0), 90)
    floor = -shapes[3,0].BoundBox.YMin
    convert = lambda p: rotation.multVec(p) + App.Vector(0,0,floor)
    groups = [{category: [] for category in COLORS} for _ in range(7)]
    origins = [App.Vector()]
    joints, mapping = [], []
    for index, key in enumerate(SERVOS, 1):
        p, axis, horns, body = shaft(shapes[key])
        # 用下游结构件的同轴圆柱面再次核对轴线。
        structural = shapes[index+3, 0]
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
        joints.append({'name': f'joint_{index}', 'parent': 'base_link' if index==1 else f'link_{index-1}',
                       'child': f'link_{index}', 'origin_xyz': values((origin-origins[-1])/1000),
                       'axis': values(converted_axis), 'cad_axis_point_mm': values(p),
                       'cad_axis_direction': values(axis), 'coaxial_error_mm': error,
                       'servo_bom_no': key[0], 'servo_occurrence_index': key[1],
                       'preview_range_deg': [-90,90], 'status_zh': 'CAD 推导轴线及连接关系，实物方向与限位待确认'})
        origins.append(origin)
        groups[index-1]['servo'].extend(body)
        groups[index]['horn'].extend(horns)
        mapping.append({'bom_no': key[0], 'occurrence_index': key[1],
                        'body_link': index-1, 'horn_link': index,
                        'body_solids': len(body), 'horn_solids': len(horns)})
    for (number, occurrence), shape in shapes.items():
        if number in models:
            continue
        link = ATTACHMENTS[number]
        category = 'structure' if number in range(3,13) else 'hardware'
        groups[link][category].extend(shape.Solids)
        mapping.append({'bom_no': number, 'occurrence_index': occurrence, 'link': link,
                        'solids': len(shape.Solids),
                        'status_zh': '按结构顺序归属' if number in range(3,10) else '附件固定归属待装配工程复核'})
    count = sum(len(s) for g in groups for s in g.values())
    assert count == sum(len(s.Solids) for s in shapes.values())
    robot = ET.Element('robot', name='touch_r1_leader_arm_preview')
    robot.append(ET.Comment('运动学预览草案：continuous 仅为无已知限位时的可视化表示；不是实机无限旋转声明。未提供惯量、碰撞模型或控制接口。'))
    meshes = []
    for index, group in enumerate(groups):
        name = 'base_link' if index == 0 else f'link_{index}'
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
    PACKAGE.joinpath('urdf').mkdir(parents=True,exist_ok=True)
    ET.indent(robot,space='  ')
    ET.ElementTree(robot).write(PACKAGE/'urdf/touch-r1.urdf',encoding='utf-8',xml_declaration=True)
    manifest = {'model': 'Touch R1 Leader Arm V3.1', 'status_zh': '六轴运动学预览草案',
                'source_assembly_sha256': bom['source_sha256'], 'source_length_unit': 'mm', 'urdf_length_unit': 'm',
                'cad_to_urdf_zh': f'绕 X 轴 +90°（Y 向上改为 Z 向上），再沿 Z 平移 {floor:.6f} mm，使基座底面为 Z=0。',
                'floor_offset_mm': floor, 'servo_replacements': replacements, 'sources': sources,
                'zero_pose_zh': '源 STEP 装配姿态，不是实机编码器零位。',
                'joint_limits_zh': '未确认；URDF 使用 continuous 供可视化，界面 ±90° 仅为演示范围。',
                'auxiliary_parts_zh': 'A000、B000 及其夹持螺钉暂固定到基座，不增加第七轴或夹爪运动。',
                'inertia_collision_control_zh': '未提供质量、惯量、碰撞模型、驱动参数或控制接口；仅用于可视化。',
                'original_assembly_solids': bom['expanded_leaf_occurrences'], 'replacement_assembly_solids': count,
                'links': 7, 'joints': joints, 'meshes': meshes, 'source_mapping': mapping}
    (OUTPUT/'kinematics.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
    print(f'Generated 7 links, 6 joints, {len(meshes)} meshes, {count} solids.', flush=True)
    print(json.dumps(replacements,ensure_ascii=False,indent=2),flush=True)


if __name__ == '__main__':
    main()
