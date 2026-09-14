# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此仓库中工作时提供指引。

## 构建与测试命令

```bash
uv sync --dev              # 安装开发依赖
uv run pytest src/tests/ -v                     # 运行全部测试
uv run pytest src/tests/test_utils.py -v        # 单个文件
uv run pytest src/tests/test_utils.py::TestParseAtkTime::test_full_datetime -v  # 单个测试
uv run pytest src/tests/ -v --cov --cov-report=term-missing   # 带覆盖率
uv sync --extra docs && uv run mkdocs serve     # 本地构建文档
```

未配置 linter 和 formatter。CI 由 `.github/workflows/` 下的 CI / Release / 部署文档三个流水线组成。

## 架构

ATK Python SDK 通过两种相互独立的模式封装 ATK（Aerospace Tool Kit）：

- **Connect 模式**（`atk.connect`）— TCP 连接运行中的 ATK 图形界面。使用 vendored 的 SWIG 绑定（`src/vendored/ATKConnectModule`）。入口：`connect()` 上下文管理器 → `ATKConnection`。
- **Component 模式**（`atk.component`）— 直接加载 DLL，无需图形界面。需要 ATK 安装（`ATK_ROOT` 环境变量）。入口：`component_session()` 上下文管理器 → `ComponentSession`。

两种模式共享 `atk.exceptions`（以 `ATKError` 为根的异常层次）和 `atk.utils`（时间解析、路径操作、`CMDRESULT` 解析）。

### Connect 模式的猴子补丁

每个 connect 子模块（scenario、satellite、facility、mcs、reports、coverage、constellation）在 import 时调用 `_patch_connection()` 向 `ATKConnection` 注入工厂方法。这由 `connect/__init__.py` 导入全部子模块触发，不要删除这些导入。

### Vendored 原生库

`src/vendored/` 包含 SWIG 生成的 Python 封装和平台相关的原生扩展（Windows 为 `.pyd`，Linux 为 `.so`）。这些是 ATK 提供的文件，不要修改（`ATKComponentPythonModule.py` 是测试替身，可更新）。

### 构建器模式

两种模式都使用流式构建器（`ScenarioBuilder`、`SatelliteBuilder`、`FacilityBuilder`、`SensorBuilder`、`McsBuilder`）。Connect 模式构建器封装经 TCP 发送的命令字符串；Component 模式构建器封装 SWIG 对象引用（`IScenario`、`ISatellite`、`IFacility`、`ISensor`、`IVADriverMCS`）。

## 关键约定

- **src 布局**：包代码在 `src/atk/`，测试在 `src/tests/`
- **零运行时依赖**：SDK 不依赖任何 pip 包（pandas 支持是可选的运行时导入）
- **单元测试 mock SWIG**：所有测试使用 `unittest.mock.MagicMock` 模拟原生绑定 — 运行测试无需安装 ATK
- **文档使用中文**：`docs/`、`README.md`、注释与提交信息均为中文
