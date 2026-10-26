# 应用代码职责

修改前按需读取 [架构说明](../docs/architecture.md)。

- `main.py`：直接用 `app = FastAPI()` 创建应用，再注册路由与静态目录。
- 当前以学习响应方式为主；保留可运行示例，避免加入无实际用途的配置层与工厂。
- `api/router.py`：汇总路由；`api/routes/` 中每个文件负责一个明确主题。
- 页面与文件响应见 [pages/AGENTS.md](pages/AGENTS.md)。`templates/` 负责 HTML 模板，
  `static/` 负责浏览器脚本、样式与图片，`resources/` 保存固定下载文件。
- 静态目录挂载在 `main.py`；保持 URL、函数、文件映射的中文注释与实现同步。
- `schemas/`：请求、响应及字段约束。业务规则出现后放入对应 service，不藏在 schema 中。
- FastAPI 的 OpenAPI 是 HTTP 契约的直接展示；新增行为在 `tests/` 中验证，不手工复制整套接口清单。
- 尚无数据库层；需要持久化时按架构文档新增 `app/db/`，不要直接在路由里拼 SQL。
- 业务实现与示例的区别要明确；`examples` 下的接口是学习演示。
