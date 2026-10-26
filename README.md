# FastAPI Learning Lab

这是一个以学习为目的、可以持续维护的 Python 后端项目。当前先跑通“HTTP 请求 → 路由 →
数据校验 → JSON 响应”，并演示静态文件、模板、直接 HTML 与文件下载。

## 快速开始（Windows PowerShell）

在本目录运行。首次安装会联网下载工具、Python 和依赖，后续可重复执行：

```powershell
.\scripts\bootstrap.ps1
.\scripts\dev.ps1
```

浏览器打开 <http://127.0.0.1:8000/demo>，逐个体验页面中的五种响应方式。
接口调试可打开 <http://127.0.0.1:8000/docs>，点击 **Try it out** 调用接口。
在终端按 `Ctrl+C` 停止服务。默认只监听本机。

若 PowerShell 阻止运行脚本，可只对这一次进程使用：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1
```

首次安装同理，将脚本名改成 `bootstrap.ps1`；不需要修改系统执行策略。

## 当前提供

| 接口 | 用途 |
|---|---|
| `GET /` | 查看应用名称、环境和文档入口 |
| `GET /health` | 确认应用能响应；目前不检查数据库 |
| `POST /examples/echo` | 发送 `{"message":"你好"}`，观察类型校验和响应模型 |
| `GET /docs` | FastAPI 自动生成的交互接口文档 |
| `GET /demo` | 模板生成的学习页面，包含 JSON 表单、图片和演示链接 |
| `GET /static/...` | 按相对路径提供图片、CSS 和 JavaScript |
| `GET /demo/html` | 直接返回 HTML 字符串 |
| `GET /demo/download` | 下载固定的调用映射文本文件 |

建议先读 [网页响应练习](docs/web-demo.md)，再对照代码中的中文调用映射注释。

可以用另一个 PowerShell 终端试一下：

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/examples/echo `
  -ContentType 'application/json; charset=utf-8' `
  -Body ([System.Text.Encoding]::UTF8.GetBytes('{"message":"你好，FastAPI"}'))
```

## 环境与常用命令

Python 版本由 `.python-version` 固定，依赖声明在 `pyproject.toml`，精确依赖由 `uv.lock` 固定。
安装位置、配置方法、恢复和新增依赖见 [环境说明](docs/setup.md)。

```powershell
.\scripts\uv.ps1 run python --version
.\scripts\uv.ps1 run pytest
.\scripts\uv.ps1 run ruff check .
.\scripts\uv.ps1 run ruff format --check .
```

以上测试和代码检查就是当前的轻量验证流程。纯文档修改只需核对命令、路径和实际行为。

## 下一步与维护入口

- [文档地图](docs/README.md)：按任务找到负责说明的文档。
- [学习路线](docs/learning.md)：Python → HTTP → FastAPI → 数据库 → 部署。
- [架构与扩展位置](docs/architecture.md)：知道每项代码该放在哪里。
- [Agent 入口](AGENTS.md)：后续由 Agent 协作维护时的导航与约定。

目前没有接入数据库、账号系统或远程服务器；后续在实际练习中逐步实现。
