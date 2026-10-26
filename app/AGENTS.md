# 应用代码职责

修改前按需读取 [架构说明](../docs/architecture.md)。

- `main.py`：应用创建、路由组装和根接口；不堆业务逻辑。
- `core/config.py`：环境配置和默认值；新增配置同步 `.env.example` 与环境说明。
- `api/router.py`：汇总路由；`api/routes/` 中每个文件负责一个明确主题。
- `schemas/`：请求、响应及字段约束。业务规则出现后放入对应 service，不藏在 schema 中。
- FastAPI 的 OpenAPI 是 HTTP 契约的直接展示；新增行为在 `tests/` 中验证，不手工复制整套接口清单。
- 尚无数据库层；需要持久化时按架构文档新增 `app/db/`，不要直接在路由里拼 SQL。
- 业务实现与示例的区别要明确；`examples` 下的接口是学习演示。
