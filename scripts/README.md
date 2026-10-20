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

`fastener_specs.py` 按圆柱面半径与轴向边界核查 4 种紧固件，区分头下长度、头高、台阶段与末段；提取程序将结果写入 `bom.json` 的 `fastener_specification`。源尺寸变化时检查会中止，需复核后更新规格。

`bom.json` 第 2 版保留英文机器字段名，展示名称使用 `name_zh`，不再生成 `name_en`。规格中的 M3 × 4 是 CAD 推定，不能作为已确认的采购螺纹。材质、强度等级和表面处理须另有依据。

中文正文更新后，运行 `python scripts/check_readme_sync.py --write-redirects` 更新旧 `README.zh.md` 兼容页，再运行文档检查。兼容页保留已发布的显式章节锚点，正文只维护一份。

## URDF 与交互预览

`generate_urdf.py` 从去除限位块的 [FCStd 装配体](../hardware/robot-description/source/r1-hd-urdf-only.FCStd) 和用户提供的两个舵机 STEP 生成 URDF 与米制 STL。只提取装配树的实体叶节点，排除父装配缓存和基准几何；按对象标识检查 97 个源实体全部唯一归属，A000、B000 不从旧 BOM 回填。源文件 SHA-256 已锁定，修改装配后需复核并更新脚本映射。舵机机壳归上游连杆，舵盘归下游连杆；六轴与结构件同轴圆柱面交叉核对。`check_urdf.py` 检查连接树、轴向、零位映射、网格路径、校验值与米制尺寸；`package_urdf.py` 打包可下载的预览资源。

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
