# 绍兴大学学生手册 RAG 网站

基于 FastAPI 的学生手册问答网站，包含网页和 HTTP API。RAG 运行代码、学生手册分块及已有向量索引都随项目提供，不需要另外下载 RAG 仓库或重新生成索引。

- 学生手册问答与来源引用。
- 账号注册、登录、个人问答记录。
- RAG 安装教程和登录后可用的安装助手。
- 面向外部程序的 JSON API。

项目基于 [学生手册 RAG](https://github.com/normal12isreal/shaoxing_university_handbook_rag)，上游来源与文件校验记录在 [rag/upstream.json](rag/upstream.json)。这是学习与实验项目，具体规定仍以学校正式文件为准。

## 使用 Docker 运行

先安装并启动 Docker；Windows 的 Docker Desktop 使用 Linux 容器模式。发布镜像面向 `linux/amd64`。

### 1. 配置自己的 API Key

下载 [docker.env.example](docker.env.example)，复制并改名为 `docker.env`，填写自己的阿里云百炼（DashScope）API Key：

```dotenv
DASHSCOPE_API_KEY=替换为你自己的API_Key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
COOKIE_SECURE=false
```

如果已经克隆仓库，可在 PowerShell 中复制模板：

```powershell
Copy-Item docker.env.example docker.env
```

Linux/macOS 对应为 `cp docker.env.example docker.env`。然后使用文本编辑器修改 `docker.env`。

Key 必须与上面的百炼服务地址匹配，并能调用项目配置的文本生成、Embedding 和 Rerank 模型；模型配置位于 [rag/config/](rag/config/)。模型调用费用由该 Key 的持有者承担。

镜像不包含维护者的 API Key、现有账号数据库或问答历史。`docker.env` 留在运行者自己的电脑上，不要上传 GitHub；仓库已经忽略这个文件。启动时直接读取配置，不弹出输入窗口。

### 2. 下载镜像并启动

从 [最新 Release](https://github.com/normal12isreal/fast_shaoxi/releases/latest) 下载 `fast-shaoxi-linux-amd64.tar.gz`。
将它和 `docker.env` 放在同一个目录，打开终端执行：

```bash
docker load -i fast-shaoxi-linux-amd64.tar.gz
docker run -d --name fast-shaoxi --env-file docker.env -p 127.0.0.1:8000:8000 fast-shaoxi:latest
```

镜像加载成功后无需重新构建或登录镜像仓库。打开 <http://127.0.0.1:8000/>。第一次启动自动创建空数据库，可以自行注册账号。

| 地址 | 用途 |
|---|---|
| `/` | 学生手册问答首页 |
| `/guide` | RAG 安装教程 |
| `/api-docs` | 面向调用者的接口教程 |
| `/docs` | FastAPI 自动接口文档 |
| `/health` | 应用存活检查 |

```bash
docker logs --tail 50 fast-shaoxi
docker stop fast-shaoxi
docker start fast-shaoxi
```

首次创建后用 `docker start` 重新启动，无需重复 `docker run`。当前示例将数据保存在容器内；停止、启动会保留数据，删除并重建容器会丢失账号和历史记录。需要备份或持久化时参阅 [数据库说明](docs/database.md)。

如需部署到服务器，将端口映射改为 `-p 80:8000`，并在服务器安全组中放行 HTTP 80；运行方式见 [服务器说明](docs/server.md)。公网长期使用时应配置域名与 HTTPS，HTTPS 下设置 `COOKIE_SECURE=true`。

## 调用 API

运行容器后可在 PowerShell 中调用：

```powershell
$body = @{ question = "申请国家奖学金需要满足哪些条件？" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/api/rag/ask -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($body)) -TimeoutSec 210
```

`POST /api/rag/ask` 只接收 `question`，调用者无需提交模型 Key；模型 Key 由运行容器的人配置。公开问答接口不要求登录，匿名问答不保存个人历史。

当前使用单进程、一个 RAG 执行名额；网站等待最多 180 秒，客户端建议等待 210 秒。忙碌返回 503，上游失败 502，超时 504，不自动重发付费请求。

## 从源码运行

```powershell
git clone https://github.com/normal12isreal/fast_shaoxi.git
cd fast_shaoxi
.\scripts\bootstrap.ps1
Copy-Item .env.example .env
# 编辑 .env，填写 DASHSCOPE_API_KEY 和 DASHSCOPE_BASE_URL，再启动：
.\scripts\dev.ps1
```

项目 Python、虚拟环境、工具和缓存都放在项目内，不依赖系统 Python。开发环境说明见 [docs/setup.md](docs/setup.md)。脚本执行受限时可使用 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1`。

自行构建镜像：

```bash
docker build --platform linux/amd64 -t fast-shaoxi:local .
docker run -d --name fast-shaoxi --env-file docker.env -p 127.0.0.1:8000:8000 fast-shaoxi:local
```

构建不会打包本机 `.env`、`docker.env`、`rag/.runtime/` 或 `data/`。已有 Linux 依赖由 `uv.lock` 安装，不复制 Windows 虚拟环境。

## 开发与文档

```powershell
.\scripts\uv.ps1 run --locked pytest
.\scripts\uv.ps1 run --locked ruff check .
.\scripts\uv.ps1 run --locked ruff format --check .
```

- [文档地图](docs/README.md)：按问题查找说明。
- [网站调用关系](docs/website.md)：页面、接口与处理模块。
- [架构说明](docs/architecture.md)：请求路径与职责边界。
- [数据库说明](docs/database.md)：账号、历史记录与迁移。
- [服务器说明](docs/server.md)：Docker、端口与部署。
- [Agent 入口](AGENTS.md)：项目维护约定。

## 许可证

项目代码使用 [MIT License](LICENSE)。RAG 上游许可证保留在 [rag/LICENSE](rag/LICENSE)。学生手册内容的权利归原发布方所有。
