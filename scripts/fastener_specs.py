"""从 R1 简化 CAD 的圆柱面核查紧固件尺寸，并输出按实物确认的品名与规格。

品名、规格与材质来自用户对实物的确认（2026-10-20）；几何尺寸仍由 CAD 圆柱面测量，
两者不一致之处写入 ``assessment_zh``，不据源名称推定螺纹。
"""

# 源 PRODUCT 编号 → 紧固件类别。V3.3 起三颗自攻螺丝合并为 GB_T70_1-M3X530001 一个源件。
FASTENER_PRODUCTS = {
    89966: 'self-tapping',
    91683: 'shoulder',
    113237: 'unclassified',
}
# 前两种沿 Z 轴，塞打螺丝沿 Y 轴；测量头下长度而不是总包围长度。
AXES = {89966: 'Z', 91683: 'Y', 113237: 'Z'}
REFERENCE = 'https://github.com/servodevelop/Star-Arm-102/blob/main/hardware/102-hd/README.zh.md#bill-of-materials'


def _measure(shape, axis):
    import Part
    groups = {}
    for face in shape.Faces:
        surface = face.Surface
        if not isinstance(surface, Part.Cylinder):
            continue
        assert abs(abs(getattr(surface.Axis, axis.lower())) - 1) < 1e-6
        radius = round(surface.Radius, 6)
        lo = getattr(face.BoundBox, axis + 'Min')
        hi = getattr(face.BoundBox, axis + 'Max')
        previous = groups.get(radius, (lo, hi))
        groups[radius] = (min(previous[0], lo), max(previous[1], hi))
    return groups


def describe_fastener(product, shape):
    family = FASTENER_PRODUCTS.get(product)
    if family is None:
        return None
    groups = _measure(shape, AXES[product])
    head_radius = max(groups)
    head_lo, head_hi = groups[head_radius]
    dimensions = {
        'head_diameter_mm': round(2 * head_radius, 4),
        'head_height_mm': round(head_hi - head_lo, 4),
    }
    if family == 'shoulder':
        assert set(groups) == {1.0, 1.25, 2.5}, '圆柱尺寸变化，请重新审核规格'
        shoulder_lo, shoulder_hi = groups[1.25]
        tip_lo, tip_hi = groups[1.0]
        assert abs(shoulder_lo - head_hi) < 1e-4 and abs(tip_lo - shoulder_hi) < 1e-4
        dimensions.update({
            'shoulder_diameter_mm': 2.5,
            'shoulder_length_mm': round(shoulder_hi - head_hi, 4),
            'tip_diameter_mm': 2.0,
            'tip_length_mm': round(tip_hi - tip_lo, 4),
            'under_head_length_mm': round(tip_hi - head_hi, 4),
        })
        assert dimensions == dict(head_diameter_mm=5.0, head_height_mm=2.5,
                                  shoulder_diameter_mm=2.5, shoulder_length_mm=3.0,
                                  tip_diameter_mm=2.0, tip_length_mm=4.0,
                                  under_head_length_mm=7.0)
        name = '304 塞打螺丝（轴肩螺钉）'
        specification = 'Ø2.5 × M2 × 3'
        note = ('按实物确认为 304 塞打螺丝，规格 Ø2.5 × M2 × 3：轴肩 Ø2.5 × 3 mm、螺纹 M2。'
                '源名称含 M3，与轴肩直径不一致，不据名称认定 M3。V3.3 装配体只用 1 件。')
    elif family == 'self-tapping':
        assert set(groups) == {1.5, 2.75}, '圆柱尺寸变化，请重新审核规格'
        shank_lo, _ = groups[1.5]
        dimensions.update({'shank_diameter_mm': 3.0,
                           'under_head_length_mm': round(head_lo - shank_lo, 4)})
        assert dimensions == dict(head_diameter_mm=5.5, head_height_mm=3.0,
                                  shank_diameter_mm=3.0, under_head_length_mm=4.0)
        name = '304 薄头内六角平尾自攻螺丝'
        specification = 'HB3 × 5'
        note = ('按实物确认为 304 薄头内六角平尾自攻螺丝 HB3 × 5：螺纹公称 Ø3 mm、长度 5 mm、薄头内六角、'
                '平尾自攻。V3.3 装配体中三颗合并为一个源件 GB_T70_1-M3X530001；'
                '头厚由 V3.2 的 2.00 mm 改为 3.00 mm（头下长度与螺纹不变），实物是否同步加厚待确认，'
                '确认后「薄头」的表述需一并复核。')
    else:
        assert set(groups) == {1.5, 2.75}, '圆柱尺寸变化，请重新审核规格'
        shank_lo, shank_hi = groups[1.5]
        dimensions.update({'shank_diameter_mm': 3.0,
                           'shank_cylinder_length_mm': round(shank_hi - shank_lo, 4),
                           'under_head_length_mm': round(head_lo - shank_lo, 4)})
        assert dimensions == dict(head_diameter_mm=5.5, head_height_mm=2.7,
                                  shank_diameter_mm=3.0, shank_cylinder_length_mm=9.33,
                                  under_head_length_mm=9.5)
        name = '内六角圆柱头螺钉'
        specification = 'M3 × 10'
        note = ('V3.3 新增的 1 件紧固件，源名称为 PRT0007，未沿用既有紧固件源名的 M2X4X30001 一类命名。'
                '按实物确认为 M3 × 10 内六角圆柱头螺钉（2026-10-23）。CAD 圆柱面实测：'
                '头部 Ø5.50 × 2.70 mm、杆部 Ø3.00 mm、头下长度 9.50 mm，'
                '另有 6 个环面与 6 个锥面，杆部按螺纹建模；包围盒 5.95 × 5.95 × 13.00 mm。'
                'CAD 头下长度比标称 10 mm 短 0.5 mm，差值来自螺纹收尾与头部倒角的建模方式，'
                '采购仍按 M3 × 10。')
    return {
        'name_zh': name,
        'specification_zh': specification,
        'dimensions_mm': dimensions,
        'measurement_basis_zh': '按圆柱面半径及轴向边界测量；含头总长不作为螺钉标称长度。',
        'assessment_zh': note,
        'confirmation_status_zh': ('品名、规格与 304 不锈钢材质按实物确认（2026-10-20）；螺纹精度、强度等级及表面处理待采购确认。'
                                   if family != 'unclassified' else
                                   '品名与规格按实物确认（2026-10-23，M3 × 10 内六角圆柱头螺钉）；材质、强度等级与表面处理待采购确认。'),
        'format_reference': REFERENCE,
        'reference_scope_zh': '仅参考 102 的品名与规格表达方式，不继承其尺寸、数量和采购属性。',
    }
