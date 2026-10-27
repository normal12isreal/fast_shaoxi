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

根目录的 `Dockerfile` 已在本机 Docker Desktop 完成构建和启动检查，并部署到 AWS。
本地检查覆盖页面、健康接口、SQLite 完整性、RAG 导入及索引文件存在性；
远端额外完成了一次真实 RAG 提问，返回 HTTP 200。
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

以下是在本机构建和启动的命令；Docker Desktop 需要处于 Linux 容器模式：

```powershell
# 在项目根目录构建，目标对应当前 AWS x86_64 实例。
docker build --platform linux/amd64 -t fastapi-rag:trial .

# 先复制 .env.example 为 .env 并填写百炼的两个环境变量。
# 不要将本机 Windows 数据库或 RAG 绝对路径写进这个容器环境文件。
docker run -d --name fastapi-rag --env-file .env -p 127.0.0.1:8000:8000 fastapi-rag:trial
```

`EXPOSE 8000` 不会自动发布端口；上述映射只允许本机访问 `http://127.0.0.1:8000/`，
健康检查地址为 `http://127.0.0.1:8000/health`。在 AWS 上对外提供 HTTP 时，
可改用 `-p 80:8000` 并让安全组允许 TCP 80，再通过服务器公网地址访问。
该命令在执行它的电脑运行容器，不会自动上传或部署到 AWS。
当前只有 Dockerfile，没有 Compose、反向代理或 HTTPS 配置。

同名容器已经创建后，用 `docker start fastapi-rag` 再次启动，
用 `docker stop fastapi-rag` 停止，用 `docker logs --tail 50 fastapi-rag` 查看日志。
不要重复执行同名 `docker run`；它会报容器名称已被占用。

## 当前 AWS 实验部署

实例 `normal_sc_ray` 位于 `us-east-2`，公网地址为 <http://18.220.233.65/>。
镜像使用 Docker Hub 私有仓库 `normal12isreal/fastapi-rag:latest`。
当前容器名为 `fastapi-rag`，将服务器 `80` 映射到容器 `8000`，
设置 `--restart unless-stopped`，Docker 服务随系统启动。
容器日志最多保留 3 个 10 MB 文件。

模型凭据保存在服务器 `/home/ubuntu/fastapi-rag/dashscope.local.json`，权限为 `600`，
只读挂载到 `/app/rag/.runtime/dashscope.local.json`。
拉取镜像使用的临时 Docker Hub 登录配置已在拉取结束后清理，不放入镜像或 Git。
数据库按实验要求仍保存在容器内，删除、重建容器前需要自行保留想要的数据。

实例实际关联安全组为 `launch-wizard-1`（`sg-0903f77d85c7b21dc`）。
网页曾经超时的原因是该组只有 SSH 22 入站；补上 HTTP TCP 80、来源 `0.0.0.0/0` 后，
已从本机外网验证 `/`、`/api-docs`、`/health` 返回 HTTP 200。
当前使用 HTTP；尚未配置域名和 HTTPS。

在服务器终端查看和控制容器：

```bash
docker ps --filter name=fastapi-rag
docker logs --tail 50 fastapi-rag
docker stop fastapi-rag
docker start fastapi-rag
```

AWS 管理工具和登录方式见 [项目专用 AWS 工具](setup.md#aws-项目专用工具)。

## 后续正式部署时按需补齐

1. Linux 上重建项目环境，使用锁定依赖；Windows 虚拟环境不能直接复制过去。
2. 正式运行移除 `--reload`，将应用作为进程交给 systemd 或容器管理。
3. 明确监听地址、防火墙和外部访问方式，配置反向代理及 HTTPS。
4. 通过环境变量提供数据库连接与凭据，保存日志，验证重启与备份恢复。
5. 需要时区分存活检查与包含数据库连接的就绪检查。

`scripts/dev.ps1` 仍是本机开发入口；修改代码不会自动更新远端容器，需要重新构建、上传并部署。
