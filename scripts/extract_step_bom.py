"""Extract the supplied Touch R1 V3.2 STEP's top-level CAD BOM with FreeCAD.

Run with FreeCAD's Python environment. Paths are resolved from this repository.
This is an assembly-instance BOM, not a complete manufacturing/purchasing BOM.
"""
from collections import Counter, defaultdict
import argparse
import hashlib
import json
from pathlib import Path
import re

import FreeCAD as App
import Import
import Part

from fastener_specs import describe_fastener

ROOT = Path(__file__).resolve().parents[1]
MODEL = ROOT / 'hardware'
SOURCE = MODEL / 'step/assembly/touch-r1-leader-arm-v3.2-1013.stp'
SOURCE_SHA256 = 'f2654e3ba64084a5638cb16c66ebac0a958ef50be641a09abca82bdf0ccb2bc0'

# The source PRODUCT IDs retain the distinction between similarly shaped models.
# Names describe the supplied CAD geometry, not approved supplier specifications.
ITEMS = [
    (28683, 'touch-r1-servo-rp8-u45h-m-c028', '舵机子装配'),
    (55700, 'touch-r1-servo-25-50kg-0001', '舵机子装配（型号待确认）'),
    (7112, 'touch-r1-joint-1', '关节 1 结构件'),
    (35211, 'touch-r1-joint-2', '关节 2 结构件'),
    (66078, 'touch-r1-joint-3', '关节 3 结构件'),
    (77328, 'touch-r1-joint-4', '关节 4 结构件'),
    (86268, 'touch-r1-joint-5', '关节 5 结构件'),
    (90662, 'touch-r1-joint-6', '关节 6 结构件'),
    (103509, 'touch-r1-handle-assembly', '手柄装配'),
    (107734, 'touch-r1-finger-left', '左手指'),
    (111955, 'touch-r1-finger-right', '右手指'),
    (29465, 'touch-r1-spacer', '垫片'),
    (92606, 'touch-r1-part-a000', '支架 A000（用途待确认）'),
    (93572, 'touch-r1-part-b000', '支架 B000（用途待确认）'),
    (35916, 'touch-r1-fastener-prt0001', '内六角紧固件 PRT0001'),
    (36620, 'touch-r1-fastener-prt0002', '内六角紧固件 PRT0002'),
    (91375, 'touch-r1-fastener-gb-t70-1-m3x400', '内六角紧固件 GB_T70_1-M3X400'),
    (93090, 'touch-r1-fastener-m3x3x60001', '塞打螺丝 M2X4X30001'),
]


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


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mesh-dir', type=Path, required=True,
                        help='Temporary directory for render meshes; keep outside the repository')
    args = parser.parse_args()
    data = SOURCE.read_bytes()
    assert hashlib.sha256(data).hexdigest() == SOURCE_SHA256, 'Source changed: review the mapping first'
    text = data.decode('ascii')
    products, definitions, edges, root_id = read_graph(text)
    assert 'SI_UNIT(.MILLI.,.METRE.)' in text
    top_edges = [e for e in edges if e['parent_definition'] == root_id]
    counts = Counter(definitions[e['child_definition']] for e in top_edges)
    assert set(counts) == {p for p, *_ in ITEMS}
    assert sum(counts.values()) == 24 and len(counts) == 18
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
    args.mesh_dir.mkdir(exist_ok=True, parents=True)
    rows = []
    for number, (product, identifier, zh) in enumerate(ITEMS, 1):
        shape = shapes[product]
        filename = parts / f'{identifier}.step'
        shape.exportStep(str(filename))
        check = Part.read(str(filename))
        original, exported = metrics(shape), metrics(check)
        assert exported['valid'] and exported['solid_count'] == original['solid_count']
        assert abs(exported['volume_mm3'] - original['volume_mm3']) <= max(1e-3, original['volume_mm3'] * 1e-4)
        assert all(abs(a-b) < .001 for a,b in zip(original['local_bbox_mm'], exported['local_bbox_mm']))
        row = {'no': number, 'id': identifier, 'name_zh': zh,
               'source_product_entity': product, 'source_name': products[product],
               'decoded_source_name': decode_name(products[product]),
               'quantity': counts[product], 'unit': 'subassembly' if original['solid_count'] > 1 else 'piece',
               'step_file': f'step/parts/{identifier}.step', 'image': f'images/{identifier}.png',
               'geometry': original, 'source_shape_max_tolerance_mm': shape.getTolerance(1), 'export_roundtrip_valid': True,
               'export_volume_relative_error': abs(exported['volume_mm3'] - original['volume_mm3']) / original['volume_mm3'],
               'export_bbox_max_error_mm': max(abs(a-b) for a,b in zip(original['local_bbox_mm'], exported['local_bbox_mm'])),
               'occurrences': occurrences[product]}
        fastener = describe_fastener(product, shape)
        if fastener:
            row['name_zh'] = fastener['name_zh']
            row['fastener_specification'] = fastener
        rows.append(row)
        (args.mesh_dir / f'{identifier}.json').write_text(json.dumps(mesh_data(shape)), encoding='utf-8')
        print(f"Exported {number:02d}: {identifier} x {counts[product]}", flush=True)
    (args.mesh_dir / 'touch-r1-assembly.json').write_text(json.dumps(mesh_data(assembly.Shape)), encoding='utf-8')
    manifest = {'schema_version': 2, 'model': 'Touch R1 Leader Arm', 'revision': 'V3.2',
                'source_file': SOURCE.relative_to(MODEL).as_posix(), 'source_sha256': SOURCE_SHA256,
                'source_length_unit': 'mm', 'root_product_entity': definitions[root_id],
                'root_definition_entity': root_id, 'top_level_occurrences': len(top_edges),
                'unique_bom_items': len(rows), 'expanded_leaf_occurrences': leaves(root_id),
                'assembly_geometry': metrics(assembly.Shape),
                'export_check_tolerances': {'relative_volume': 1e-4, 'absolute_volume_mm3': 1e-3, 'bbox_mm': .001},
                'quantity_basis': '按根装配直接子项统计，合并重复 PRODUCT 引用；舵机内部零件不重复列为 BOM 行。',
                'procurement_status': '由 CAD 提取；采购规格、未建模组件与清单完整性待工程确认。',
                'items': rows,
                'source_products': {str(p): {'raw_name': name, 'decoded_name': decode_name(name)} for p,name in products.items()},
                'source_product_definitions': definitions, 'source_assembly_edges': edges,
                'tool': {'freecad': '.'.join(App.Version()[:3])}}
    (MODEL / 'bom.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    placeholder = parts / '.gitkeep'
    if placeholder.exists():
        placeholder.unlink()
    App.closeDocument(document.Name)
    print('Verified 18 STEP exports; 24 top-level occurrences; 115 expanded solids.')


if __name__ == '__main__':
    main()

