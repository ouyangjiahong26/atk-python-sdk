# CHANGELOG


## v1.3.0 (2026-10-03)

### Bug Fixes

- 修复评审发现的四处问题
  ([`c4e6348`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/c4e6348f86f916007be5a67da5852ebdcc954121))

- coverage.py：删除误留的 COV_RM_STYLES 重复定义块 - reports.py：补回被误删的 from __future__ import annotations
  （requires-python >=3.9 下 str | None 注解需要延迟求值） - session.pyi：补回被误删的 send_str 存根与 McsBuilder 导入 -
  repro2_exec_report.py：补 import os；test_new_commands.py 清理 装饰器与 def 间空行

- 补回 session.pyi 误删的 ReportResult 导入与 send_retry 存根
  ([`15cc477`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/15cc477a5ca93918becd3e8ef82eb73563b41c8e))

### Chores

- 移除 docs/superpowers，该工具不再使用
  ([`2beded1`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/2beded1d0ec8eb41bec2fe07c83d4d3e19006b1c))

### Documentation

- Readme 添加徽章，补充 MIT LICENSE 文件
  ([`f8f7d11`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/f8f7d112c90e2ddb7529870b84986ef5f5d39123))

- 更新 4.2 命令参考与 CHANGELOG，版本升至 1.3.0
  ([`755fa77`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/755fa7712bbe6cebdb21dc594d1940c9af7adee6))

- docs/reference/atk-commands.md：增补 4.2 全部新命令语法与示例 （Access/AER/Access_RM/AccessMulti/Cov
  族/CovMulti/VectorTool/ ACAT/星座创建族/QuickReport 族/Exec_Report/RPO 段类型） - CHANGELOG
  v1.3.0：两批次特性、测试与上游限制清单 - 版本 1.2.0 → 1.3.0

### Features

- **component**: 封装 ATK 4.2 新增 Component 接口
  ([`b1ad493`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/b1ad493882edefdfe35217c681889d71d2e2f8de))

- 新增 access.py：AccessCalculator（IAtkAccess：计算/区间/23 种报告 枚举/约束管理）与 AccessConstraints - 新增
  vgt.py：VgtBuilder（六个组件组的创建/删除/查询，位移向量/ 叉积/两向量夹角便捷方法，枚举名短名模糊解析） - 新增
  constellation.py：ConstellationDesigner（12 个星座设计方法， int 参数按 SWIG typemap 实测转换） - 新增
  cat.py：CatAnalysis（场景/TLE 目标、时间窗、计算、12 项结果 向量）与 CatAdvanceConfig（滤波器与门限） - 新增
  coord.py：BatchCoordinateTransform（时间类型/坐标系/单位/ vector_EDataSequence 数据列序/导入导出） - 新增
  maneuver.py：ManeuverDetectionAnalysis（POD 变体，strDetectDVutc 为 std::string& 出参在 4.2.0-alpha.1
  不可调用，转译为带替代方案的 明确报错）与 TLEManeuverDetection（TLE 历史机动检测，出参 vector<string>+vector<double>，可正常调用） -
  ComponentSession 新增 constellation_designer/cat_analysis/
  batch_coord_transform/access_calculator/maneuver_detection 便捷方法 - vendored 测试替身增补：指针与 SWIG
  向量助手、eACCESS_*/VGT/时间 类型等新枚举、根类 GetCat/GetConstellDesign/GetBatchCrdnTransform

- **connect**: 封装 ATK 4.2 新增 Connect 命令
  ([`6a32f44`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/6a32f44c31b80e6b199ca7d1a17792e3a8039d53))

- 新增 access.py：AccessBuilder（Access/AER/Access_RM 九种报告样式， 样式非法抛 ATKValueError）与
  AccessMultiBuilder（Assets/Objects/ Access Compute 先配置后计算框架） - 新增
  vgt.py：VectorToolBuilder（六类向量几何组件的 Create/Modify/ Delete，类型表按帮助文档校验，附位移向量/叉积/两向量夹角便捷方法） - 新增
  cat.py：AdvCatBuilder（ACAT 高级接近分析：阈值/主次目标/ 时间窗/Compute/SSCFile） - 扩展
  coverage.py：set_interval/access_compute/access_clear/access_rm/ fom_rm；新增
  CoverageMultiBuilder（CovMulti/CovMulti_RM） - 扩展 constellation.py：ConstellationCreator（WalkerDelta/
  WalkerCustom/Rosette/Flower/AsymmetricFlower，种子与六要素两种形态， Semimajoraxis/TureAnomaly 按文档原文拼写） - 扩展
  reports.py：quick_report_create/add/list/get 与 exec_report_create/rm（ExecReport） - 扩展 mcs.py：通用
  insert_segment（含 24 种 RPO 段类型校验） - session.py 新增 wait_ready()/send_retry()：命令节流 + NACK 退避
  重试（Connect 服务端对命令速率敏感、启动加载完成前部分命令暂不可用）

