"""从 R1 简化 CAD 的圆柱面核查紧固件尺寸，并输出按实物确认的品名与规格。

品名、规格与材质来自用户对实物的确认（2026-10-20）；几何尺寸仍由 CAD 圆柱面测量，
两者不一致之处写入 ``assessment_zh``，不据源名称推定螺纹。
"""

FASTENER_PRODUCTS = {35916, 36620, 99391, 101106}
REFERENCE = 'https://github.com/servodevelop/Star-Arm-102/blob/main/hardware/102-hd/README.zh.md#bill-of-materials'


def describe_fastener(product, shape):
    if product not in FASTENER_PRODUCTS:
        return None
    # 前三种沿 Z 轴，台阶件沿 Y 轴；测量头下长度而不是总包围长度。
    axis = 'Y' if product == 101106 else 'Z'
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
    expected = {1.0, 1.25, 2.5} if product == 101106 else {1.5, 2.75}
    assert set(groups) == expected, '圆柱尺寸变化，请重新审核规格'
    head_radius = max(groups)
    head_lo, head_hi = groups[head_radius]
    dimensions = {
        'head_diameter_mm': round(2 * head_radius, 4),
        'head_height_mm': round(head_hi - head_lo, 4),
    }
    if product == 101106:
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
                '源名称含 M3，与轴肩直径不一致，不据名称认定 M3。')
    else:
        shank_lo, _ = groups[1.5]
        dimensions.update({'shank_diameter_mm': 3.0,
                           'under_head_length_mm': round(head_lo - shank_lo, 4)})
        assert dimensions == dict(head_diameter_mm=5.5, head_height_mm=2.0,
                                  shank_diameter_mm=3.0, under_head_length_mm=4.0)
        name = '304 薄头内六角平尾自攻螺丝'
        specification = 'HB3 × 5'
        note = ('按实物确认为 304 薄头内六角平尾自攻螺丝 HB3 × 5：螺纹公称 Ø3 mm、长度 5 mm、薄头内六角、'
                '平尾自攻。PRT0001、PRT0002、GB_T70_1-M3X400 三个源 PRODUCT 为同一采购件。')
    return {
        'name_zh': name,
        'specification_zh': specification,
        'dimensions_mm': dimensions,
        'measurement_basis_zh': '按圆柱面半径及轴向边界测量；含头总长不作为螺钉标称长度。',
        'assessment_zh': note,
        'confirmation_status_zh': '品名、规格与 304 不锈钢材质按实物确认（2026-10-20）；螺纹精度、强度等级及表面处理待采购确认。',
        'format_reference': REFERENCE,
        'reference_scope_zh': '仅参考 102 的品名与规格表达方式，不继承其尺寸、数量和采购属性。',
    }
