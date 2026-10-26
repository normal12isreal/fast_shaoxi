# 文档地图

按当前问题阅读对应文档，不需要每次读完整套资料。

| 要解决的问题 | 直接说明 | 对应实现 |
|---|---|---|
| 如何启动、有哪些可用接口 | [项目入口](../README.md) | `app/main.py`、`app/api/routes/` |
| JSON、模板、图片、HTML 与下载怎样串起来 | [网页响应练习](web-demo.md) | `app/pages/`、`app/templates/`、`app/static/` |
| Python 放在哪里、怎么装库与配置 | [环境说明](setup.md) | `scripts/`、`pyproject.toml`、`uv.lock` |
| 一项改动该放在哪个模块 | [架构职责](architecture.md) | `app/`、`tests/` |
| 先学什么、下一步做到什么程度 | [学习路线](learning.md) | 当前阶段对应的练习代码 |
| Uvicorn、端口、服务器与后续部署 | [服务器说明](server.md) | `scripts/dev.ps1` |
| Agent 进入项目后怎样维护 | [根 AGENTS.md](../AGENTS.md) | 各职责目录的 `AGENTS.md` |

HTTP 接口的准确字段和响应以运行中的 `/docs` 与 schema 代码为准，文档不再复制一份契约。
