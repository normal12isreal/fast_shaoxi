# Python 与依赖环境

## 选择与安装位置

采用 Python 3.13 系列，便于统一练习环境；准确补丁版本记录在根 `.python-version`。
uv 是项目的 Python 和依赖管理工具，不要求预装 Python。

| 位置 | 内容 | 是否进入 Git |
|---|---|---|
| `.tools/uv/` | 固定版本 uv 可执行文件 | 否 |
| `.runtime/python/` | 项目专用 CPython 发行版 | 否 |
| `.venv/` | 项目虚拟环境与安装的库 | 否 |
| `.uv-cache/` | Python 与依赖下载缓存 | 否 |
| `.tools/tmp/` | 安装及运行命令的临时文件 | 否 |
| `.python-version` | Python 补丁版本选择 | 是 |
| `pyproject.toml` | 依赖声明与检查工具配置 | 是 |
| `uv.lock` | 所有依赖的精确版本与校验信息 | 是 |
| `scripts/toolchain.json` | uv 版本与官方压缩包校验值 | 是 |

`scripts/uv.ps1` 仅在命令执行期间设置项目路径，结束后恢复当前进程环境。
它禁止安装时注册 Python、创建全局 Python 命令或使用用户级 Python 包。
不修改系统 PATH、注册表、全局依赖与 PowerShell profile。
虚拟环境引用本项目内的 Python，因此整个目录移动后应重新执行 bootstrap 重建环境。
目前引导脚本针对 Windows x64；Linux 部署时再增加对应平台的入口。

路径控制依据 [uv 官方存储说明](https://docs.astral.sh/uv/reference/storage/)；
Python 来自 uv 使用的 [python-build-standalone 发行版](https://docs.astral.sh/uv/guides/install-python/)。

## 当前依赖职责

- FastAPI：HTTP 路由和自动接口文档。
- Uvicorn：运行 ASGI 应用的服务器；standard 扩展支持开发热重载。
- Pydantic：请求、响应模型及数据校验。
- Jinja2：将 `app/templates/` 中的 HTML 模板与页面数据合成为 HTML 响应。
- pytest、HTTPX2：测试运行器与内存中的 HTTP 接口测试。当前 Starlette TestClient
  使用 [HTTPX2](https://starlette.dev/testclient/)。
- Ruff：基础代码检查与格式化。

- Markdown-it：安全渲染公开 README，禁用原始 HTML。
- SQLAlchemy、Alembic：SQLite ORM 与表结构迁移，不安装远程数据库服务。
- pwdlib 与 Argon2：密码哈希与验证。

## 应用配置

页面和本地账号可直接启动；RAG 查询需要原项目已有数据和模型凭据。
复制根 `.env.example` 为 `.env` 后，`scripts/dev.ps1` 通过 uv 加载。
直接运行 uvicorn、迁移脚本时须自行设置环境变量或使用 uv 的 `--env-file .env`。
测试使用临时数据库和模拟模型，不读取个人 `.env`。

`RAG_PROJECT_DIR` 默认同级 `student-handbook-rag`；网站只引用原代码和数据。
`DASHSCOPE_API_KEY`、`DASHSCOPE_BASE_URL` 可覆盖原 RAG 的私有本地凭据。
真实密钥只放本机环境或被忽略的 `.env`，不放教程、聊天或 Git。
`HANDBOOK_DATABASE_PATH` 默认 `data/site.sqlite3`，`COOKIE_SECURE=true` 用于 HTTPS。
助手独立模型名称由 `ASSISTANT_MODEL` 指定，默认 `qwen3.7-plus`。

## 日常安装与恢复

统一从项目根运行，使用项目包装脚本：

```powershell
# 依据锁文件恢复全部依赖，包含开发工具
.\scripts\uv.ps1 sync --locked
# 添加实际需要的库，同时更新 pyproject.toml 与 uv.lock
.\scripts\uv.ps1 add sqlalchemy
# 只用于开发的库
.\scripts\uv.ps1 add --dev pytest-cov
# 删除不再使用的库
.\scripts\uv.ps1 remove sqlalchemy
# 查看项目真实 Python 路径
.\scripts\uv.ps1 run python -c "import sys; print(sys.executable); print(sys.base_prefix)"
```

以上 add/remove 是操作示例，只在真正需要对应库时执行。精确版本以锁文件为准。
不要使用系统 `pip install` 或 `--system`。通常不需要手动激活虚拟环境。
新机器上直接执行根 README 的 bootstrap；它会校验 uv 下载内容并按锁文件恢复。
升级 Python 或依赖时显式更新版本与锁文件，运行测试后一起提交，不在启动时自动升级。
