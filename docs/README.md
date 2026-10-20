# Touch R1 Leader Arm 文档中心

[← 首页](../README.md)　|　<sub>**简体中文**</sub>

这里是整个仓库的文档入口，涵盖装配、校准及使用指南。Python 代码和依赖安装脚本位于 [python-sdk/](../python-sdk/)；CAD、打印文件和图纸位于 [hardware/](../hardware/)。

## 使用指南

| 任务 | 指南 | 适用范围与状态 |
| --- | --- | --- |
| 安装、校准并运行 Python 遥操作 | [操作指南（中文 Word）](StarArm102_Lumos_Python_Teleoperation_Guide.docx) · [Python SDK 说明](../python-sdk/README.md) | 已有 Star Arm 102 → Lumos 流程；Touch R1 Leader Arm V3.1 兼容性尚未验证 |
| 安装 LeRobot、遥操作、采集与回放 | [LeRobot 完整实操教程（Markdown）](../lerobot/README.md) | Python 3.12，StarArm102 → Lumos，无摄像头关节数据流程；Touch R1 Leader Arm V3.1 兼容性尚未验证 |
| 装配 Touch R1 Leader Arm | 待补充 | 装配顺序、紧固件与接线说明待编写 |
| 校准 Touch R1 Leader Arm 硬件 | 待补充 | 机械参考姿态、关节限位及零位校准待确认 |

Word 指南虽然存放在此目录，其 Python 命令仍需在 `python-sdk/` 中执行。后续跨硬件与软件的指南统一在此目录按任务组织。
