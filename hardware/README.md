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

结构件的图片由源 STEP 几何渲染为 1024 × 1024 白底图；舵机为产品外观图，标准件与配件为产品外观图或示意图。所有图片只用于识别类型，不代表实物材质、颜色或表面处理，各图独立缩放。表内 CAD 包围尺寸为零件本地坐标轴的包围盒尺寸，四舍五入到 0.01 mm，不是工程尺寸、公差或采购规格。

| 序号 | 品名 | 型号／规格 | 图片 | 描述 | 数量 |
| :---: | --- | --- | :---: | --- | :---: |
| 1 | 舵机 | [RP8-U45H-M-C028](step/parts/touch-r1-servo-rp8-u45h-m-c028.step) | <a href="images/parts/rp8-u45h-m-c028.webp"><img src="images/parts/rp8-u45h-m-c028.webp" alt="舵机 简图" width="90"></a> | 12 V；45 kg·cm；118 rpm；双轴；空心杯电机；12 位磁性绝对值编码器；25T。含舵盘与内部 CAD 零件。 | 4 |
| 2 | 舵机 | [RP8-U45H-M](step/parts/touch-r1-servo-25-50kg-0001.step) | <a href="images/parts/rp8-u45h-m.webp"><img src="images/parts/rp8-u45h-m.webp" alt="舵机 简图" width="90"></a> | 12 V；45 kg·cm；118 rpm；双轴款壳体（平面下盖，无后输出轴）；空心杯电机；12 位磁性绝对值编码器；25T。含舵盘与内部 CAD 零件。 | 3 |
| 3 | 关节 1 结构件 | [touch-r1-joint-1](step/parts/touch-r1-joint-1.step) | <a href="images/touch-r1-joint-1.png"><img src="images/touch-r1-joint-1.png" alt="关节 1 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_1_NEW`<br>CAD 包围尺寸：120.03 × 56.00 × 120.02 mm。<br>材质与制造工艺待确认。 | 1 |
| 4 | 关节 2 结构件 | [touch-r1-joint-2](step/parts/touch-r1-joint-2.step) | <a href="images/touch-r1-joint-2.png"><img src="images/touch-r1-joint-2.png" alt="关节 2 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_2__X2_65B0_X0_`<br>CAD 包围尺寸：69.27 × 27.42 × 46.15 mm。<br>材质与制造工艺待确认。 | 1 |
| 5 | 关节 3 结构件 | [touch-r1-joint-3](step/parts/touch-r1-joint-3.step) | <a href="images/touch-r1-joint-3.png"><img src="images/touch-r1-joint-3.png" alt="关节 3 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_3`<br>CAD 包围尺寸：170.96 × 30.31 × 61.65 mm。<br>材质与制造工艺待确认。 | 1 |
| 6 | 关节 4 结构件 | [touch-r1-joint-4](step/parts/touch-r1-joint-4.step) | <a href="images/touch-r1-joint-4.png"><img src="images/touch-r1-joint-4.png" alt="关节 4 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_4`<br>CAD 包围尺寸：167.35 × 70.38 × 63.65 mm。<br>材质与制造工艺待确认。 | 1 |
| 7 | 关节 5 结构件 | [touch-r1-joint-5](step/parts/touch-r1-joint-5.step) | <a href="images/touch-r1-joint-5.png"><img src="images/touch-r1-joint-5.png" alt="关节 5 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_5_NEW`<br>CAD 包围尺寸：69.52 × 53.85 × 83.00 mm。<br>材质与制造工艺待确认。 | 1 |
| 8 | 关节 6 结构件 | [touch-r1-joint-6](step/parts/touch-r1-joint-6.step) | <a href="images/touch-r1-joint-6.png"><img src="images/touch-r1-joint-6.png" alt="关节 6 结构件 简图" width="90"></a> | 源名称：`_X2_51738282_X0_6_NEW`<br>CAD 包围尺寸：46.20 × 25.75 × 51.70 mm。<br>材质与制造工艺待确认。 | 1 |
| 9 | 手柄装配 | [touch-r1-handle-assembly](step/parts/touch-r1-handle-assembly.step) | <a href="images/touch-r1-handle-assembly.png"><img src="images/touch-r1-handle-assembly.png" alt="手柄装配 简图" width="90"></a> | 源名称：`SHOUBING_ASM`<br>CAD 包围尺寸：50.40 × 138.32 × 65.07 mm。<br>手柄部装配；含内部 CAD 零件，材质与制造工艺待确认。 | 1 |
| 10 | 左手指 | [touch-r1-finger-left](step/parts/touch-r1-finger-left.step) | <a href="images/touch-r1-finger-left.png"><img src="images/touch-r1-finger-left.png" alt="左手指 简图" width="90"></a> | 源名称：`LEFT_ZHUA`<br>CAD 包围尺寸：92.13 × 42.99 × 26.55 mm。<br>左手指；由右手指经 `mimic` 反向联动。材质与制造工艺待确认。 | 1 |
| 11 | 右手指 | [touch-r1-finger-right](step/parts/touch-r1-finger-right.step) | <a href="images/touch-r1-finger-right.png"><img src="images/touch-r1-finger-right.png" alt="右手指 简图" width="90"></a> | 源名称：`RIGHT_ZHUA`<br>CAD 包围尺寸：92.62 × 40.27 × 24.74 mm。<br>右手指；由 J7 舵机直接驱动。材质与制造工艺待确认。 | 1 |
| 12 | 支架 A000（用途待确认） | [touch-r1-part-a000](step/parts/touch-r1-part-a000.step) | <a href="images/touch-r1-part-a000.png"><img src="images/touch-r1-part-a000.png" alt="支架 A000（用途待确认） 简图" width="90"></a> | 源名称：`A000`<br>CAD 包围尺寸：41.12 × 41.76 × 8.00 mm。<br>保留源编号；用途、材质及工艺待确认。 | 1 |
| 13 | 支架 B000（用途待确认） | [touch-r1-part-b000](step/parts/touch-r1-part-b000.step) | <a href="images/touch-r1-part-b000.png"><img src="images/touch-r1-part-b000.png" alt="支架 B000（用途待确认） 简图" width="90"></a> | 源名称：`B000`<br>CAD 包围尺寸：10.00 × 22.11 × 13.51 mm。<br>保留源编号；用途、材质及工艺待确认。 | 1 |
| 14 | 304 薄头内六角平尾自攻螺丝 | HB3 × 5 | <a href="images/touch-r1-fastener-prt0001.png"><img src="images/touch-r1-fastener-prt0001.png" alt="304 薄头内六角平尾自攻螺丝 简图" width="90"></a> | 304 不锈钢；螺纹公称 Ø3，长度 5 mm；薄头内六角，平尾（钝头）自攻。 | 3 |
| 15 | 304 塞打螺丝（轴肩螺钉） | Ø2.5 × M2 × 3 | <a href="images/touch-r1-fastener-m3x3x60001.png"><img src="images/touch-r1-fastener-m3x3x60001.png" alt="304 塞打螺丝（轴肩螺钉） 简图" width="90"></a> | 304 不锈钢；轴肩 Ø2.5 × 3 mm，螺纹 M2。 | 2 |
| 16 | 内六角圆柱头螺钉 | M2 × 8 | <a href="images/fasteners/m2-8-socket-head-cap-screw.png"><img src="images/fasteners/m2-8-socket-head-cap-screw.png" alt="内六角圆柱头螺钉 简图" width="90"></a> | 黑色表面 | 16 |
| 17 | 十字槽盘头自攻螺钉 | PB2.0 × 5 | <a href="images/fasteners/pb2-5-phillips-pan-head-self-tapping-screw.png"><img src="images/fasteners/pb2-5-phillips-pan-head-self-tapping-screw.png" alt="十字槽盘头自攻螺钉 简图" width="90"></a> | 黑色表面，加硬 | 28 |
| 18 | 十字槽盘头螺钉 | M2 × 4.5 | <a href="images/fasteners/m2-4-5-phillips-pan-head-screw.png"><img src="images/fasteners/m2-4-5-phillips-pan-head-screw.png" alt="十字槽盘头螺钉 简图" width="90"></a> | 黑色表面；靠近末端的约 2/3 螺纹段预涂蓝色锁固胶 | 52 |
| 19 | 十字槽盘头螺钉 | M3 × 10 | <a href="images/fasteners/m3-10-phillips-pan-head-screw.png"><img src="images/fasteners/m3-10-phillips-pan-head-screw.png" alt="十字槽盘头螺钉 简图" width="90"></a> | 黑色表面，加硬 | 1 |
| 20 | 螺母 | M3 | <a href="images/fasteners/m3-nut.png"><img src="images/fasteners/m3-nut.png" alt="螺母 简图" width="90"></a> | 黑色表面 | 1 |
| 21 | 平垫圈 | M3（3 × 6 × 0.5 mm） | <a href="images/fasteners/m3-6-0-5-stainless-washer.png"><img src="images/fasteners/m3-6-0-5-stainless-washer.png" alt="平垫圈 简图" width="90"></a> | 不锈钢 | 1 |
| 22 | HD 按钮盖 | hd-button-cover | <a href="images/parts/hd-button-cover.png"><img src="images/parts/hd-button-cover.png" alt="HD 按钮盖 简图" width="90"></a> | 米白色 PLA 打印件 | 1 |
| 23 | HD 按钮座 | hd-button-base | <a href="images/parts/hd-button-base.png"><img src="images/parts/hd-button-base.png" alt="HD 按钮座 简图" width="90"></a> | 米白色 PLA 打印件 | 1 |
| 24 | TTL/USB 舵机转接板 | UC-01 | <a href="images/parts/uc-01.webp"><img src="images/parts/uc-01.webp" alt="TTL/USB 舵机转接板 简图" width="90"></a> | USB Type-C；半双工／全双工转换；3.3 V／5 V TTL 电平可切换；输入 6–15 V；2 个 PH2.0 舵机接口；反接保护；XT30 接口 | 1 |
| 25 | 按钮板 | UK-01 | <a href="images/parts/uk-01-board.webp"><img src="images/parts/uk-01-board.webp" alt="按钮板 简图" width="90"></a> | 带插座 | 1 |
| 26 | 推力滚针轴承 | AXK2035+2AS | <a href="images/parts/axk2035-2as-bearing.png"><img src="images/parts/axk2035-2as-bearing.png" alt="推力滚针轴承 简图" width="90"></a> | 内径 20 mm，外径 35 mm，厚度 4 mm | 1 |
| 27 | 舵机连接线 | PH2.0（PH-3Y）120 mm | <a href="images/parts/ph3y-servo-cable-120mm.png"><img src="images/parts/ph3y-servo-cable-120mm.png" alt="舵机连接线 简图" width="90"></a> | 黑色硅胶绝缘排线，外覆黑色编织护套；两端线序反向；每根导体 60 × Ø0.08 mm（约 22 AWG） | 3 |
| 28 | 舵机连接线 | PH2.0（PH-3Y）200 mm | <a href="images/parts/ph3y-servo-cable-200mm.png"><img src="images/parts/ph3y-servo-cable-200mm.png" alt="舵机连接线 简图" width="90"></a> | 黑色硅胶绝缘排线，外覆黑色编织护套；两端线序反向；每根导体 60 × Ø0.08 mm（约 22 AWG） | 5 |

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