### Refactoring

- 统一时间区间参数的成对校验语义
  ([`6d50b89`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/6d50b891879b448601cc0207dd351d2d2acad6f3))

utils 新增 validate_time_pair：start/stop 必须成对提供，否则抛
  ATKValueError。access.py（_time_param/_interval_param）、coverage.py （access_rm，修复单传 stop
  被静默忽略）、reports.py（ExecReport ._options）三处统一改用该助手，消除同形逻辑的三份实现与行为分叉； 补负例单测

### Testing

- 新增 4.2 封装的 mock 单测与真实 ATK 集成测试
  ([`f3c6073`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/f3c6073c964b6bca0962f827a1f661d11046a326))

- Connect：test_access/test_vgt/test_cat/test_constellation_reports， 扩展
  test_coverage/test_mcs/test_session（期望工厂方法清单）， 断言命令三元组精确匹配与非法参数负例（mock，无 ATK 可跑） -
  Component：test_new_modules 覆盖六个新模块的 SWIG 调用序列与 TLEManeuverDetection 出参归一化 -
  集成：src/tests/integration（ATK_INTEGRATION=1 门控），conftest 按 200ms 节流 + NACK 自动重试（Connect
  服务端速率敏感），RPO 等 命令在 wine 部分实例不可用时环境门控 skip（非缺陷） - mock 套件由 93 增至 207 个用例

- 新增集成 runner 与 wine Component 冒烟脚本
  ([`9f6318d`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/9f6318ddab2fff4d91a8b5d397c2e418d52663aa))

- scripts/run_integration.sh：启动 wine ATK → 预热 → 分组执行集成 套件（规避连接数上限），内嵌实测工程注意事项说明 -
  scripts/integration_canary.py：命令就绪探测 - scripts/wine/run_all.sh + component_smoke.py：在真实
  ATKComponentPythonModule 下逐项 PASS/FAIL（9 PASS + 1 LIMITED 上游缺陷），覆盖 xlsx R12 全部接口与 RPO 段插入 -
  scripts/feedback/：ATK 上游问题反馈材料（POD string& 出参、 Exec_Report 空返回），复现脚本只依赖 ATK 自带模块


## v1.2.0 (2026-09-14)

### Bug Fixes

- Add hatchling config to exclude vendored from package
  ([`e105ead`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/e105eadaf3d225a28eb954b429d3fabac4661cb0))

- Resolve pyright diagnostic issues
  ([`fae4e97`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/fae4e97ff38b293611049b5f9bb49b024b9687e5))

- Add str | None types to ATKComponentPythonModule stub - Add reportArgumentType=none to test files
  using MockATKConnection - Add type: ignore comments for private __slots__ attribute access - Add
  type: ignore for @contextmanager return type in tests - Remove unused MagicMock import from
  test_satellite.py - Remove unused MagicMock import from test_facility.py

Remaining reportMissingImports for ATKConnectModule/pandas/ATKComponentPythonModule are expected
  (external dependencies not installed in type-check environment).

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Update ImportError message to use uv instead of pip
  ([`288d1ad`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/288d1ad8222e28656ae115aa01b342a643d846e3))

- 修复测试替身在 Python 3.9 下的注解求值错误
  ([`24910a7`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/24910a74c5e3814af1a87f6a8808466dc0645376))

ATKComponentPythonModule.py 测试替身的 path: str | None 注解 在 3.9 运行时报 TypeError（PEP 604 需 3.10+）。 此前 CI
  从未跑通故未暴露；补 from __future__ import annotations 使注解延迟求值。已在 3.9 隔离环境验证 93 个测试全部通过。

- **build**: 移除 semantic-release 的 build_command，修复发布失败
  ([`0b3cb82`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/0b3cb8299f9740f9a18a3735064749966861ad6d))

