# atk-python-sdk

atk-python-sdk 是社区整理的 [ATK（Aerospace Tool Kit）](https://www.osredm.com/atknudt/atk/about) 二次开发包，在官方 Connect 协议和 Component 接口之上提供构建器风格的 Python API、完整异常层次和报告解析工具。

## 两种工作模式

| 模式 | 需要 ATK 图形界面 | 工作方式 |
|------|------------------|----------|
| **Connect** | 需要（ATK 正在运行） | TCP 连接 → Connect 命令 |
| **Component** | 不需要 | 直接加载 DLL → 面向对象接口 |

## 安装

```bash
uv sync
```

`src/vendored/` 内置了 ATK 提供的 Connect 模式 SWIG 绑定（含 Windows / Linux 二进制），安装后即可使用 Connect 模式。

Component 模式需要 ATK 安装目录中的 `ATKComponentPythonModule.py` 与 `_ATKComponentPythonModule.pyd`，二者任选其一：

- 复制到 `src/vendored/`；
- 或设置环境变量 `ATK_ROOT` 指向 ATK 安装目录。

## 快速开始

### Connect 模式

需要 ATK 软件已在 `127.0.0.1:6655` 运行：

```python
from atk.connect import connect

with connect() as atk:
    scenario = atk.create_scenario('MyMission')
    scenario.set_analysis_period('1 Jan 2024', '7 Jan 2024')

    sat = atk.create_satellite('Sat1')
    sat.set_propagator('PropagatorAstromaster')
    sat.set_keplerian(sma=7100, ecc=0.001, inc=30, raan=0, argp=0, ta=0)
    sat.run_mcs()

    facility = atk.create_facility('Beijing', lat=39.9, lon=116.4, height=50)

    result = atk.quick_report('*/Satellite/Sat1', 'Position', time_period='*')
    df = result.to_dataframe()  # 需要 pandas
```

### Component 模式

无需运行 ATK 图形界面：

```python
from atk.component import component_session
from atk.component.scenario import ScenarioBuilder
from atk.component.satellite import SatelliteBuilder
from atk.component.facility import FacilityBuilder
from atk.component.mcs import McsBuilder

with component_session() as session:
    scenario = ScenarioBuilder(session, session.new_scenario('MyMission'))
    scenario.set_analysis_period('1 Jan 2024', '7 Jan 2024')

    sat = SatelliteBuilder(session.create_satellite('Sat1'))
    sat.set_propagator_type('PropagatorAstromaster')

    mcs = McsBuilder(sat.get_mcs_driver())
    mcs.initial_state_keplerian(sma=6678, ecc=0, inc=28.5, raan=0, argp=0, ta=0)
    mcs.propagate_duration(duration_seconds=5444.0)
    mcs.run()

    # 地面站与传感器
    facility = FacilityBuilder(scenario.create_facility('Beijing'))
    facility.set_position_geodetic(lat=39.9, lon=116.4, alt=50)

    sensor = facility.create_sensor('Sensor1')
    sensor.set_pattern_simple_conic(cone_angle=40)
    sensor.point_fixed_euler(sequence=123, a=180, b=0, c=0)
```

## 文档

详细文档位于 [docs/](docs/index.md)，也可在线阅读：[GitHub Pages](https://ouyangjiahong26.github.io/atk-python-sdk)。

- [快速开始](docs/guides/getting-started.md) — 5 分钟上手
- [Connect 模式](docs/architecture/connect-mode.md) — TCP 连接与命令发送
- [Component 模式](docs/architecture/component-mode.md) — DLL 直接加载
- [轨道力学基础](docs/guides/orbital-mechanics-primer.md) — 理解示例代码中的公式
- [ATK Connect 命令参考](docs/reference/atk-commands.md)

本地构建文档：

```bash
uv sync --extra docs
uv run mkdocs serve
```

## 运行测试

```bash
uv sync --dev
uv run pytest
```

测试使用 mock 模拟 ATK 绑定，无需安装 ATK。

## 参与贡献

欢迎提 issue 和 PR。**如果 issue、PR 由 AI 工具参与编写，请在标题最前面标注 `[AI Generated]`。** 详见[贡献指南](CONTRIBUTING.md)。
