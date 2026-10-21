"""打包 URDF、网格与离线预览；在仓库根目录执行。"""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1] / 'hardware/robot-description'
with ZipFile(ROOT / 'touch-r1-urdf.zip', 'w', compression=ZIP_DEFLATED) as archive:
    for directory in ['touch_r1_description', 'preview']:
        for path in sorted((ROOT/directory).rglob('*')):
            if path.is_file():
                archive.write(path, path.relative_to(ROOT))
    archive.write(ROOT/'kinematics.json', 'kinematics.json')
    archive.writestr('使用说明.txt', '''Touch R1 Leader Arm V3.2 — 七轴与双 Finger 运动学预览

在解压目录运行：
python -m http.server 8765 --bind 127.0.0.1
然后在浏览器打开 http://127.0.0.1:8765/preview/

URDF: touch_r1_description/urdf/touch-r1.urdf
请保持 URDF 和 meshes 的相对位置。预览依赖已包含，不需联网。

源模型：V3.2 STEP 导入的 r1-hd-urdf-only.FCStd 快照，已移除 A000、B000。
包含七个舵机、左右 finger；J7 驱动右侧，左侧通过 URDF mimic 反向联动。
1:1 传动关系按 CAD 齿形推定，待实物确认。
0° 是源 FCStd 装配姿态，不是实机编码器零位。
continuous 仅供可视化，不代表实机可无限旋转；J1–J6 ±90°、J7 0–25° 都只是界面演示范围。
未提供实机限位、质量、惯量、碰撞模型、控制接口或 ROS 启动包。
保留源文件中的垫片和紧固件，固定归属需工程复核。
参考记录与源文件校验值见 kinematics.json。
完整说明：https://github.com/servodevelop/touch-r1-leader-arm/tree/main/hardware/robot-description
''')
print('已生成', ROOT/'touch-r1-urdf.zip')
