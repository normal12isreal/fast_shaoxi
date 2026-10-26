# 本地数据库

SQLite 文件默认是 `data/site.sqlite3`，应用启动自动执行 Alembic `upgrade head`。
也可以在项目根运行 `scripts/uv.ps1 run --locked python -m scripts.migrate`。
迁移只负责表结构，ORM 默认值由 `app/db/models.py` 提供。

| 表 | 归属与用途 |
|---|---|
| users | 小写用户名、Argon2 密码哈希 |
| login_sessions | 用户、随机令牌的 SHA-256 哈希、七天到期时间 |
| rag_records | 用户、本次问题、处理状态、公开结果及安全错误提示 |
| conversations | 用户、标题、历史摘要、摘要边界 |
| messages | 所属对话、角色、原始正文、完成或失败状态 |

删除对话时由外键级联删除消息。
所有记录查询都限定当前用户；未登录无法枚举记录。会话 Cookie 为 HttpOnly、SameSite=Lax，
退出删除服务端会话。HTTPS 部署要设置 `COOKIE_SECURE=true`。
携带登录 Cookie 的写请求需发送同源 Origin（浏览器自动发送）；脚本可显式设置，
例如 `Origin: http://127.0.0.1:8000`。不开放跨站 Cookie 写操作。

模型调用期间没有数据库写事务。调用结束后开启短事务保存结果；
失败、超时和中断明确记录，不编造答案。进程重启时将遗留 processing/pending 标为失败或中断，
不自动重放付费调用。

新增表结构时添加新的迁移版本，不改动已应用的历史迁移。
测试使用临时 SQLite，并核对迁移与 ORM 一致性。未来再单独学习 PostgreSQL 迁移。
备份时先停服务，再备份整个 `data/`，不要在写入时只拷贝主数据库文件。
