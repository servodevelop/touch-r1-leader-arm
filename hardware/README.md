# Touch R1 Leader Arm 硬件

[← 首页](../README.md)　|　<sub>**简体中文**</sub>

提供 V3.1／V3.2 装配体 CAD 资源；物料清单、独立零件导出件与七轴 URDF 均基于 V3.2，V3.1 装配体保留为历史版本。

**目录：**

- [⚙️ 产品规格](#specifications)
- [📂 资源目录](#resources)
- [📐 装配模型](#assembly-model)
- [📋 物料清单](#bill-of-materials)
- [🔎 待确认事项](#confirmation)
- [🛠️ 装配与校准](#assembly-and-calibration)
- [✅ 验证状态](#validation-status)

<a id="specifications"></a>

## 产品规格

| 规格 | Touch R1 Leader Arm |
| --- | --- |
| 硬件版本 | V3.2，依据所提供装配体的文件名标注；V3.1 装配体保留为历史版本 |
| 产品类型 | 遥操作主臂 |
| 自由度 | 待确认 |
| 臂展与重量 | 待确认 |
| 电源与通信 | 待确认 |
| 执行器与编码器 | 待确认 |
| 关节运动范围 | 待确认 |

<a id="resources"></a>

## 资源目录

| 目录／文件 | 内容 | 状态 |
| --- | --- | --- |
| [step/assembly/](step/assembly/) | 原始 V3.1／V3.2 装配体 STEP | 源文件字节保持不变；已检查 CAD 导入（V3.2 为当前依据） |
| [step/components/](step/components/) | 用户提供的 RP8-U45H-M / C028 舵机 STEP | 用于 URDF 视觉模型，保留原文件内容 |
| [step/parts/](step/parts/) | 18 份独立零件或子装配 STEP | 已通过导出与重新导入检查 |
| [bom.json](bom.json) | BOM 数量、源编号、实例位置及几何检查结果 | 根据源装配树提取 |
| [printing/stl/](printing/stl/) | 可打印的零件网格 | 待补充 |
| [printing/3mf/](printing/3mf/) | 独立零件与整套打印项目 | 待补充 |
| [drawings/](drawings/) | 带尺寸工程图纸，PDF／DWG | 待补充 |
| [robot-description/](robot-description/) | V3.2 七轴 URDF、网格和交互预览 | 包含 J7 舵机与双 finger，排除两个限位块；实机参数待确认 |

<a id="assembly-model"></a>

## 装配模型

- [下载 V3.2 装配体 STEP](step/assembly/touch-r1-leader-arm-v3.2-1013.stp)：**当前 BOM、独立零件导出件与七轴 URDF 的依据**，包含 J7 舵机和左右手指。
- [下载 V3.1 装配体 STEP](step/assembly/touch-leader-arm-v3.1-1013.stp)：历史版本，保留供对照；其 BOM 与导出件已被 V3.2 取代。

V3.2 原文件 `遥操臂V3.2_1013(1).stp` 仅规范保存名称，文件内容保持不变，共 115 个实体，包含 A000、B000。URDF 专用快照另外排除这两个限位块；[来源记录](robot-description/source/assembly-source.json) 保存原文件 SHA-256。

<a href="images/touch-r1-assembly.png"><img src="images/touch-r1-assembly.png" alt="Touch R1 V3.1 CAD 装配体" width="320"></a>

所提供的文件 `遥操臂V3.1_1013.stp` 以 `touch-leader-arm-v3.1-1013.stp` 保存，内容未作修改。STEP 文件头记录的导出软件为 Creo Parametric，导出时间为 `2026-10-13T11:21:50`。版本标注来自源文件名。

独立 STEP 保留各组件自身的 CAD 坐标系；舵机导出件保留内部几何，作为完整子装配提供。这些文件为参考 CAD 导出件，尚未指定制造或打印工艺。

<a id="bill-of-materials"></a>

## 物料清单

下表列出一套装配体的完整物料，共 **28 项**：结构件与舵机 13 项（装配体中 18 个顶层实例），标准件与配件 15 项。装配体另有 5 个紧固件实例并入第 14、15 行，1 个经确认不存在的「垫片」实体未列入，合计 24 个顶层实例。

结构件与舵机的数量来自 STEP 装配引用，逐项记录在 `bom.json`；标准件与配件为采购件，规格按 102 同款件与实物确认记录，数量按 R1 装配需求给定。装配体中的 5 个紧固件实例（自攻螺丝 3 件、塞打螺丝 2 件）已按采购规格并入本表，不再单列。

装配体中另有一个源名称为「垫片」（`_X2_57AB7247_X0_`）的实体，经确认不是实际使用的零件，**未列入本表**；其 CAD 记录仍保留在 `bom.json`。

表内品名与描述沿用 Star Arm 102 的英文写法（`No. | Part Name | Model / Specification | Image | Description | Quantity`），不再逐条译成中文。结构件的图片由源 STEP 几何渲染为 1024 × 1024 白底图；舵机为产品外观图，标准件与配件为产品外观图或示意图。所有图片只用于识别类型，不代表实物材质、颜色或表面处理，各图独立缩放。表内 CAD 包围尺寸为零件本地坐标轴的包围盒尺寸，四舍五入到 0.01 mm，不是工程尺寸、公差或采购规格。

| No. | Part Name | Model / Specification | Image | Description | Quantity |
| :---: | --- | --- | :---: | --- | :---: |
| 1 | UART bus servo | [RP8-U45H-M-C028](step/parts/touch-r1-servo-rp8-u45h-m-c028.step) | <a href="images/parts/rp8-u45h-m-c028.webp"><img src="images/parts/rp8-u45h-m-c028.webp" alt="UART bus servo" width="90"></a> | 12V; 45kg-cm; 118rpm; Dual-shaft Housing (Flat Bottom Cover, No Rear Output Shaft); Coreless Motor; 12-bit Magnetic Absolute Encoder; 25T | 4 |
| 2 | UART bus servo | [RP8-U45H-M](step/parts/touch-r1-servo-25-50kg-0001.step) | <a href="images/parts/rp8-u45h-m.webp"><img src="images/parts/rp8-u45h-m.webp" alt="UART bus servo" width="90"></a> | 12V; 45kg-cm; 118rpm; Dual-shaft; Coreless Motor; 12-bit Magnetic Absolute Encoder; 25T | 3 |
| 3 | Link 1 | [touch-r1-joint-1](step/parts/touch-r1-joint-1.step) | <a href="images/touch-r1-joint-1.png"><img src="images/touch-r1-joint-1.png" alt="Joint 1 structure" width="90"></a> | Source name: `_X2_51738282_X0_1_NEW`<br>CAD bounding box: 120.03 × 56.00 × 120.02 mm.<br>Material and manufacturing process TBD. | 1 |
| 4 | Link 2 | [touch-r1-joint-2](step/parts/touch-r1-joint-2.step) | <a href="images/touch-r1-joint-2.png"><img src="images/touch-r1-joint-2.png" alt="Joint 2 structure" width="90"></a> | Source name: `_X2_51738282_X0_2__X2_65B0_X0_`<br>CAD bounding box: 69.27 × 27.42 × 46.15 mm.<br>Material and manufacturing process TBD. | 1 |
| 5 | Link 3 | [touch-r1-joint-3](step/parts/touch-r1-joint-3.step) | <a href="images/touch-r1-joint-3.png"><img src="images/touch-r1-joint-3.png" alt="Joint 3 structure" width="90"></a> | Source name: `_X2_51738282_X0_3`<br>CAD bounding box: 170.96 × 30.31 × 61.65 mm.<br>Material and manufacturing process TBD. | 1 |
| 6 | Link 4 | [touch-r1-joint-4](step/parts/touch-r1-joint-4.step) | <a href="images/touch-r1-joint-4.png"><img src="images/touch-r1-joint-4.png" alt="Joint 4 structure" width="90"></a> | Source name: `_X2_51738282_X0_4`<br>CAD bounding box: 167.35 × 70.38 × 63.65 mm.<br>Material and manufacturing process TBD. | 1 |
| 7 | Link 5 | [touch-r1-joint-5](step/parts/touch-r1-joint-5.step) | <a href="images/touch-r1-joint-5.png"><img src="images/touch-r1-joint-5.png" alt="Joint 5 structure" width="90"></a> | Source name: `_X2_51738282_X0_5_NEW`<br>CAD bounding box: 69.52 × 53.85 × 83.00 mm.<br>Material and manufacturing process TBD. | 1 |
| 8 | Link 6 | [touch-r1-joint-6](step/parts/touch-r1-joint-6.step) | <a href="images/touch-r1-joint-6.png"><img src="images/touch-r1-joint-6.png" alt="Joint 6 structure" width="90"></a> | Source name: `_X2_51738282_X0_6_NEW`<br>CAD bounding box: 46.20 × 25.75 × 51.70 mm.<br>Material and manufacturing process TBD. | 1 |
| 9 | Handle assembly | [touch-r1-handle-assembly](step/parts/touch-r1-handle-assembly.step) | <a href="images/touch-r1-handle-assembly.png"><img src="images/touch-r1-handle-assembly.png" alt="Handle assembly" width="90"></a> | Source name: `SHOUBING_ASM`<br>CAD bounding box: 50.40 × 138.32 × 65.07 mm.<br>Handle sub-assembly with internal CAD parts. | 1 |
| 10 | Left finger | [touch-r1-finger-left](step/parts/touch-r1-finger-left.step) | <a href="images/touch-r1-finger-left.png"><img src="images/touch-r1-finger-left.png" alt="Left finger" width="90"></a> | Source name: `LEFT_ZHUA`<br>CAD bounding box: 92.13 × 42.99 × 26.55 mm.<br>Driven in reverse from the right finger via URDF `mimic`. | 1 |
| 11 | Right finger | [touch-r1-finger-right](step/parts/touch-r1-finger-right.step) | <a href="images/touch-r1-finger-right.png"><img src="images/touch-r1-finger-right.png" alt="Right finger" width="90"></a> | Source name: `RIGHT_ZHUA`<br>CAD bounding box: 92.62 × 40.27 × 24.74 mm.<br>Driven directly by the J7 servo. | 1 |
| 12 | Bracket A000 (purpose TBD) | [touch-r1-part-a000](step/parts/touch-r1-part-a000.step) | <a href="images/touch-r1-part-a000.png"><img src="images/touch-r1-part-a000.png" alt="Bracket A000 (purpose TBD)" width="90"></a> | Source name: `A000`<br>CAD bounding box: 41.12 × 41.76 × 8.00 mm.<br>Source ID retained; purpose, material and process TBD. | 1 |
| 13 | Bracket B000 (purpose TBD) | [touch-r1-part-b000](step/parts/touch-r1-part-b000.step) | <a href="images/touch-r1-part-b000.png"><img src="images/touch-r1-part-b000.png" alt="Bracket B000 (purpose TBD)" width="90"></a> | Source name: `B000`<br>CAD bounding box: 10.00 × 22.11 × 13.51 mm.<br>Source ID retained; purpose, material and process TBD. | 1 |
| 14 | 304 thin-head hex-socket blunt-tip self-tapping screw | HB3 × 5 | <a href="images/touch-r1-fastener-prt0001.png"><img src="images/touch-r1-fastener-prt0001.png" alt="304 thin-head hex-socket blunt-tip self-tapping screw" width="90"></a> | 304 stainless steel; nominal thread Ø3, length 5 mm; thin-head hex socket, blunt tip. | 3 |
| 15 | 304 shoulder screw | Ø2.5 × M2 × 3 | <a href="images/touch-r1-fastener-m3x3x60001.png"><img src="images/touch-r1-fastener-m3x3x60001.png" alt="304 shoulder screw" width="90"></a> | 304 stainless steel; shoulder Ø2.5 × 3 mm, thread M2. | 2 |
| 16 | Socket-head cap screw | M2 × 8 | <a href="images/fasteners/m2-8-socket-head-cap-screw.png"><img src="images/fasteners/m2-8-socket-head-cap-screw.png" alt="Socket-head cap screw" width="90"></a> | Black finish | 16 |
| 17 | Phillips pan-head self-tapping screw | PB2.0 × 5 | <a href="images/fasteners/pb2-5-phillips-pan-head-self-tapping-screw.png"><img src="images/fasteners/pb2-5-phillips-pan-head-self-tapping-screw.png" alt="Phillips pan-head self-tapping screw" width="90"></a> | Black finish, hardened | 28 |
| 18 | Phillips pan-head screw | M2 × 4.5 | <a href="images/fasteners/m2-4-5-phillips-pan-head-screw.png"><img src="images/fasteners/m2-4-5-phillips-pan-head-screw.png" alt="Phillips pan-head screw" width="90"></a> | Black finish; blue pre-applied threadlocker on approximately the lower two-thirds of the threaded shank (toward the tip) | 52 |
| 19 | Phillips pan-head screw | M3 × 10 | <a href="images/fasteners/m3-10-phillips-pan-head-screw.png"><img src="images/fasteners/m3-10-phillips-pan-head-screw.png" alt="Phillips pan-head screw" width="90"></a> | Black finish, hardened | 1 |
| 20 | Nut | M3 | <a href="images/fasteners/m3-nut.png"><img src="images/fasteners/m3-nut.png" alt="Nut" width="90"></a> | Black finish | 1 |
| 21 | Washer | M3 (3 × 6 × 0.5 mm) | <a href="images/fasteners/m3-6-0-5-stainless-washer.png"><img src="images/fasteners/m3-6-0-5-stainless-washer.png" alt="Washer" width="90"></a> | Stainless steel | 1 |
| 22 | HD button cover | hd-button-cover | <a href="images/parts/hd-button-cover.png"><img src="images/parts/hd-button-cover.png" alt="HD button cover" width="90"></a> | Ivory, PLA 3D printed part | 1 |
| 23 | HD button base | hd-button-base | <a href="images/parts/hd-button-base.png"><img src="images/parts/hd-button-base.png" alt="HD button base" width="90"></a> | Ivory, PLA 3D printed part | 1 |
| 24 | TTL/USB Servo Adapter | UC-01 | <a href="images/parts/uc-01.webp"><img src="images/parts/uc-01.webp" alt="TTL/USB Servo Adapter" width="90"></a> | USB Type-C; half-/full-duplex conversion; selectable 3.3 V / 5 V TTL levels; 6–15 V input; 2 × PH2.0 servo ports; reverse-polarity protection; XT30 connector | 1 |
| 25 | Button board | UK-01 | <a href="images/parts/uk-01-board.webp"><img src="images/parts/uk-01-board.webp" alt="Button board" width="90"></a> | With socket | 1 |
| 26 | Thrust needle roller bearing | AXK2035+2AS | <a href="images/parts/axk2035-2as-bearing.png"><img src="images/parts/axk2035-2as-bearing.png" alt="Thrust needle roller bearing" width="90"></a> | Inner diameter 20 mm, outer diameter 35 mm, thickness 4 mm | 1 |
| 27 | Servo cable | PH2.0 (PH-3Y)<br>120 mm | <a href="images/parts/ph3y-servo-cable-120mm.png"><img src="images/parts/ph3y-servo-cable-120mm.png" alt="Servo cable" width="90"></a> | Black silicone-insulated ribbon cable with black braided sleeving; reversed pin order between ends; 60 × Ø0.08 mm strands per conductor (approx. 22 AWG) | 3 |
| 28 | Servo cable | PH2.0 (PH-3Y)<br>200 mm | <a href="images/parts/ph3y-servo-cable-200mm.png"><img src="images/parts/ph3y-servo-cable-200mm.png" alt="Servo cable" width="90"></a> | Black silicone-insulated ribbon cable with black braided sleeving; reversed pin order between ends; 60 × Ø0.08 mm strands per conductor (approx. 22 AWG) | 5 |

<a id="confirmation"></a>

## 待确认事项

- 源名称为 `_25-50KG-0001_ASM_ASM` 的子装配（3 件）按实物确认为 **RP8-U45H-M**；源名称未体现型号，交付配置（舵盘、线材、固件）仍需核对。`RP8-U45H-M-C028`（4 件）同样需核对实际配置。
- 第 14 行 `HB3 × 5`（3 件）与第 15 行 `Ø2.5 × M2 × 3`（2 件）的品名、规格与材质按实物确认（2026-10-20）；螺纹精度、表面处理、用量与安装位置需按实物与采购渠道复核。
- 源名称为「垫片」的实体（`_X2_57AB7247_X0_`，CAD 包围 20.00 × 2.30 × 20.00 mm）经确认不是实际使用的零件，已从物料清单剔除；`bom.json` 仍保留其 CAD 记录，`step/parts/touch-r1-spacer.step` 保留供核对。
- 确认 A000、B000 的用途，以及全部结构件的材质、制造工艺和公差。不预设 PLA、打印参数或加工方式。
- 确认实物所需的完整紧固件、线缆、控制板、电源及配件。源装配树中只有 5 个顶层紧固件实例，不代表用 5 个紧固件就能完成装配。源名称中的关节 1–6 也不能据此认定机械臂的驱动自由度。
- V3.2 相对 V3.1 的变化（按装配体实测）：关节 7 由「手柄装配」取代，新增左右手指，RP8 舵机子装配由 3 个增至 4 个（多出的是 J7 手指驱动舵机），原台阶螺钉的源名称改为 M2X4X30001（几何 69.45 mm³ 不变）；其余 13 种结构件与舵机几何未变。请确认这些变化是设计意图。
- 手指联动关系取自 URDF（右手指直驱、左手指通过 mimic 反向联动），机械限位、零位与夹持力需按实物确认。
- 第 16–21 行的紧固件规格、表面处理与强度等级沿用 102 同款件写法；第 22–28 行的按钮盖／按钮座、UC-01、UK-01、推力滚针轴承与舵机连接线按 102 同型件记录。以上供应商、材质与实配数量均需按 R1 实物与采购渠道复核。

<a id="assembly-and-calibration"></a>

## 装配与校准

装配顺序、经确认的紧固件规格、接线、关节限位及零位校准说明待补充。

现有 [Python 遥操作指南](../python-sdk/README.md) 面向 Star Arm 102 → Lumos；与此 V3.1 装配体的兼容性尚未验证。

<a id="validation-status"></a>

## 验证状态

| 项目 | 状态 |
| --- | --- |
| V3.1 源装配体 | SHA-256 与附件一致；1 个根装配、21 个顶层实例 |
| V3.2 源装配体 | SHA-256 与附件一致（2654e3b…）；24 个顶层实例、115 个实体；BOM、导出件与七轴 URDF 的依据 |
| V3.1 CAD 导入（历史） | 99 个实体；通过 FreeCAD 形体有效性检查 |
| 18 份 STEP 导出件 | 已成功重新导入；实体数不变，最大相对体积差低于 0.0011%，包围尺寸差低于 0.001 mm |
| BOM 数量 | 已交叉核对 STEP 引用与导入对象；源映射保留于 bom.json |
| 标准件与配件 | 第 14、15 行品名、规格与材质按实物确认（2026-10-20）；第 16–28 行规格沿用 102 同型件，数量按 R1 装配需求给定，待采购复核 |
| 零件简图 | 根据 CAD 网格渲染；使用中性显示材质；各图独立缩放 |
| 干涉、配合与实物装配 | 尚未验证 |
| 采购 BOM 完整性与硬件规格 | 待工程确认 |
| URDF 与交互预览 | 已提供 9 连杆、7 控制关节及 1 从动关节的运动学草案；[查看预览说明](robot-description/) |
| 可打印性与动力学仿真 | 尚未验证；未提供打印文件、碰撞模型与惯量参数 |
| V3.1 的 Python 遥操作 | 尚未验证 |

几何检查用于验证 CAD 导入导出一致性，不代表通过制造验收。重新生成导出件和简图的方法见 [生成说明](../scripts/README.md)。
