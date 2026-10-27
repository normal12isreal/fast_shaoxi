# 学生手册 RAG 网站

用 FastAPI 学习网页、HTTP 接口、数据库和模型调用。网站自带
[学生手册 RAG](https://github.com/normal12isreal/shaoxing_university_handbook_rag) 的运行代码和现有索引，
统一放在 `rag/`，无需另一个仓库目录或重新生成向量。

## 本地启动

在本目录运行 PowerShell，Python、依赖和缓存都保留在项目内：

```powershell
.\scripts\bootstrap.ps1
.\scripts\dev.ps1
```

打开 <http://127.0.0.1:8000/>，面向调用者的接口使用教程在 `/api-docs`。
开发调试用的 FastAPI 自动文档仍在 `/docs`。按 Ctrl+C 停止。
如脚本执行受限，可用 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1`。

## 当前功能

首页 `/`、安装教程 `/guide`、登录 `/login`、注册 `/register`、个人中心 `/account`
均已可用。首页公开单次问答；安装教程公开，安装助手及历史对话需要登录。
助手只帮助安装、运行原 RAG，支持新建对话、恢复历史和较早上下文的摘要压缩。
原消息始终完整保留，失败或超时会标明状态。
网站默认使用项目内 `rag/`，可通过 `RAG_PROJECT_DIR` 显式指定其他位置；相对路径以项目根为基准。
教程与首页读取 `rag/README.md`，安装补充资料在 `knowledge/installation.md`。
运行资料和来源说明见 [RAG 导航](rag/AGENTS.md)。

可复制 `.env.example` 为 `.env` 调整配置，`scripts/dev.ps1` 会读取它。
首次启动自动创建 `data/site.sqlite3` 并应用迁移。账号采用用户名和密码，不接邮箱。
登录后首页问答才保存到个人记录；匿名请求不保存问答历史。
数据库和密码哈希不进入 Git，详见 [数据库说明](docs/database.md)。

公开 `POST /api/rag/ask` 只接收 `{"question":"申请国家奖学金需要满足哪些条件？"}`，
不需要账号或 API Key。已有索引随项目提供；网站调用模型需要维护者配置百炼凭据。
可以在 `.env` 中提供 `DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL`，或使用本机私有文件
`rag/.runtime/dashscope.local.json`（格式参考 `rag/config/dashscope.example.json`）。
本机迁入的凭据和后续查询缓存均不进入 Git，原仓库保持不变。
外部程序示例：

```powershell
.\scripts\uv.ps1 run --locked python scripts/ask.py "申请国家奖学金需要满足哪些条件？"
```

网站等待最多 180 秒，示例和浏览器等待 210 秒。忙碌返回 503，上游失败 502，超时 504。
网站使用单进程、一个 RAG 执行名额；超时后底层线程结束前仍保持忙碌，不自动重发。

## 验证与阅读入口

```powershell
.\scripts\uv.ps1 run --locked pytest
.\scripts\uv.ps1 run --locked ruff check .
.\scripts\uv.ps1 run --locked ruff format --check .
```

- [文档地图](docs/README.md)：按问题找说明。
- [网站调用关系](docs/website.md)：页面、JSON 接口和处理模块。
- [架构阅读顺序](docs/architecture.md)：从入口沿一条请求往下看。
- [环境说明](docs/setup.md)：项目内工具与依赖。
- [服务器说明](docs/server.md)：监听地址、端口与 Docker 实验镜像配置。
- [Agent 导航](AGENTS.md)：维护职责。

本轮只在本地开发，不推送、不部署。
