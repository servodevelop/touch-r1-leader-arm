#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
CORE_URL="https://github.com/VincentHSS/stararm102-lumos-lerobot.git"
CORE_COMMIT="454979c7c8b9d5ced15f1964a2d588acf531ae3f"
CORE_DIR="$PROJECT_DIR/.dependencies/stararm102-lumos-lerobot"
PYTHON_BIN="${PYTHON_BIN:-python}"

for tool in git "$PYTHON_BIN"; do
  if ! command -v "$tool" >/dev/null 2>&1; then
    echo "找不到命令：$tool。请先安装 Git 并激活 Python 3.12 环境。" >&2
    exit 1
  fi
done

"$PYTHON_BIN" - <<'PY'
import sys
if sys.version_info[:2] != (3, 12):
    raise SystemExit("请先激活 Python 3.12 环境，再安装 LeRobot 接入依赖。")
print("使用 Python:", sys.executable)
PY

if [[ ! -r /etc/os-release ]]; then
  echo "此安装入口仅支持 Ubuntu/Debian。" >&2
  exit 1
fi
# shellcheck disable=SC1091
source /etc/os-release
if [[ "${ID:-}" != "ubuntu" && "${ID:-}" != "debian" ]]; then
  echo "此安装入口仅支持 Ubuntu/Debian，当前为 ${PRETTY_NAME:-未知系统}。" >&2
  exit 1
fi

if [[ ! -e "$CORE_DIR" ]]; then
  mkdir -p "$(dirname -- "$CORE_DIR")"
  echo "下载 LeRobot 硬件适配依赖：$CORE_URL"
  git clone "$CORE_URL" "$CORE_DIR"
  git -C "$CORE_DIR" checkout --detach "$CORE_COMMIT"
elif [[ ! -d "$CORE_DIR/.git" ]]; then
  echo "$CORE_DIR 已存在但不是 Git 仓库；请检查目录，不会覆盖本地文件。" >&2
  exit 1
fi

if [[ "$(git -C "$CORE_DIR" remote get-url origin)" != "$CORE_URL" ]]; then
  echo "依赖仓库来源与预期不符；请检查 $CORE_DIR，不会改写远端。" >&2
  exit 1
fi
if [[ "$(git -C "$CORE_DIR" rev-parse HEAD)" != "$CORE_COMMIT" ]]; then
  echo "依赖版本与固定版本 $CORE_COMMIT 不符；请检查 $CORE_DIR，不会重置本地修改。" >&2
  exit 1
fi
if [[ -n "$(git -C "$CORE_DIR" status --porcelain --untracked-files=normal)" ]]; then
  echo "依赖目录有本地修改；请检查 $CORE_DIR 后重试，不会覆盖文件。" >&2
  exit 1
fi

PYTHON_BIN="$PYTHON_BIN" bash "$CORE_DIR/scripts/install_lerobot_ubuntu.sh"

echo "LeRobot 接入依赖安装完成。请按 lerobot/README.md 设置端口、校准并核对限位。"
echo "依赖目录：$CORE_DIR；请保留该目录，运行时会使用其中的 SDK 和适配器。"
echo "安装过程未连接机械臂或发送运动目标。"