官方 action 在自有容器内执行 build_command，容器中没有 uv， 导致 'uv: command not found'（exit 127）中止发布。 产物构建改由 release
  workflow 后续步骤在 job 环境完成 （uv build + gh release upload），semantic-release 只负责 版本计算、tag 与 GitHub
  Release。

- **coverage**: Raise error on unexpected CoverageStats format
  ([`551dd51`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/551dd5107ab7958bfaff7d38260bbf83f86fcd6d))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Build System

- 修复 hatch 打包配置，dev 依赖迁移到标准依赖组
  ([`9343da6`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/9343da61abec14d7dcd8fcf453970286861d8fce))

- 原配置段 [tool.hatchling] 无效，hatchling 不识别， 导致 uv sync/build 一直失败；改为 tool.hatch.build.targets.wheel，
  wheel 同时打包 src/atk 与 src/vendored（connect 模块按相对路径定位 vendored） - pytest 依赖从 optional-dependencies
  迁移到 PEP 735 dependency-groups， 修复 uv sync --dev 装不上测试依赖的问题 - 提交 uv.lock，保证 CI 可重现构建

### Continuous Integration

- Migrate ci.yml from setup-python/pip to setup-uv
  ([`455566d`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/455566d98f0ddd4a78bcef01cf6d412f5cfb0c0d))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Migrate docs.yml from setup-python/pip to setup-uv
  ([`5e15188`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/5e151887178f081f63824f9321594503bf376ce6))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Migrate release.yml from setup-python/pip to setup-uv
  ([`3953b3b`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/3953b3bc531f6aa3530f3bfe11af4e26bb0a94ba))

- 修复流水线并接通语义化发布链路
  ([`28a1fdd`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/28a1fddef542ad70a7f8f6c1470742c81ad5756c))

- ci.yml：Python 版本矩阵此前未传给 setup-uv，实际未生效，已接上； pytest/mkdocs 改为 uv run 调用（原裸调用在 uv 环境中找不到可执行文件） -
  release.yml：原配置打 tag 后既不推送也不创建 GitHub Release， 改用官方 python-semantic-release action，发布前先跑测试，
  有新版本时构建产物并上传到对应 Release - docs.yml：mkdocs gh-deploy 同样改为 uv run 调用

- 测试矩阵扩展到 Python 3.15
  ([`78df43c`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/78df43cdeaa98a62deb37c443a104485b314fa2b))

矩阵由 3.9-3.12 扩展为 3.9-3.15（3.15 当前解析到最新预发布版）， pyproject classifiers 同步补充 3.13/3.14/3.15

### Documentation

- Add code quality fix implementation plan
  ([`10bc958`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/10bc9586be5d55b28d9dfdab33564ec5a8142e9b))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Add uv migration design spec
  ([`1b8a636`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/1b8a6362423493e86e72a31e2c53869c533df2e5))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Add uv migration implementation plan
  ([`80c46e9`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/80c46e9d5474adc2a2dbbe65b9fb7932c3100ab7))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Update CLAUDE.md pip commands to uv
  ([`0ae79c4`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/0ae79c451ecd87289a32718323fc94bc3284b0b3))

- Update getting-started.md pip commands to uv
  ([`f36d4ab`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/f36d4ab865536cda0fa594131cdb8b72a981c0b1))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Update README.md pip commands to uv
  ([`43f89c1`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/43f89c18df9bc393d54e6021a1d54c6843b9bd47))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Update vendored-modules.md pip command to uv
  ([`defeb32`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/defeb32c36a0858f1aee01fe610f0ebf26be7744))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- 新增 AGENTS.md，同步交流语言、写作要求与编码准则
  ([`c41b9a0`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/c41b9a0d4352a2ce47350cd3b31378cd293bc427))

- 新增贡献指南与 issue/PR 模板，约定 AI 参与需标注 [AI Generated]
  ([`edf8fb0`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/edf8fb0d14a9745c87c3c2fe2bb1af21172557f9))

- 贡献指南说明交流语言、开发环境、约定式提交与代码约定 - bug/功能建议两套 issue 模板与 PR 模板，均提示： AI 工具参与编写的 issue/PR 须在标题最前面加 [AI
  Generated]

- 精简 README 并全面中文化仓库说明
  ([`a529140`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/a52914008231559cb8e0fe8b59537c7e4feec2ed))

