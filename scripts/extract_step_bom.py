"""Extract the supplied Touch R1 V3.3 STEP's top-level CAD BOM with FreeCAD.

Run with FreeCAD's Python environment. Paths are resolved from this repository.
This is an assembly-instance BOM, not a complete manufacturing/purchasing BOM.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import re
import struct
import zipfile

import FreeCAD as App
import Import
import Part

from fastener_specs import describe_fastener

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'hardware'
SOURCE = MODEL / 'step/assembly/touch-r1-leader-arm-v3.3-1023.stp'
SOURCE_SHA256 = '7f96310c42fe7f7440359c246477c20b67a0f7d25fc3f097860783a02cfce782'

# The source PRODUCT IDs retain the distinction between similarly shaped models.
# Names describe the supplied CAD geometry, not approved supplier specifications.
ITEMS = [
    (28758, 'touch-r1-servo-rp8-u45h-m-c028', '舵机子装配'),
    (53697, 'touch-r1-servo-25-50kg-0001', '舵机子装配（型号待确认）'),
    (7186, 'touch-r1-joint-1', '关节 1 结构件'),
    (34617, 'touch-r1-joint-2', '关节 2 结构件'),
    (64264, 'touch-r1-joint-3', '关节 3 结构件'),
    (75582, 'touch-r1-joint-4', '关节 4 结构件'),
    (84888, 'touch-r1-joint-5', '关节 5 结构件'),
    (89282, 'touch-r1-joint-6', '关节 6 结构件'),
    (101568, 'touch-r1-handle-assembly', '手柄装配'),
    (105793, 'touch-r1-finger-left', '左手指'),
    (110016, 'touch-r1-finger-right', '右手指'),
    (91198, 'touch-r1-part-a000', '支架 A000（用途待确认）'),
    (112460, 'touch-r1-base-plate', '底座（固定板底座）'),
    (89966, 'touch-r1-fastener-gb-t70-1-m3x530001', '内六角紧固件 GB_T70_1-M3X530001'),
    (91683, 'touch-r1-fastener-m3x3x60001', '塞打螺丝 M2X4X30001'),
    (113237, 'touch-r1-fastener-prt0007', '紧固件 PRT0007'),
    (29540, 'touch-r1-spacer', '垫片'),
]

# Parts get an STL mesh alongside the STEP export; purchased sub-assemblies and
# standard fasteners do not. The spacer is excluded because it is not a real part.
STL_ITEMS = {'touch-r1-joint-1', 'touch-r1-joint-2', 'touch-r1-joint-3', 'touch-r1-joint-4',
             'touch-r1-joint-5', 'touch-r1-joint-6', 'touch-r1-handle-assembly',
             'touch-r1-finger-left', 'touch-r1-finger-right', 'touch-r1-part-a000',
             'touch-r1-base-plate'}
# 标准紧固件按标准号采购，不提供独立 STEP 导出件，只在 BOM 内记录来源与规格。
NO_STEP_EXPORT = {'touch-r1-fastener-gb-t70-1-m3x530001', 'touch-r1-fastener-m3x3x60001',
                  'touch-r1-fastener-prt0007'}
# 下载包名与包内目录沿用 Star Arm 102 的写法：包名带装配体日期，包内是固定目录。
STL_ARCHIVE = 'touch-r1-stl-2026-10-23.zip'
STL_ARCHIVE_FOLDER = 'touch-r1-stl'


def decode_name(text):
    return re.sub(r'_X2_([0-9A-F]+)_X0_',
                  lambda m: bytes.fromhex(m[1]).decode('utf-16-be'), text)


def read_graph(text):
    # This parser targets the checksum-pinned Creo export, whose entity strings
    # contain no embedded semicolons. It is not a general-purpose STEP parser.
    entities = {int(n): body for n, body in re.findall(r'#(\d+)\s*=\s*(.*?);', text, re.S)}
    refs = lambda body: [int(n) for n in re.findall(r'#(\d+)', body)]
    products = {n: re.findall("'([^']*)'", body)[0]
                for n, body in entities.items() if body.startswith('PRODUCT(')}
    definitions = {}
    for n, body in entities.items():
        if body.startswith('PRODUCT_DEFINITION('):
            formation = refs(body)[0]
            definitions[n] = refs(entities[formation])[0]
    edges = []
    for n, body in entities.items():
        if body.startswith('NEXT_ASSEMBLY_USAGE_OCCURRENCE('):
            parent, child = refs(body)[:2]
            edges.append({'entity': n, 'parent_definition': parent, 'child_definition': child})
    roots = {e['parent_definition'] for e in edges} - {e['child_definition'] for e in edges}
    assert len(roots) == 1, 'Expected one assembly root'
    root = roots.pop()
    return products, definitions, edges, root


def metrics(shape):
    box = shape.BoundBox
    return {'solid_count': len(shape.Solids), 'valid': shape.isValid(),
            'volume_mm3': shape.Volume,
            'local_bbox_mm': [box.XLength, box.YLength, box.ZLength]}


def mesh_data(shape):
    vertices, triangles = [], []
    # Tessellate each CAD face independently so sharp boundaries remain sharp.
    for face in shape.Faces:
        points, facets = face.tessellate(0.06)
        offset = len(vertices)
        vertices.extend([[p.x, p.y, p.z] for p in points])
        triangles.extend([[a + offset, b + offset, c + offset] for a, b, c in facets])
    return {'vertices': vertices, 'triangles': triangles}


def write_stl(shape, path, tolerance=0.05, angle=0.3):
    """Write a binary STL plus a watertightness report for one solid or sub-assembly."""
    import MeshPart
    mesh = MeshPart.meshFromShape(Shape=shape, LinearDeflection=tolerance,
                                  AngularDeflection=angle, Relative=False)
    points = [(point.Vector.x, point.Vector.y, point.Vector.z) for point in mesh.Points]
    triangles = [[points[i] for i in facet.PointIndices] for facet in mesh.Facets]
    edges = Counter()
    for triangle in triangles:
        for a, b in ((0, 1), (1, 2), (2, 0)):
            edges[frozenset((triangle[a], triangle[b]))] += 1
    open_edges = sum(1 for count in edges.values() if count != 2)
    with path.open('wb') as stream:
        stream.write(b'Touch R1 leader arm printable mesh'.ljust(80, b'\0'))
        stream.write(struct.pack('<I', len(triangles)))
        for triangle in triangles:
            stream.write(struct.pack('<3f', 0, 0, 0))
            for point in triangle:
                stream.write(struct.pack('<3f', *point))
            stream.write(struct.pack('<H', 0))
    return {'triangles': len(triangles), 'vertices': len(points),
            'open_edges': open_edges, 'bytes': path.stat().st_size}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh-dir', type=Path, required=True,
                        help='Temporary directory for render meshes; keep outside the repository')
    parser.add_argument('--stl-dir', type=Path, default=MODEL / 'stl',
                        help='Directory for the printable STL meshes (default: hardware/stl)')
    args = parser.parse_args()
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA256, 'Source changed: review the mapping first'
    text = data.decode('ascii')
    products, definitions, edges, root_id = read_graph(text)
    assert 'SI_UNIT(.MILLI.,.METRE.)' in text
    top_edges = [e for e in edges if e['parent_definition'] == root_id]
    counts = Counter(definitions[e['child_definition']] for e in top_edges)
    assert set(counts) == {p for p, *_ in ITEMS}
    assert sum(counts.values()) == 24 and len(counts) == 17
    by_parent = defaultdict(list)
    for edge in edges:
        by_parent[edge['parent_definition']].append(edge['child_definition'])
    def leaves(definition):
        children = by_parent[definition]
        return sum(leaves(child) for child in children) if children else 1
    assert leaves(root_id) == 115

    pref = App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import')
    # Change only this Python process's preferences; do not save user settings.
    pref.SetBool('ImportMode', False)
    pref.SetBool('ReadShapeCompoundMode', False)
    document = App.newDocument('TouchR1BOM')
    Import.insert(str(SOURCE), document.Name)
    document.recompute()
    roots = [o for o in document.Objects if o.TypeId == 'App::Part'
             and o.Label == products[definitions[root_id]] and not o.InList]
    assert len(roots) == 1
    assembly = roots[0]
    assert len(assembly.Group) == len(top_edges)
    assert assembly.Shape.isValid() and len(assembly.Shape.Solids) == leaves(root_id)

    shapes, occurrences = {}, defaultdict(list)
    for edge, obj in zip(top_edges, assembly.Group):
        product = definitions[edge['child_definition']]
        shape = obj.Shape.copy()
        # Remove this occurrence's placement, preserving internal subassembly
        # placements. Each export stays in the source component's coordinates.
        shape.Placement = App.Placement()
        measured = metrics(shape)
        assert measured['valid'] and measured['solid_count'] == leaves(edge['child_definition'])
        if product not in shapes:
            assert obj.Label == products[product], (obj.Label, products[product])
            shapes[product] = shape
        else:
            first = metrics(shapes[product])
            assert abs(first['volume_mm3'] - measured['volume_mm3']) < 1e-4
            assert all(abs(a-b) < 1e-5 for a,b in zip(first['local_bbox_mm'], measured['local_bbox_mm']))
        occurrences[product].append({'source_occurrence_entity': edge['entity'],
                                    'source_definition_entity': edge['child_definition'],
                                    'imported_label': obj.Label,
                                    'placement_matrix': list(obj.Placement.toMatrix().A)})

    parts = MODEL / 'step/parts'
    parts.mkdir(exist_ok=True, parents=True)
    stl_dir = args.stl_dir
    stl_dir.mkdir(exist_ok=True, parents=True)
    args.mesh_dir.mkdir(exist_ok=True, parents=True)
    rows = []
    meshes = []
    for number, (product, identifier, zh) in enumerate(ITEMS, 1):
        shape = shapes[product]
        original = metrics(shape)
        row = {'no': number, 'id': identifier, 'name_zh': zh,
               'source_product_entity': product, 'source_name': products[product],
               'decoded_source_name': decode_name(products[product]),
               'quantity': counts[product], 'unit': 'subassembly' if original['solid_count'] > 1 else 'piece',
               'step_file': None, 'image': f'images/{identifier}.png',
               'geometry': original, 'source_shape_max_tolerance_mm': shape.getTolerance(1),
               'occurrences': occurrences[product]}
        if identifier not in NO_STEP_EXPORT:
            filename = parts / f'{identifier}.step'
            shape.exportStep(str(filename))
            check = Part.read(str(filename))
            exported = metrics(check)
            assert exported['valid'] and exported['solid_count'] == original['solid_count']
            assert abs(exported['volume_mm3'] - original['volume_mm3']) <= max(1e-3, original['volume_mm3'] * 1e-4)
            assert all(abs(a-b) < .001 for a,b in zip(original['local_bbox_mm'], exported['local_bbox_mm']))
            row.update({'step_file': f'step/parts/{identifier}.step', 'export_roundtrip_valid': True,
                        'export_volume_relative_error': abs(exported['volume_mm3'] - original['volume_mm3']) / original['volume_mm3'],
                        'export_bbox_max_error_mm': max(abs(a-b) for a,b in zip(original['local_bbox_mm'], exported['local_bbox_mm']))})
        fastener = describe_fastener(product, shape)
        if fastener:
            row['name_zh'] = fastener['name_zh']
            row['fastener_specification'] = fastener
        if identifier in STL_ITEMS:
            stl_path = stl_dir / f'{identifier}.stl'
            mesh = write_stl(shape, stl_path)
            assert mesh['triangles'] and mesh['open_edges'] == 0, (identifier, mesh)
            row['stl_file'] = f'stl/{identifier}.stl'
            row['stl_mesh'] = mesh
            meshes.append((identifier, stl_path, mesh))
        rows.append(row)
        (args.mesh_dir / f'{identifier}.json').write_text(json.dumps(mesh_data(shape)), encoding='utf-8')
        print(f"Exported {number:02d}: {identifier} x {counts[product]}", flush=True)
    (args.mesh_dir / 'touch-r1-assembly.json').write_text(json.dumps(mesh_data(assembly.Shape)), encoding='utf-8')
    # 单包下载：与 stl/ 散件逐字节同源，条目放在同名子目录里（参照 Star Arm 102 的打包方式）。
    archive = stl_dir / 'downloads' / STL_ARCHIVE
    archive.parent.mkdir(exist_ok=True, parents=True)
    folder = STL_ARCHIVE_FOLDER
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as bundle:
        for identifier, stl_path, _ in meshes:
            bundle.write(stl_path, f'{folder}/{stl_path.name}')
    with zipfile.ZipFile(archive) as bundle:
        archived = {info.filename.split('/')[-1]: info.file_size for info in bundle.infolist()}
    assert archived == {path.name: mesh['bytes'] for _, path, mesh in meshes}, '下载包与散件不一致'
    manifest = {'schema_version': 2, 'model': 'Touch R1 Leader Arm', 'revision': 'V3.3',
                'source_file': SOURCE.relative_to(MODEL).as_posix(), 'source_sha256': SOURCE_SHA256,
                'source_length_unit': 'mm', 'root_product_entity': definitions[root_id],
                'root_definition_entity': root_id, 'top_level_occurrences': len(top_edges),
                'unique_bom_items': len(rows), 'expanded_leaf_occurrences': leaves(root_id),
                'assembly_geometry': metrics(assembly.Shape),
                'export_check_tolerances': {'relative_volume': 1e-4, 'absolute_volume_mm3': 1e-3, 'bbox_mm': .001},
                'stl_tessellation': {'linear_deflection_mm': .05, 'angular_deflection_rad': .3,
                                     'format': 'binary STL', 'closed_mesh_required': True},
                'stl_archive': {'file': archive.relative_to(MODEL).as_posix(), 'entries': len(archived),
                                'folder': folder, 'bytes': archive.stat().st_size},
                'quantity_basis': '按根装配直接子项统计，合并重复 PRODUCT 引用；舵机内部零件不重复列为 BOM 行。',
                'procurement_status': '由 CAD 提取；采购规格、未建模组件与清单完整性待工程确认。',
                'items': rows,
                'source_products': {str(p): {'raw_name': name, 'decoded_name': decode_name(name)} for p,name in products.items()},
                'source_product_definitions': definitions, 'source_assembly_edges': edges,
                'tool': {'freecad': '.'.join(App.Version()[:3])}}
    (MODEL / 'bom.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    for directory in (parts, stl_dir):
        placeholder = directory / '.gitkeep'
        if placeholder.exists():
            placeholder.unlink()
    App.closeDocument(document.Name)
    print(f'Verified {len(rows) - len(NO_STEP_EXPORT)} STEP exports; {len(meshes)} closed STL meshes '
          f'in {len(archived)}-file archive {STL_ARCHIVE}; '
          f'{len(top_edges)} top-level occurrences; {leaves(root_id)} expanded solids.')


if __name__ == '__main__':
    main()

