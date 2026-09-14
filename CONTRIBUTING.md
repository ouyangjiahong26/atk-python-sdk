# 贡献指南

## 交流语言

本仓库全面使用中文：代码注释、提交信息、issue、PR、文档均用中文。

## AI 参与的贡献

如果 issue、PR 或其中的代码由 AI 工具生成或主要参与编写，**必须在标题最前面标注 `[AI Generated]`**，例如：

```
[AI Generated] 补充 Component 模式地面站支持
```

## 开发环境

```bash
uv sync --dev                      # 安装开发依赖
uv run pytest                      # 运行全部测试
uv run pytest src/tests/component/ # 只跑某个模块的测试
uv sync --extra docs && uv run mkdocs serve   # 本地预览文档
```

测试全部使用 `unittest.mock` 模拟 SWIG 对象，不需要安装 ATK 即可运行。

## 提交信息规范

仓库使用 [python-semantic-release](https://python-semantic-release.readthedocs.io/) 自动计算版本号并发布，提交信息需遵循约定式提交格式：

```
<type>: <中文描述>
```

| type | 作用 |
|------|------|
| `feat` | 新功能，触发次版本号（minor）升级 |
| `fix` / `perf` | 修复 / 性能优化，触发修订号（patch）升级 |
| `refactor` / `docs` / `test` / `build` / `ci` / `chore` | 不触发版本升级 |

发布流水线会依据提交信息更新 `CHANGELOG.md`、打 tag 并创建 GitHub Release。

## 代码约定

- 源码位于 `src/atk/`（`connect/` 与 `component/` 两个模式），测试位于 `src/tests/`。
- 两种模式共享 `atk.exceptions`（以 `ATKError` 为根的异常层次）和 `atk.utils`。
- 新增构建器（Builder）时，接口命名与已有构建器保持直觉一致，docstring 用中文。
- Connect 模式各子模块在 import 时通过 `_patch_connection()` 向 `ATKConnection` 注入工厂方法，不要删除 `connect/__init__.py` 中的相关导入。
- `src/vendored/` 中 ATK 官方提供的绑定与二进制不要修改（`ATKComponentPythonModule.py` 的测试替身除外）。
