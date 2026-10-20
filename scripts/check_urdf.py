"""检查 URDF 拓扑、轴向、网格、米制尺度及 CAD 零位映射；仅依赖标准库。"""
from pathlib import Path
import hashlib
import json
import math
import struct
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'hardware/robot-description'
PACKAGE = DIRECTORY / 'touch_r1_description'


def main():
    path = PACKAGE / 'urdf/touch-r1.urdf'
    robot = ET.parse(path).getroot()
    manifest = json.loads((DIRECTORY/'kinematics.json').read_text())
    assert manifest['source_format'] == 'FCStd'
    assert manifest['original_assembly_solids'] == 97
    assert manifest['replacement_assembly_solids'] == 100
    mapped = []
    solids = 0
    for item in manifest['source_mapping']:
        assert item.get('source_label') not in {'A000', 'B000'}, '限位块不能重新进入 URDF'
        if 'source_leaf_objects' in item:
            mapped.extend(item['source_leaf_objects'])
            solids += item['body_solids'] + item['horn_solids']
        else:
            mapped.append(item['source_object'])
            solids += item['solids']
    assert len(mapped) == len(set(mapped)) == 97
    assert set(mapped) == set(manifest['source_leaf_objects'])
    assert solids == 100
    links = {link.attrib['name']: link for link in robot.findall('link')}
    joints = robot.findall('joint')
    assert len(links)==7 and len(joints)==6
    children = set()
    origins = {'base_link': [0,0,0]}
    for joint, measured in zip(joints, manifest['joints']):
        parent = joint.find('parent').attrib['link']; child = joint.find('child').attrib['link']
        assert parent in origins and child in links and child not in children
        assert joint.attrib['type']=='continuous'
        axis = list(map(float,joint.find('axis').attrib['xyz'].split()))
        assert abs(sum(x*x for x in axis)-1)<1e-8
        delta = list(map(float,joint.find('origin').attrib['xyz'].split()))
        assert joint.find('origin').attrib['rpy']=='0 0 0'
        origins[child] = [a+b for a,b in zip(origins[parent],delta)]
        px,py,pz = measured['cad_axis_point_mm']
        expected = [px/1000,-pz/1000,(py+manifest['floor_offset_mm'])/1000]
        assert max(abs(a-b) for a,b in zip(origins[child],expected))<1e-8
        assert measured['coaxial_error_mm']<.02
        children.add(child)
    assert set(links)-children=={'base_link'}
    expected_meshes={str((PACKAGE/m['file']).resolve()):m for m in manifest['meshes']}
    all_low=[float('inf')]*3; all_high=[-float('inf')]*3
    triangles=0; loaded=set()
    for name,link in links.items():
        for visual in link.findall('visual'):
            meshpath=(path.parent/visual.find('geometry/mesh').attrib['filename']).resolve()
            assert meshpath.is_relative_to(PACKAGE.resolve())
            data=meshpath.read_bytes(); declared=expected_meshes[str(meshpath)]
            assert hashlib.sha256(data).hexdigest()==declared['sha256']
            n=struct.unpack_from('<I',data,80)[0]; assert len(data)==84+50*n and n>0
            assert n==declared['triangles']
            low=[float('inf')]*3;high=[-float('inf')]*3
            for record in struct.iter_unpack('<12fH',data[84:]):
                assert all(math.isfinite(v) for v in record[:12])
                for start in [3,6,9]:
                    for i in range(3):
                        low[i]=min(low[i],record[start+i]); high[i]=max(high[i],record[start+i])
            for i in range(3):
                all_low[i]=min(all_low[i],low[i]+origins[name][i])
                all_high[i]=max(all_high[i],high[i]+origins[name][i])
                assert abs(low[i]-declared['bounds_m'][0][i])<1e-6
                assert abs(high[i]-declared['bounds_m'][1][i])<1e-6
            loaded.add(str(meshpath));triangles+=n
    assert loaded==set(expected_meshes)
    assert loaded == {str(p.resolve()) for p in (PACKAGE/'meshes').glob('*.stl')}, '有残留的旧网格'
    assert all(.03<hi-lo<1 for lo,hi in zip(all_low,all_high)), '检查毫米到米的转换'
    assert abs(all_low[2])<.001, '基座底面应在 Z=0 附近'
    for source in manifest['sources']:
        assert hashlib.sha256((ROOT/'hardware'/source['file']).read_bytes()).hexdigest()==source['sha256']
    assert hashlib.sha256((ROOT/'hardware'/manifest['source_assembly']).read_bytes()).hexdigest() == manifest['source_assembly_sha256']
    print(f'URDF 检查通过：7 个连杆，6 个活动关节，{len(loaded)} 个网格，{triangles} 个三角面。')
    print('零位包围尺寸（米）：', [round(hi-lo,6) for lo,hi in zip(all_low,all_high)])
    print('已核对连通树、轴单位向量、CAD 零位映射、源文件和网格校验值；不代表实机／动力学验证。')
    print('97 个源实体均唯一归属；替换舵机后 100 个实体，未包含 A000／B000 限位块。')


if __name__=='__main__':
    main()