- README 由英文 339 行精简为中文，定位采用一句话： atk-python-sdk 是社区整理的 ATK 二次开发包； 删除的 API 参考内容 docs 与 docstring 中已有
  - CLAUDE.md 中文化并修正过时信息（原文称无 CI、Component 无测试） - 仓库链接统一指向 ouyangjiahong26（与 git remote 一致）， 涉及
  pyproject urls 与 mkdocs repo_url

### Features

- **component**: 补充地面站与传感器支持
  ([`dc355e6`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/dc355e6c3da8f3a909cab02130d24f4be67507b2))

依据 atk-doc《4-二次开发COMPONENT模式》接口文档新增： - FacilityBuilder：大地/笛卡尔坐标设置与读取、二维颜色 -
  SensorBuilder：圆锥/矩形视场、固定欧拉角/四元数指向 - ScenarioBuilder/ComponentSession 新增 create_facility() - 测试替身补齐
  eSensor、eGeodetic、欧拉序列枚举 - 新增 18 个 mock 单元测试与 facility_sensor 示例

- **facility**: Add latitude/longitude range validation
  ([`c904ff0`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/c904ff0ac8d8d9c996e6ca29fe44ffa82d2e4294))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **satellite**: Add TLE line length validation
  ([`153bffb`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/153bffb6bf8378f7e61abf9e4302d51073e5aaef))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Refactoring

- Migrate from setuptools to hatchling build backend
  ([`12bf5a1`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/12bf5a1a0ac8d35c728079960dba3b9ca08be88a))

- **component**: 收敛 _get_enum 到 session 模块
  ([`f7995c7`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/f7995c708f4627d219043fc64186e1c469403683))

- _get_enum 此前在 scenario.py 与 facility.py 各有一份相同实现， 收敛为 session.py 中的共享函数，两处改为模块级引用 - 顺带中文化
  connect/satellite.py 中遗留的英文 docstring（TLE 校验）

- **utils**: Simplify format_atk_time implementation
  ([`837fc1b`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/837fc1b9acfc780f45579ca0b04a222da8ede57e))

### Testing

- **component**: Add ComponentSession and SatelliteBuilder tests
  ([`79a5dbf`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/79a5dbf73a4fe295005a9dcacc7a4fd1712ba74a))

- Add test_session.py with tests for new_scenario and create_satellite - Add test_satellite.py with
  tests for set_keplerian and set_mass - Add ATKComponentPythonModule.py stub to vendored for
  testing without ATK DLL

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **session**: Add monkey-patch verification test
  ([`56c9e93`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/56c9e93eb24783e87695c3ff951efd9fa47c4ecc))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>


## v1.1.0 (2026-04-20)

### Features

- **vendored**: 将atk Python Connect SDK升级到ATK 4.0.0附带版本
  ([`1a36a6d`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/1a36a6db2adc1efeef43069298dd35ca118fd551))


## v1.0.0 (2026-04-15)

### Bug Fixes

- Align ATK Connect commands with official ATK documentation
  ([`b5d7c11`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/b5d7c1141eb52bd04d77ec3ebabd35596f74c3fe))

Key fixes based on testing against ATK v4.0-rc.4 Help docs:

1. ATKConnection.send(): add NACK to error detection (ATK returns NACK for command failures, not
  just ERROR/FAIL/FALSE)

2. ScenarioBuilder.create(): use New command format from docs - Old: obj='*/Scenario/{name}',
  param='' → NACK - New: obj='*', param=' Scenario {name}' → '' or NACK if scenario already exists
  (handled gracefully since ATK always has a default scenario loaded)

3. SatelliteBuilder: use correct ATK command formats - create(): obj='*', param=' Satellite {name}'
  (not '*/Satellite/{name}') - set_propagator(): stores propagator for later use; no immediate
  send() - set_keplerian(): uses SetState with Classical {prop} format instead of individual
  SetValue calls (Classical HPOP/TwoBody work; SGP4 requires TLE format) - set_cartesian(): uses
  SetState with Cartesian format

4. WalkerBuilder.build(): fixed satellite creation to match docs: - obj='*', param=' Satellite
  {name}' for New - SetState with Classical {prop} for orbital elements

5. All tests updated to match new command formats

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Import connect submodules in __init__.py to trigger ATKConnection patches
  ([`2200834`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/22008343bbdf55803f2df2df19f8819c1d85a2d0))

