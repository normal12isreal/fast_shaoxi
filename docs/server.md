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

## 后续部署时逐项补齐

1. Linux 上重建项目环境，使用锁定依赖；Windows 虚拟环境不能直接复制过去。
2. 正式运行移除 `--reload`，将应用作为进程交给 systemd 或容器管理。
3. 明确监听地址、防火墙和外部访问方式，配置反向代理及 HTTPS。
4. 通过环境变量提供数据库连接与凭据，保存日志，验证重启与备份恢复。
5. 需要时区分存活检查与包含数据库连接的就绪检查。

到该阶段再新增 `deploy/` 和实际部署命令。当前脚本是本机开发入口，尚未部署到远程服务器。
