# Touch R1 Leader Arm

<sub>**简体中文**</sub>

Touch R1 Leader Arm 硬件资源，以及 Star Arm 102 → Lumos 的 Python 遥操作和 LeRobot 接入资源。

文档以中文为主，英文按需补充。各目录的 `README.md` 为正文入口。

## 资源入口

| 任务 | 入口 | 状态 |
| --- | --- | --- |
| 查看硬件规格与 CAD 资料 | [硬件资源](hardware/) | 已提供 V3.1／V3.2 装配体、18 份 V3.2 STEP 导出件、图文 CAD BOM 及 V3.2 七轴（含双 finger）URDF 预览；采购规格与实机参数待确认 |
| 查阅装配、校准与使用指南 | [文档中心](docs/) | 已有中文遥操作指南；其他指南待补 |
| 安装依赖并运行遥操作 | [Python SDK](python-sdk/) | 已有 Star Arm 102 → Lumos 脚本与指南；Touch R1 Leader Arm V3.1 兼容性尚未验证 |
| 使用 LeRobot 遥操作、采集关节数据与回放 | [LeRobot 完整实操教程](lerobot/README.md) | 提供 Python 3.12 安装入口，按固定版本获取外部适配依赖；Touch R1 Leader Arm V3.1 兼容性尚未验证 |

## 仓库结构

```text
.
├── README.md
├── hardware/
│   ├── bom.json
│   ├── step/
│   │   ├── assembly/
│   │   └── parts/
│   ├── printing/
│   │   ├── stl/
│   │   └── 3mf/
│   ├── drawings/
│   └── robot-description/
├── docs/
│   ├── README.md
│   └── StarArm102_Lumos_Python_Teleoperation_Guide.docx
├── python-sdk/
│   ├── stararm102_lumos_teleop.py
│   └── scripts/
├── lerobot/
│   ├── README.md
│   └── install_ubuntu.sh
└── scripts/
```

## 文档检查

在仓库根目录执行：

```bash
python -m pip install -r scripts/requirements-docs.txt
python scripts/check_docs.py
python scripts/check_readme_sync.py
```

这些检查覆盖本地文件链接、中文 README 入口与旧链接兼容页。CAD 几何和硬件实际运行需要另外验证。