Submodules (scenario, satellite, mcs, coverage, constellation) use _patch_connection() at import
  time to add factory methods (create_scenario, create_satellite, constellation_builder,
  create_coverage, mcs_builder) to ATKConnection. Since __init__.py only imported session, these
  patches never ran and those methods were missing from the connection object.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- Move vendored/ into src/ and fix vendored path resolution
  ([`8a2a58c`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/8a2a58cad9483530ecfa9bac9f3de0ff6b366275))

- vendored/ (ATK SWIG bindings) is now src/vendored/ alongside atk/, so it is part of the installed
  package and importable. - src/atk/connect/session.py resolves the vendored/ path relative to
  __file__ (src/atk/connect/) rather than as a top-level module. - .gitignore: add
  !src/vendored/*.pyd and !src/vendored/*.so to keep ATK native DLLs tracked. - pyproject.toml:
  remove stale vendored package-dir mapping.

- Track ATK official DLLs in src/vendored/ via gitignore negation rules
  ([`2818fb2`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/2818fb22cd4162c915b00a7cfca478bf27c7bd58))

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **connect**: Add Animate Reset after SetAnalysisTimePeriod
  ([`1141fca`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/1141fca2f2ca6a26752d6b34197a4ee34d40a64d))

ATK requires Animate * Reset after changing the analysis time period to apply the change to the
  scenario timeline. Without this follow-up command, subsequent operations may fail.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **connect**: Add type stub for ATKConnection monkey-patched methods
  ([`abd3b5a`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/abd3b5a76ba30045baf1490105ba9beb221e09d9))

- **connect**: Align ATK Connect command format with official documentation
  ([`e4667ff`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/e4667ffb8361c93847717c4fefcca864a3b615dc))

Two bugs found during debugging:

1. atkConnect() was called with 4 args: (conID, cmd, obj_path, param) but ATK expects 3 args:
  (conID, cmd, "obj_path param") with obj_path and param merged into a single string.

2. The New Scenario/Satellite commands used obj_path='*' but the official ATK documentation uses
  obj_path='/' (root).

Debug print added to send() to show commands and responses, making future debugging easier.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **connect**: Fix reports monkey-patch bug, remove debug prints, improve error handling
  ([`6304eec`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/6304eec1592e4853ca4cd3476a1b36d314972909))

- Import reports module in connect/__init__.py so quick_report/report_rm are actually monkey-patched
  onto ATKConnection (was a runtime AttributeError) - Remove debug print() from ATKConnection.send()
  - Narrow exception handling in constellation.run_all() and scenario.create() to avoid silently
  swallowing genuine errors - Add typed error wrapping in CoverageStats properties - Add missing
  PropagatorLOP to component mode propagator maps - Update session.pyi with create_facility,
  quick_report, report_rm stubs - Remove unused imports (warnings, Callable) from utils.py - Remove
  unreachable dead code in component/satellite.py - Extract shared MockATKConnection into
  conftest.py across 4 test files

- **connect**: Handle CMDRESULT with empty m_vectData in send()
  ([`ce0c69c`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/ce0c69c59b100b9f7ebc05651c5207ce5b3a933d))

atkConnect() can return a CMDRESULT SWIG object whose m_vectData is empty (e.g. when ATK returns
  "NACK"). The previous code called result_to_list() which returned [] for this case, causing the
  "if data:" check to be False and error detection to be silently bypassed. Now we check m_vectData
  directly and handle str/list/empty cases explicitly, ensuring error responses are always detected
  and raised as ATKCommandError.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **connect**: Make SatelliteBuilder available at runtime
  ([`88e958b`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/88e958b20f430b3f852cd72c61ca151471cb0b87))

SatelliteBuilder was imported inside TYPE_CHECKING block, making it unavailable when
  _satellite_builder_factory() was called at runtime, causing NameError when calling
  atk.create_satellite().

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

- **connect**: Remove resolve_path from send() to fix command format
  ([`cbded16`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/cbded1644cb92404ae2c5438211e90dfe6becbf5))

resolve_path() was converting '/' to '*/' in send(), corrupting ATK Connect commands. For example,
  'New / Scenario MyScenario' became 'New */ Scenario MyScenario' which ATK rejects with NACK.

All callers already pass correct ATK path formats: - '/' for New commands (root path) - '*' for
  scenario-level commands (wildcard) - '*/Satellite/Sat1' for object-specific commands (full path)

