# 代码职责与扩展方向

## 当前结构

```text
app/
  main.py              创建 FastAPI 应用、装配路由
  core/config.py       环境配置的唯一读取入口
  api/router.py        汇总 HTTP 路由
  api/routes/          health 与学习示例
  schemas/             请求与响应模型
tests/                 对外行为测试
scripts/               本地工具与开发启动
docs/                  环境、架构、学习及服务器说明
```

请求流向是：Uvicorn 接收 HTTP → FastAPI 找到路由 → Pydantic 校验输入 →
路由调用处理函数 → 响应模型约束输出 → 返回 JSON。
例如 `POST /examples/echo` 的输入输出在 `app/schemas/examples.py`，处理在
`app/api/routes/examples.py`。字符串长度按 Python `len` 计算。

目前没有持久化数据，也没有跨请求共享的业务状态。配置在创建应用时读取；
`create_app(settings)` 允许测试明确注入配置，避免依赖个人 `.env`。

## 有需求时再增加的模块

| 实际出现的职责 | 建议位置 | 边界 |
|---|---|---|
| 业务规则、多个接口共享的业务操作 | `app/services/` | 不处理 HTTP Request/Response |
| SQLAlchemy engine、会话及 ORM 模型 | `app/db/` | 管理持久化资源和表映射 |
| 数据库版本演进 | `migrations/` | Alembic 迁移；不在路由中临时建表 |
| 多个业务流程需要复用的数据库查询 | `app/repositories/` | 真正需要复用时引入，不强制一表一层 |
| 部署配置 | `deploy/` | 学到服务器阶段再引入 |

路由负责 HTTP 参数、状态码和调用；service 负责规则；数据库模块负责持久化。
ORM 模型与 HTTP schema 各自维护边界，不把数据库内部字段直接作为对外响应。
先保持简单的同步处理；学习异步时说明阻塞 I/O 与异步驱动的区别，再决定是否迁移。

## 变更时维护什么

新增接口时更新路由、必要 schema 与行为测试；只有导航或模块责任变化才改本文。
新增配置时更新 `config.py`、`.env.example` 和环境说明。
新增模块时提供简短职责说明，只有出现新的维护边界才增加局部 `AGENTS.md`。
不为了目录齐全预建空的 service、repository、数据库或部署框架。
