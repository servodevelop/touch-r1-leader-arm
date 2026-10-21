"""把指定 V3.2 STEP 导入为 URDF 专用 FCStd 快照，保留原 STEP 在用户本地。"""
from pathlib import Path
import argparse
import hashlib
import json
import tempfile
import FreeCAD as App
import Import

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'hardware/robot-description/source'
SOURCE_SHA256 = 'f2654e3ba64084a5638cb16c66ebac0a958ef50be641a09abca82bdf0ccb2bc0'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('step', type=Path)
    args = parser.parse_args()
    assert hashlib.sha256(args.step.read_bytes()).hexdigest() == SOURCE_SHA256, 'STEP 已变化，需复核映射'
    pref = App.ParamGet('User parameter:BaseApp/Preferences/Mod/Import')
    pref.SetBool('ImportMode', False)
    pref.SetBool('ReadShapeCompoundMode', False)
    doc = App.newDocument('TouchR1V32')
    Import.insert(str(args.step), doc.Name)
    doc.recompute()
    root = doc.getObject('_45_X2_535551FA8235673A_X0__ASM')
    assert len(root.Shape.Solids) == 115 and len(root.Group) == 24
    excluded = []
    for obj in list(root.Group):
        if obj.Label in {'A000', 'B000'}:
            excluded.append({'object': obj.Name, 'label': obj.Label, 'solids': len(obj.Shape.Solids)})
            doc.removeObject(obj.Name)
    assert {o['label'] for o in excluded} == {'A000', 'B000'}
    doc.recompute()
    assert root.Shape.isValid() and len(root.Shape.Solids) == 113
    OUTPUT.mkdir(parents=True, exist_ok=True)
    # 文件名沿用既有下载链接；内容升级为 V3.2，并在来源记录中明确版本。
    snapshot = OUTPUT / 'r1-hd-urdf-only.FCStd'
    # 先保存到临时目录，避免 FreeCAD 在资源目录留下 FCBak 备份。
    with tempfile.TemporaryDirectory(prefix='touch-r1-source-') as temp:
        staged = Path(temp) / snapshot.name
        doc.saveAs(str(staged))
        snapshot.write_bytes(staged.read_bytes())
    metadata = {'revision': 'V3.2', 'original_step_name': args.step.name,
                'original_step_sha256': SOURCE_SHA256, 'original_step_solids': 115,
                'excluded_objects': excluded, 'snapshot_solids': 113,
                'snapshot_sha256': hashlib.sha256(snapshot.read_bytes()).hexdigest(),
                'note_zh': 'FCStd 由指定 STEP 导入，移除 A000、B000；原 STEP 不复制进仓库。'}
    (OUTPUT/'assembly-source.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2)+'\n')
    App.closeDocument(doc.Name)
    print('已导入 V3.2：115 个源实体，排除两个限位块后保留 113 个实体。')


if __name__ == '__main__':
    main()