The resolve_path normalization was both redundant and harmful.

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Continuous Integration

- 添加 GitHub Actions CI、自动发版和文档部署工作流
  ([`9622c9a`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/9622c9a64dcafb82498c1b433f6a815af2f72def))

配置 python-semantic-release 基于 conventional commits 自动计算 版本号、生成 changelog、创建 GitHub Release（含
  wheel/sdist 产物）； CI 矩阵测试 Python 3.9-3.12；push to master 自动部署 GitHub Pages。

### Documentation

- Update README structure to reflect src/vendored layout
  ([`3a245d7`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/3a245d7da91ad39f2983e8516d6d6294c9c3593f))

- 全面更新项目文档以反映当前 API 状态
  ([`7e40b3e`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/7e40b3e0f494ff5bda45b451122d43026b22dbcb))

重写 PLAN.md 为项目路线图；更新 README.md 项目结构和 API 参考； 补充 FacilityBuilder/SensorBuilder/ReportResult 文档；扩展 ATK
  命令 参考（新增 SetPosition、Define、Point、SetConstraint 等 12+ 命令）； 添加地面站/传感器/TLE/报告示例和故障排查条目。

- 将所有源码注释翻译为中文
  ([`1f484bf`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/1f484bf890360a3c582526b9238ed3f5de5530ad))

- 核心模块（atk/）：异常类、工具函数 - Connect
  模式（atk/connect/）：session、scenario、satellite、mcs、reports、coverage、constellation - Component
  模式（atk/component/）：session、scenario、satellite、mcs、reports - 示例代码（examples/）：霍曼转移、星座覆盖 -
  测试代码（src/tests/）：utils、session、scenario、satellite、mcs

涉及 docstrings、行内注释、段落分隔注释及示例 print() 输出。

- 添加 CLAUDE.md 并忽略 .claude 目录
  ([`9c17c18`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/9c17c18cee6715c4a272c2ebf5ba6197f19a8f7e))

- 新增 CLAUDE.md 作为 Claude Code 的项目引导文档 - 将 .claude/ 添加到 .gitignore

- 重构文档，突出 SDK 接口并修正官网链接
  ([`5415ae1`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/5415ae1f097d50bf50ff594c467db7d49e5e078a))

- 重构 Connect/Component 模式文档，重点介绍 SDK 接口而非原生接口 - 添加底层依赖章节，指向 ATK 官方文档 - 修正 ATK 官网链接为 osredm.com -
  添加项目定位说明，明确为第三方二次开发库 - 排除 site/ 目录到 .gitignore

Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>

### Features

- Initial atk-python-sdk — Connect + Component mode SDK
  ([`e331465`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/e331465cf90a1902982f1e2bdee1baaa9a685517))

Add high-level Python SDK for ATK (Analytical Toolkit):

- vendored/: ATK-provided SWIG bindings (ATKConnectModule.py + native DLLs) These are THE core ATK
  secondary development interface files.

- src/atk/connect/: Connect mode SDK — TCP to running ATK instance. ScenarioBuilder,
  SatelliteBuilder, McsBuilder, CoverageBuilder, WalkerBuilder, ReportResult with DataFrame export.

- src/atk/component/: Component mode SDK — direct DLL load, no ATK GUI. ComponentSession,
  IScenario/ISatellite wrappers, IVADriverMCS builder.

- src/tests/: 51 passing unit tests (pytest).

- examples/: Hohmann transfer, Walker constellation coverage (both Connect and Component modes).

Install: pip install -e .

- **connect**: Add FacilityBuilder/SensorBuilder, fix Save command format and satellite state
  methods
  ([`87ebb56`](https://github.com/ouyangjiahong26/atk-python-sdk/commit/87ebb563cb0e907c3c46c0a29000883c9214e7c5))

- Add FacilityBuilder with create, set_position(Geodetic), set_color - Add SensorBuilder with
  create, define_conical, point_fixed_euler, set_range_constraint - Add
  SatelliteBuilder.set_state_tle() for TLE-based satellite creation - Add Animate Reset after all
  SetState calls (matching reference code) - Add propagator validation for SetState
  Classical/Cartesian - Fix Save/SaveAs/Load command format to match ATK docs (Save / * not Save
  */Scenario/...) - Update create_scenario.py example with facility/sensor workflow
