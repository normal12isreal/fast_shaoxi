# 从本地服务到服务器

## 当前怎样运行

FastAPI 描述“请求进来后如何处理”，Uvicorn 负责监听端口、接收请求并调用应用。
`scripts/dev.ps1` 用 Uvicorn 加载 `app.main:app`，监听 `127.0.0.1:8000`，修改 `app/`
中的 Python 文件后自动重载。终端关闭或按 `Ctrl+C` 后服务停止。

`127.0.0.1` 表示本机；`8000` 是端口，不是数据库。
`/health` 只表示应用进程能处理请求，不能说明数据库或外部服务已经就绪。

当前必须保持单进程，不增加 Uvicorn workers。RAG 执行限额在本进程内；
阻塞计算在线程中运行，健康检查和页面无需等它完成。
网站问答等待 180 秒，浏览器和外部示例为 210 秒。未来 Nginx 的
`proxy_read_timeout` 至少设为 210 秒；keep-alive 不是问答执行超时。
HTTP 超时无法杀死 Python 线程，执行名额等真实调用结束才释放。
依据：[Nginx](https://nginx.org/en/docs/http/ngx_http_proxy_module.html#proxy_read_timeout)、
[Uvicorn](https://uvicorn.dev/settings/)。

端口冲突时可改用：

```powershell
.\scripts\dev.ps1 -Port 8001
```

随后访问 <http://127.0.0.1:8001/docs>。

## Docker 实验镜像

根目录的 `Dockerfile` 已准备好打包配置，目前尚未构建、运行或部署验证。
依赖安装方式参考 [uv 官方 Docker 说明](https://docs.astral.sh/uv/guides/integration/docker/)。

- 使用 Python 3.13，在镜像内按 `uv.lock` 创建 Linux `.venv`，不复制 Windows 虚拟环境。
- 将网站代码、模板、静态资源、数据库迁移、`knowledge/` 和 `rag/` 的已有索引一起复制。
- 按当前实验需求，将本地 `data/` 数据库一起放入镜像，不声明外部数据卷。
  新容器从构建时的数据副本开始；后续修改写在当前容器内，删除容器会丢失这些修改。
  构建前先停止本地开发服务，避免在数据库写入期间复制；包含已有 WAL，排除可重建的 SHM。
  从没有 `data/` 的源码构建也可以，应用启动时自动创建数据库。
- `.dockerignore` 排除本机工具、虚拟环境、Git、测试、`.env` 和 `rag/.runtime/`。
  模型凭据由运行环境提供 `DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL`，不嵌入镜像。
- 启动命令监听 `0.0.0.0:8000`，关闭 `--reload`，明确只启用一个 worker。

以下命令供审阅后手动执行，创建这些文件不代表已执行构建或启动：

```powershell
# 在项目根目录构建，目标对应当前 AWS x86_64 实例。
docker build --platform linux/amd64 -t fastapi-rag:trial .

# 先复制 .env.example 为 .env 并填写百炼的两个环境变量。
# 不要将本机 Windows 数据库或 RAG 绝对路径写进这个容器环境文件。
docker run -d --name fastapi-rag --env-file .env -p 80:8000 fastapi-rag:trial
```

`EXPOSE 8000` 不会自动发布端口；`-p 80:8000` 才把宿主机 80 端口转到容器 8000。
本机测试时访问 `http://127.0.0.1/health`；远程运行时用服务器公网地址替换本机地址，
并让 AWS 安全组允许 TCP 80。该命令在执行它的电脑运行容器，不会自动上传或部署到 AWS。
当前只有 Dockerfile，没有 Compose、反向代理或 HTTPS 配置。

## 后续部署时逐项补齐

1. Linux 上重建项目环境，使用锁定依赖；Windows 虚拟环境不能直接复制过去。
2. 正式运行移除 `--reload`，将应用作为进程交给 systemd 或容器管理。
3. 明确监听地址、防火墙和外部访问方式，配置反向代理及 HTTPS。
4. 通过环境变量提供数据库连接与凭据，保存日志，验证重启与备份恢复。
5. 需要时区分存活检查与包含数据库连接的就绪检查。

当前 `scripts/dev.ps1` 仍是本机开发入口；实际上传、部署和远程运行另行执行。
