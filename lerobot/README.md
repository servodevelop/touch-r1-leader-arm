# StarArm102 → Lumos：LeRobot 完整实操教程

[← 首页](../README.md)　|　<sub>**简体中文**</sub>

本教程介绍 StarArm102 主臂与 Lumos 从臂的 LeRobot 接入流程，包括环境安装、配对校准、遥操作、关节数据采集和回放。数据包含六关节与可选夹爪，不包含图像或视频。

适用环境为 Ubuntu 22.04 / 24.04 x86_64、Python 3.12。Touch R1 Leader Arm 的实机兼容性尚未验证。

## 目录

- [1. 环境准备](#environment)
- [2. 安装与检查](#installation)
- [3. 接线与通信设置](#connection)
- [4. 配对校准与关节限位](#calibration)
- [5. 预览与遥操作](#teleoperation)
- [6. 关节数据采集](#recording)
- [7. 数据回放](#replay)
- [8. 日常启动](#daily)
- [9. 常见问题](#faq)
- [10. 依赖与验证范围](#dependencies)

<a id="environment"></a>

## 1. 环境准备

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Ubuntu 22.04 / 24.04，x86_64 |
| Python | 3.12，使用独立 Conda 环境 |
| 主臂 | StarArm102，通过 USB/UART 连接 |
| 从臂 | Lumos，通过 CAN 连接，速率 1 Mbps |
| 网络与权限 | 可访问 GitHub、PyPI，具备 `sudo` 权限 |

遥操作与关节数据采集可使用 CPU。此流程使用独立的 Python 3.12 环境，与 [Python SDK 教程](../python-sdk/README.md)中的 Python 3.10 环境分开。

### 1.1 安装基础工具

```bash
sudo apt-get update
sudo apt-get install -y git curl can-utils
```

### 1.2 安装 Conda

已安装 Conda 时跳过本步。以下命令将 Miniforge 安装到 `~/miniforge3`；该目录已存在时，使用现有环境。

```bash
mkdir -p ~/Downloads
cd ~/Downloads
curl -L https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh \
  -o Miniforge3-Linux-x86_64.sh
bash Miniforge3-Linux-x86_64.sh -b -p "$HOME/miniforge3"
source "$HOME/miniforge3/etc/profile.d/conda.sh"
```

安装说明见 [Miniforge 文档](https://github.com/conda-forge/miniforge)。

### 1.3 创建并激活环境

```bash
conda create -n lumos-lerobot python=3.12 -y
conda activate lumos-lerobot
python --version
```

应输出 `Python 3.12.x`。

<a id="installation"></a>

## 2. 安装与检查

### 2.1 克隆本仓库

```bash
cd ~
git clone https://github.com/servodevelop/touch-r1-leader-arm.git
cd ~/touch-r1-leader-arm/lerobot
```

### 2.2 安装 LeRobot、硬件 SDK 和适配器

在已激活的 `lumos-lerobot` 环境中执行：

```bash
bash install_ubuntu.sh
```

安装脚本下载固定版本的硬件适配器、LeRobot 和 Lumos SDK，并安装系统与 Python 依赖。安装过程中不连接机械臂；脚本正常结束后再继续。

依赖文件位于本目录的 `.dependencies/stararm102-lumos-lerobot/`，运行时需要保留。具体来源与版本见[依赖与验证范围](#dependencies)。

### 2.3 检查安装结果

```bash
python -c "import serial, fashionstar_uart_sdk; from startouchclass import SingleArm; print('SDK OK')"
python -c "from lerobot_robot_lumos_stararm102 import LumosConfig, StarArm102Config; print(LumosConfig().type, StarArm102Config().type)"
python -m pip check
```

应看到 `SDK OK`、`lumos stararm102`，且没有依赖冲突。

<a id="connection"></a>

## 3. 接线与通信设置

### 3.1 接线

1. 将 StarArm102 的 USB/UART 接入 Ubuntu 主机。
2. 将 Lumos 通过 CAN 适配器接入同一台主机，检查 CAN 总线接线与终端电阻配置。
3. 连接主从臂电源与急停，清理机械臂活动范围后上电。

**校准与预览也会初始化 Lumos SDK，可能使能电机。** 预览不发送从臂运动目标，HD 按钮仍可控制主臂保持。操作时保持急停可及，同一时间只运行一个控制程序。

### 3.2 找到 StarArm102 串口

```bash
ls -l /dev/ttyUSB* /dev/ttyACM* 2>/dev/null
ls -l /dev/serial/by-id/ 2>/dev/null
```

需要识别端口时，可运行以下工具，并按提示插拔主臂 USB：

```bash
lerobot-find-port
```

后续示例使用 `/dev/ttyUSB0`，请按实际设备修改。Lumos 使用 CAN 接口。

串口报 `Permission denied` 时：

```bash
sudo usermod -aG dialout "$USER"
```

注销并重新登录，使组权限生效，然后重新激活 Conda 环境。后续 LeRobot 命令使用当前用户执行。

### 3.3 设置 Lumos CAN 接口

```bash
ip -details link show can0
```

应看到接口为 `UP`、`bitrate 1000000`。接口存在但尚未启用时：

```bash
sudo ip link set can0 up type can bitrate 1000000
```

接口已启用且速率正确时跳过设置。提示 `Device or resource busy` 时，先检查当前接口状态。

确实要重新设置速率时，先停止控制进程，再运行：

```bash
sudo ip link set can0 down
sudo ip link set can0 up type can bitrate 1000000
```

找不到 `can0` 时，检查适配器驱动和实际接口名。

### 3.4 设置端口与路径

进入仓库的 `lerobot/` 目录，设置后续命令使用的端口与路径：

```bash
cd ~/touch-r1-leader-arm/lerobot

export STARARM_PORT=/dev/ttyUSB0
export LUMOS_CAN=can0
export LEROBOT_CORE_ROOT="$PWD/.dependencies/stararm102-lumos-lerobot"
export LUMOS_SDK_ROOT="$LEROBOT_CORE_ROOT/.dependencies/startouch_sdk"
export LUMOS_MAPPING_FILE="$HOME/.config/stararm102_lumos/calibration.json"
export LUMOS_LIMITS_FILE="$PWD/lumos_joint_limits.json"
```

将 `STARARM_PORT` 和 `LUMOS_CAN` 改为实际接口。以上变量仅在当前终端生效；后续命令均在 `lerobot/` 目录执行。

<a id="calibration"></a>

## 4. 配对校准与关节限位

### 4.1 配对校准主从臂

将主从臂放到相互对应的参考姿态，启动配对校准：

```bash
python "$LEROBOT_CORE_ROOT/stararm102_lumos_teleop.py" \
  --calibrate \
  --leader-port "$STARARM_PORT" \
  --can "$LUMOS_CAN" \
  --sdk-root "$LUMOS_SDK_ROOT" \
  --calibration-file "$LUMOS_MAPPING_FILE" \
  --gripper
```

按终端提示操作：

1. 将主从臂放到相互对应的参考姿态，按 Enter 记录。
2. 缓慢移动主臂六个关节，覆盖计划使用的遥操作范围；完成后按 Enter。
3. 记录主臂夹爪完全闭合与完全打开的位置。
4. 等待提示校准文件保存成功。

校准时保持在机械限位以内。按实际配置调整参数：

| 配置 | 校准命令 | 后续 LeRobot 命令 |
| --- | --- | --- |
| 无 HD 按钮板 | 增加 `--button-disable` | 将 `--teleop.button_enabled` 设为 `false` |
| 不使用夹爪 | 删除 `--gripper` | 将适用的 `--robot.gripper`、`--teleop.gripper` 均设为 `false` |

校准文件保存到 `LUMOS_MAPPING_FILE` 指定的位置，默认为 `~/.config/stararm102_lumos/calibration.json`。端口、关节顺序、夹爪设置和参考姿态均未变化时，可复用已有文件。首次配对必须使用上述向导，单独运行 `lerobot-calibrate` 不能代替该步骤。

### 4.2 导出并核对从臂关节限位

遥操作、采集与回放均需从臂关节限位文件；预览可在未提供限位文件时运行。限位数据应来自实际从臂模型。

只有确认实际型号使用 SDK 的 `FastTouchV2.SLDASM.urdf`，且 `joint1` 到 `joint6` 与 SDK 关节顺序和方向一致时，才使用：

```bash
python "$LEROBOT_CORE_ROOT/tools/export_joint_limits.py" \
  --urdf "$LUMOS_SDK_ROOT/src/config/FastTouchV2.SLDASM.urdf" \
  --output "$LUMOS_LIMITS_FILE"
```

其他型号使用对应的 URDF，并通过 `--joint-names` 指定 SDK 顺序下的六个关节名。导出后核对 `lower_rad`、`upper_rad`：各包含六个以 rad 为单位、与 SDK 关节方向一致的限位值。确认后保留文件；工具不会覆盖已存在的文件。

<a id="teleoperation"></a>

## 5. 预览与遥操作

### 5.1 预览映射结果

保持当前终端的环境变量有效，运行 LeRobot 原生命令：

```bash
lerobot-teleoperate \
  --robot.type=lumos \
  --robot.id=lumos01 \
  --robot.can_interface="$LUMOS_CAN" \
  --robot.sdk_root="$LUMOS_SDK_ROOT" \
  --robot.mapping_file="$LUMOS_MAPPING_FILE" \
  --robot.gripper=true \
  --robot.execute=false \
  --robot.cameras='{}' \
  --teleop.type=stararm102 \
  --teleop.id=stararm01 \
  --teleop.port="$STARARM_PORT" \
  --teleop.mapping_file="$LUMOS_MAPPING_FILE" \
  --teleop.gripper=true \
  --teleop.button_enabled=true \
  --fps=30
```

缓慢移动主臂，一次先检查一个关节，观察打印的目标。确认顺序、方向和夹爪开合方向后，按 `Ctrl+C` 停止。

根据预览结果调整参数，并同步到后续遥操作和采集命令：

| 参数 | 用途 |
| --- | --- |
| `--teleop.button_enabled=false` | 无 HD 按钮板时禁用按钮功能 |
| `--teleop.invert_gripper=true` | 反转夹爪开合方向 |
| `--teleop.signs='[-1,1,1,1,-1,-1]'` | 设置六个关节的映射方向，按实际结果调整各项 |
| `--teleop.joint_map='[0,1,2,3,4,5]'` | 设置关节对应顺序，修改后重新配对校准 |

### 5.2 启动主从跟随

将 Lumos 恢复到校准参考姿态附近，确认急停、方向和限位，再运行：

```bash
lerobot-teleoperate \
  --robot.type=lumos \
  --robot.id=lumos01 \
  --robot.can_interface="$LUMOS_CAN" \
  --robot.sdk_root="$LUMOS_SDK_ROOT" \
  --robot.mapping_file="$LUMOS_MAPPING_FILE" \
  --robot.joint_limits_file="$LUMOS_LIMITS_FILE" \
  --robot.gripper=true \
  --robot.execute=true \
  --robot.cameras='{}' \
  --teleop.type=stararm102 \
  --teleop.id=stararm01 \
  --teleop.port="$STARARM_PORT" \
  --teleop.mapping_file="$LUMOS_MAPPING_FILE" \
  --teleop.gripper=true \
  --teleop.button_enabled=true \
  --fps=30
```

移动主臂，Lumos 会按映射跟随。首次先做小幅单关节动作，逐项确认六关节与夹爪。

| 项目 | 默认值或操作 |
| --- | --- |
| 启动姿态允许偏差 | 第 2 关节为 0.40 rad，其余五个关节为 0.15 rad |
| 目标变化速度上限 | 50°/s |
| 单次目标变化上限 | 2° |
| HD 按钮 | 控制主臂六关节保持，不参与关节和夹爪映射 |
| 正常退出 | `Ctrl+C` |

启动姿态超限时，程序会显示当前姿态、校准姿态与差值。将对应关节恢复到参考姿态附近后重试。发生卡滞、碰撞或持续力矩报警时，立即使用硬件急停。

<a id="recording"></a>

## 6. 关节数据采集

熟悉遥操作后再采集。采集程序本身会控制 Lumos，不要同时运行另一个遥操作进程。

### 6.1 记录 10 个回合

示例每段 30 秒，段间留 15 秒重置场景，只保存在本地：

```bash
lerobot-record \
  --robot.type=lumos \
  --robot.id=lumos01 \
  --robot.can_interface="$LUMOS_CAN" \
  --robot.sdk_root="$LUMOS_SDK_ROOT" \
  --robot.mapping_file="$LUMOS_MAPPING_FILE" \
  --robot.joint_limits_file="$LUMOS_LIMITS_FILE" \
  --robot.gripper=true \
  --robot.execute=true \
  --robot.cameras='{}' \
  --teleop.type=stararm102 \
  --teleop.id=stararm01 \
  --teleop.port="$STARARM_PORT" \
  --teleop.mapping_file="$LUMOS_MAPPING_FILE" \
  --teleop.gripper=true \
  --teleop.button_enabled=true \
  --dataset.repo_id=local/lumos_joint_demo_001 \
  --dataset.root="$PWD/datasets/lumos_joint_demo_001" \
  --dataset.single_task="Move the arm through the demonstrated joint trajectory" \
  --dataset.fps=30 \
  --dataset.episode_time_s=30 \
  --dataset.reset_time_s=15 \
  --dataset.num_episodes=10 \
  --dataset.video=false \
  --dataset.no_stamp=true \
  --dataset.push_to_hub=false \
  --display_data=false \
  --play_sounds=false
```

首次可将 `dataset.num_episodes` 改为 `3`、`dataset.episode_time_s` 改为 `15`，确认采集正常后再增加数量。采集使用与遥操作相同的启动姿态检查、限位和速度限制；重置阶段仍可能处理主臂输入。

开始下一批采集时，同时修改 `dataset.repo_id` 和 `dataset.root`，例如将 `lumos_joint_demo_001` 改为 `lumos_joint_demo_002`。

### 6.2 采集参数

| 参数 | 含义 |
| --- | --- |
| `dataset.repo_id` | 数据集名称，本例不会触发上传 |
| `dataset.root` | 本地保存目录 |
| `dataset.single_task` | 本批数据的任务描述 |
| `dataset.fps` | 数据采集频率 |
| `dataset.episode_time_s` | 单回合时长 |
| `dataset.reset_time_s` | 段间重置时长 |
| `dataset.num_episodes` | 本次采集回合数 |
| `dataset.video=false` | 不保存视频 |
| `dataset.no_stamp=true` | 名称不自动附加时间戳 |
| `dataset.push_to_hub=false` | 只保存在本地 |

### 6.3 键盘控制

| 按键 | 功能 |
| --- | --- |
| 右方向键 | 提前结束当前阶段 |
| 左方向键 | 请求重录当前回合 |
| `Esc` | 结束采集 |

键盘监听受桌面环境、SSH 和终端权限影响，以启动日志为准。监听不可用时，程序按设定的回合数和时长运行。紧急停止使用硬件急停。

### 6.4 检查数据

等待正常结束并完成写盘，再查看：

```bash
find datasets/lumos_joint_demo_001 -maxdepth 3 -type f | head -30
```

使用 LeRobot 读取数据：

```bash
python - <<'PY'
from pathlib import Path
from lerobot.datasets import LeRobotDataset

dataset = LeRobotDataset(
    "local/lumos_joint_demo_001",
    root=Path("datasets/lumos_joint_demo_001").resolve(),
    video_backend="pyav",
)
print("回合数:", dataset.num_episodes)
print("总帧数:", dataset.num_frames)
print("状态维度:", dataset[0]["observation.state"].shape)
print("动作维度:", dataset[0]["action"].shape)
PY
```

启用夹爪时状态和动作都是 7 维（六关节 + 夹爪），不用夹爪时为 6 维。`observation.state` 是 Lumos 实测状态，`action` 是限速后最终发送的目标。这里没有图像或视频字段。

安装脚本已应用录制修正，使 `action` 保存限速后的实际下发目标。单独重装 LeRobot 后，应重新运行安装脚本再采集。

<a id="replay"></a>

## 7. 数据回放

回放会驱动 Lumos，不读取 StarArm102。确认数据对应当前机械臂，检查运动范围与急停，并将从臂恢复到校准参考姿态附近。

`episode` 从 `0` 开始，下面回放第一个回合：

```bash
lerobot-replay \
  --robot.type=lumos \
  --robot.id=lumos01 \
  --robot.can_interface="$LUMOS_CAN" \
  --robot.sdk_root="$LUMOS_SDK_ROOT" \
  --robot.mapping_file="$LUMOS_MAPPING_FILE" \
  --robot.joint_limits_file="$LUMOS_LIMITS_FILE" \
  --robot.gripper=true \
  --robot.execute=true \
  --robot.cameras='{}' \
  --dataset.repo_id=local/lumos_joint_demo_001 \
  --dataset.root="$PWD/datasets/lumos_joint_demo_001" \
  --dataset.episode=0 \
  --play_sounds=false
```

<a id="daily"></a>

## 8. 日常启动

完成首次安装、校准与限位核对后，日常使用无需重复安装。检查接线、急停与机械臂活动范围，上电后打开终端：

```bash
source "$HOME/miniforge3/etc/profile.d/conda.sh"
conda activate lumos-lerobot
cd ~/touch-r1-leader-arm/lerobot

export STARARM_PORT=/dev/ttyUSB0
export LUMOS_CAN=can0
export LEROBOT_CORE_ROOT="$PWD/.dependencies/stararm102-lumos-lerobot"
export LUMOS_SDK_ROOT="$LEROBOT_CORE_ROOT/.dependencies/startouch_sdk"
export LUMOS_MAPPING_FILE="$HOME/.config/stararm102_lumos/calibration.json"
export LUMOS_LIMITS_FILE="$PWD/lumos_joint_limits.json"

ip -details link show "$LUMOS_CAN"
```

Conda 安装位置、串口和 CAN 接口与示例不同时，修改对应路径与变量。CAN 接口为 `DOWN` 时，按[通信设置](#connection)启用。

确认从臂位于参考姿态附近后，先运行[预览命令](#teleoperation)，检查正常再启动遥操作。需要采集时，退出遥操作后运行[采集命令](#recording)。

<a id="faq"></a>

## 9. 常见问题

| 问题 | 处理方法 |
| --- | --- |
| 找不到 `conda` | 使用 `source` 加载实际 Conda 安装目录下的 `etc/profile.d/conda.sh` |
| 无法下载硬件适配依赖 | 检查 GitHub 网络连接与仓库访问权限 |
| 依赖版本不符或有本地修改 | 检查报错目录，保存并处理本地修改后重试；安装脚本不会重置已有目录 |
| 找不到 `lerobot-teleoperate` | 激活 `lumos-lerobot` 环境，确认安装成功 |
| 串口 `Permission denied` | 加入 `dialout` 组后注销 Ubuntu 登录并重新登录 |
| 找不到 `/dev/ttyUSB0` | 查看实际串口和 `/dev/serial/by-id/`，修改 `STARARM_PORT` |
| 找不到 `can0` | 检查适配器驱动和实际接口名 |
| CAN 提示 busy | 查看是否已 UP、速率是否正确；重配前先停止控制程序 |
| 没有校准文件 | 核对 `LUMOS_MAPPING_FILE`，完成配对向导 |
| 端口或关节顺序与校准不符 | 使用原校准设置，或重新配对校准 |
| HD 按钮 ID 7 不响应 | 有按钮时检查接线与 ID；没有按钮板才禁用 |
| 缺少从臂限位 | 核对 `LUMOS_LIMITS_FILE`，生成并核实限位 |
| `Lumos is away from calibrated home` | 查看报错中的当前姿态、校准姿态、差值和阈值；将超限关节恢复到参考姿态附近，或重新配对校准 |
| SDK 找不到配置 | 检查 `LUMOS_SDK_ROOT/src/config/robot_kinematics.yaml` |
| 数据目录已存在 | 为新采集换一个新名称和新目录 |
| 方向不正确 | 停止执行，在预览模式逐关节核对 `joint_map` 与 `signs` |
| 卡滞、碰撞、力矩报警 | 停止并使用硬件急停，检查机械状态和映射，不提高保护阈值掩盖问题 |

<a id="dependencies"></a>

## 10. 依赖与验证范围

安装脚本使用以下固定版本：

| 依赖 | 来源 | 提交版本 |
| --- | --- | --- |
| LeRobot 硬件适配器 | [stararm102-lumos-lerobot](https://github.com/VincentHSS/stararm102-lumos-lerobot) | `454979c7c8b9d5ced15f1964a2d588acf531ae3f` |
| LeRobot 0.6.2 | [huggingface/lerobot](https://github.com/huggingface/lerobot) | `3991580a5673f5f0219a4e8835a5f973eeccf9a7` |
| Lumos SDK | [lumos-open/startouch_sdk](https://github.com/lumos-open/startouch_sdk) | `040412542c0b6b6fd2bb6dd652c0de6c666631be` |

重新运行安装脚本会核对固定版本，不会自动升级或覆盖本地修改。

上游[验证记录](https://github.com/VincentHSS/stararm102-lumos-lerobot/blob/454979c7c8b9d5ced15f1964a2d588acf531ae3f/VALIDATION.md)涵盖软件接口、控制循环、数据读写与回放，硬件通信使用测试替身。本仓库的 Ubuntu 完整安装、SDK 编译及实机运行尚未完成验证。本文不包含视觉策略训练与部署。
