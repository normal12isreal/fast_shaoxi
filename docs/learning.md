# 用当前网站学习后端

原来的 echo、下载和占位图片练习已替换为实际问答网站。
Python、FastAPI、SQLite、账号及多轮助手已经接通；PostgreSQL、Linux 和真实部署留待后续。

| 阅读顺序 | 直接看哪里 | 可观察的行为 |
|---|---|---|
| 1. 应用装配 | `app/main.py`、`pages/routes.py` | 页面路由、API 路由和静态目录怎样注册 |
| 2. 网页到 JSON | `static/home.js`、`api/routes/rag.py`、`schemas/rag.py` | 提交问题、422 校验、答案与引用 |
| 3. 等待与并发 | `services/execution.py`、`services/rag.py` | 工作线程、限额、503/504 和健康检查 |
| 4. 数据库与账号 | `db/`、`migrations/`、`services/auth.py` | 短事务、密码哈希、Cookie 和个人记录 |
| 5. 多轮模型调用 | `services/assistant.py`、`assistant_context.py`、`qwen.py` | 持久历史、摘要、最近六轮和失败记录 |
| 6. 后续服务器阶段 | `docs/server.md` | Linux 进程、PostgreSQL、反向代理、HTTPS 和备份 |

建议一次跟踪一条请求：浏览器操作 → 路由 → schema/身份 → 处理模块 → 数据库或模型 → 响应。
可先在 `/docs` 比较非空问题、空白问题与超过 500 字符的问题，再阅读相应测试。
自动测试默认不调用真实模型，慢调用测试约等待 20 秒；真实模型调用可能产生费用，按需单次验证。

维护时沿 [文档地图](README.md) 找直接职责，不必先掌握所有文件。
后续扩展先围绕现有网站增加实际能力，暂不引入消息队列、Redis 或复杂服务拆分。
