#!/usr/bin/env bash
# Connect 集成测试一体化运行脚本：启动 wine ATK → 预热 → 分组跑套件。
#
# ATK 4.2.0-alpha.1（wine）实测工程注意事项：
#   1. 命令发送需保持间隔（连发 NACK）：测试侧已按 200ms 节流 +
#      NACK 自动重试（见 src/tests/integration/conftest.py）；
#   2. TCP 可连早于命令就绪：引擎初始化需数十秒，需预热；
#   3. socket 层对连接数敏感：同一实例约 5 次连接后拒绝服务，
#      因此把 10 个用例分成两组、组间重启 ATK；
#   4. 单条长连接遇重计算命令（Access 等）可能无响应挂起，
#      因此采用每用例独立短连接而非会话级长连接。
set -u

ATK_ROOT="${ATK_ROOT:-/home/ouyangjiahong/codes/ATK/ATK-v4.2.0-alpha.1-windows-x64/ATK-4.2.0-alpha.1}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
WARMUP="${WARMUP:-30}"
GROUP_A=(
    test_step01_create_scene
    test_step02_access_aer_access_rm
    test_step03_access_multi
    test_step04_coverage_family
    test_step05_coverage_multi
)
GROUP_B=(
    test_step06_vector_tool
    test_step07_adv_cat
    test_step08_walker_delta
    test_step09_quick_and_exec_report
    test_step10_mcs_rpo_segment
)

start_atk() {
    pkill -9 -f "ATK.exe" 2>/dev/null
    sleep 2
    ( cd "$ATK_ROOT" && WINEDLLOVERRIDES="mscoree,mshtml=" \
      nohup wine ATK.exe > /tmp/atk_integration.log 2>&1 & )
    echo "ATK 预热 ${WARMUP}s..."
    sleep "$WARMUP"
}

overall=0
for group in A B; do
    declare -n tests="GROUP_${group}"
    start_atk
    echo "=== 组 ${group}（${#tests[@]} 个用例）==="
    if ! ATK_INTEGRATION=1 uv run pytest -q \
        "${tests[@]/#/src/tests/integration/test_new_commands.py::}" \
        > "/tmp/pytest_group_${group}.log" 2>&1; then
        overall=1
        grep -E "^FAILED|^ERROR" "/tmp/pytest_group_${group}.log"
    fi
    tail -1 "/tmp/pytest_group_${group}.log"
done

echo "==== 汇总 ===="
[ "$overall" -eq 0 ] && echo "集成套件通过（环境门控 skip 项见各组日志）" \
    || echo "存在失败/错误用例（见上方输出）"
exit "$overall"
