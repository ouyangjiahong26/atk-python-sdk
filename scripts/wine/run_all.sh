#!/usr/bin/env bash
# wine 内嵌 Windows Python 运行 Component 冒烟测试。
set -eu

ATK_ROOT="${ATK_ROOT:-/home/ouyangjiahong/codes/ATK/ATK-v4.2.0-alpha.1-windows-x64/ATK-4.2.0-alpha.1}"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
WORK=/tmp/atk42test
mkdir -p "$WORK"
# TLE 数据（ASCII 路径，避免 GBK 目录名问题）
ATK_TLE="$ATK_ROOT/Help/Examples"
tle_src=$(find "$ATK_TLE" -name "TLE20230212.txt" | head -1)
[ -n "$tle_src" ] && cp -f "$tle_src" "$WORK/tle.txt" || echo "提示：未找到示例 TLE，接近分析将仅验证封装"

to_z() { # /unix/path -> Z:\unix\path
    local p="$1"
    echo "Z:${p//\//\\}"
}

cd "$ATK_ROOT"
exec wine Python/_internal/python.exe "$(to_z "$REPO/scripts/wine/component_smoke.py")" \
    "$(to_z "$ATK_ROOT")" "$(to_z "$REPO")" "$(to_z "$WORK")"
