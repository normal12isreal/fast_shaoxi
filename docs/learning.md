# 学习路线

当前已具备项目环境、应用骨架、健康检查、输入输出示例和基础测试。
下面的数据库与部署内容是后续练习，不代表已经实现。

| 阶段 | 学习重点 | 做到什么算完成 |
|---|---|---|
| 1. Python 基础 | 变量、字符串、列表/字典、条件循环、函数、模块、异常、类型标注 | 能解释 echo 示例每一行，自己写函数及简单测试 |
| 2. HTTP 与 FastAPI | 方法、路径、查询参数、JSON、状态码、Pydantic | 能加一个带参数校验的接口，在 `/docs` 调用并解释 422 |
| 3. 小型业务 | 以待办事项为例，增加新增/查询/修改/删除与业务规则 | 路由和规则职责清楚，失败场景有测试；内存存储需说明重启丢失 |
| 4. SQLite 数据库 | 表、主键、SQL、事务，之后引入 SQLAlchemy 与 Alembic | 重启后数据仍存在；能解释迁移与事务回滚 |
| 5. PostgreSQL | 服务进程、连接地址、凭据、连接池、备份 | 能切换数据库，独立测试数据与个人学习数据，验证备份恢复 |
| 6. 服务器部署 | Linux、进程、端口、环境变量、日志、反向代理、HTTPS | 能部署并检查健康、读取日志、重启服务；之后再考虑 Docker |

建议下一次从阶段 1 或 2 开始，由你写一个小改动，再一起解释执行过程与验证结果。
不必一次性引入登录、消息队列、Redis、微服务和复杂部署平台。

## 第一个练习

1. 启动服务并打开 `/docs`，调用 `GET /health`。
2. 调用 `POST /examples/echo`，依次发送中文、空字符串和数字，观察成功与 422 响应。
3. 从 schema 找出长度限制，把上限由 200 改为 100，并同步相应边界测试。
4. 运行根 README 的验证命令，读懂它们分别检查什么，再做一次本地提交。

## 官方资料

- [Python 中文教程](https://docs.python.org/zh-cn/3.13/tutorial/)
- [FastAPI 教程](https://fastapi.tiangolo.com/tutorial/)
- [SQLAlchemy 教程](https://docs.sqlalchemy.org/en/20/tutorial/)（数据库阶段）
- [PostgreSQL 教程](https://www.postgresql.org/docs/current/tutorial.html)（服务型数据库阶段）
