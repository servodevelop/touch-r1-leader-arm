# 仓库维护脚本

[← 首页](../README.md)　|　<sub>**简体中文**</sub>

## 文档检查

使用 Python 3.10 或更新版本，在仓库根目录执行：

```bash
python -m pip install -r scripts/requirements-docs.txt
python scripts/check_docs.py
python scripts/check_readme_sync.py
```

检查覆盖本地文件／图片链接、中文 README 入口与旧链接兼容页。正文只维护 `README.md`，不要求同步英文。

## 重新生成 CAD BOM 与简图

[硬件 BOM](../hardware/README.md#bill-of-materials) 根据以校验值锁定的 V3.1 装配体提取。`extract_step_bom.py` 需要可导入 FreeCAD、Part、Import 的 Python 环境；`render_bom.py` 在 Blender 内运行。生成资源已使用 FreeCAD 1.1.4 和 Blender 5.2.2 检查。

在 macOS 上，FreeCAD 与 Blender 安装于 `/Applications` 时，在仓库根目录执行：

```bash
PYTHONPATH=/Applications/FreeCAD.app/Contents/Resources/lib \
  /Applications/FreeCAD.app/Contents/Resources/bin/python \
  scripts/extract_step_bom.py --mesh-dir /tmp/touch-r1-bom-meshes

/Applications/Blender.app/Contents/MacOS/Blender \
  --background --factory-startup --python scripts/render_bom.py -- \
  --mesh-dir /tmp/touch-r1-bom-meshes
```

第一条命令重新生成 16 份 `step/parts/` 导出件及 `bom.json`；第二条生成 17 张图片（16 项 BOM 及装配体）。临时三角网格保存在仓库外，不改写装配体源文件。重复的源 PRODUCT 引用按实例计数；舵机内部零件保留在子装配内。外形相似但源 PRODUCT 标识不同的组件不会自动合并。

导出件会重新导入，检查形体有效性、实体数，以及包围尺寸差小于 0.001 mm、体积差不超过 0.001 mm³ 与 0.01% 中的较大值。源 CAD 公差和实测误差保留在 `bom.json`。这些数值检查阈值不是制造公差。独立导出时移除组件在总装中的位置变换，保留子装配内部的位置变换。

装配体变更后，先复核源编号与 BOM 范围，再更新锁定的 SHA-256 和项目映射。STEP 引用解析器仅针对这份 Creo 导出文件。脚本不改写 README 表格：重新生成数据后需更新中文表格，逐张检查图片并运行文档检查。

## 螺钉规格维护

`fastener_specs.py` 记录了 4 个紧固件源模型的品名与规格；脚本仍按圆柱面半径与轴向边界测量，测量值写入 `dimensions_mm` 供核对，不作为采购规格来源。源尺寸变化时检查会中止，需复核后更新。提取程序把结果写入 `bom.json` 的 `fastener_specification`。

`bom.json` 第 2 版保留英文机器字段名，展示名称使用 `name_zh`，不再生成 `name_en`。品名与规格按实物确认（2026-10-20）：`PRT0001`、`PRT0002`、`GB_T70_1-M3X400` 是同一件 304 薄头内六角平尾自攻螺丝 HB3 × 5，`M3X3X60001` 是 304 塞打螺丝 Ø2.5 × M2 × 3。`bom.json` 仍按源 PRODUCT 保留 4 行，README 采购表内合并为 2 行，品名与型号直接按标准件给定。

中文正文更新后，运行 `python scripts/check_readme_sync.py --write-redirects` 更新旧 `README.zh.md` 兼容页，再运行文档检查。兼容页保留已发布的显式章节锚点，正文只维护一份。

## URDF 与交互预览

`import_urdf_source.py` 从指定 V3.2 STEP 导入 [FCStd 快照](../hardware/robot-description/source/r1-hd-urdf-only.FCStd)，排除 A000、B000 并保存源校验记录；原 STEP 留在本地。`generate_urdf.py` 读取快照及两款舵机 STEP，生成七轴与双 finger URDF。113 个保留源实体全部唯一归属；J7 驱动右 finger，左 finger 通过 URDF `mimic` 反向联动。机壳归上游、舵盘归下游；轴线由 CAD 圆柱面交叉核对。`check_urdf.py` 检查实体覆盖、连接树、联动关系、轴向、米制尺寸及资源校验；`package_urdf.py` 打包资源。

生成方法和未确认参数见 [机器人描述](../hardware/robot-description/README.md)。文档更新后照常运行文档检查；网格和 URDF 更新后必须运行 `python scripts/check_urdf.py`，再执行 `python scripts/package_urdf.py`。

修改预览的 `preview/viewer.js` 后，从仓库根目录重新构建离线模块：

```bash
npm install --prefix /tmp/touch-r1-viewer --ignore-scripts --no-audit --no-fund three@0.180.0 esbuild@0.25.10
NODE_PATH=/tmp/touch-r1-viewer/node_modules \
  /tmp/touch-r1-viewer/node_modules/.bin/esbuild \
  hardware/robot-description/preview/viewer.js --bundle --minify --format=esm \
  --outfile=hardware/robot-description/preview/app.js
python scripts/package_urdf.py
```

预览直接读取交付的 URDF 与 STL，不额外维护一套独立运动学模型。第三方 Three.js 许可随资源包保留。


从实际交付的 URDF / STL 渲染预览图：

```bash
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python scripts/render_urdf_preview.py
/Applications/Blender.app/Contents/MacOS/Blender --background --factory-startup \
  --python scripts/render_urdf_preview.py -- --j7 25 --closeup --output finger-open.png
```

`preview/joint-motion.mjs` 根据 URDF 的 `mimic` 关系计算从动角度。修改预览源码或该模块后须重新构建离线模块。
