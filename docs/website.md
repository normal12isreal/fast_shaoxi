# 网站调用关系

本轮顺序：页面与资料 → 公开问答 → 数据库与账号 → 多轮安装助手，每步验证后本地提交。

```text
浏览器 GET / 或 /guide
  → app/main.py 注册 pages/routes.py
  → services/knowledge.py 读取白名单公开资料
  → templates/*.html 生成页面
  → static/*.js 在后续阶段调用 JSON API
```

首页公开单次手册问答；安装页展示原 RAG 的教程，登录后才能使用多轮安装助手。
账号页面用于注册、登录和查看自己的手册问答记录。以上四个施工阶段已接通。
完整行为以路由、schema、测试和运行中的 `/docs` 为准。

公开问答的调用顺序：`static/home.js` 或外部程序 → `api/routes/rag.py`
→ `services/rag.py` → `services/execution.py` 的工作线程 → 原 `HandbookRAG.ask()`。
只传本次问题，不传历史；保留原库的默认检索、证据判断和复核。
输出通过 `schemas/rag.py` 筛选，内部文件路径、配置和记录路径不公开。

原代码从 `RAG_PROJECT_DIR` 引用，配置与索引通过 `.runtime/rag-view/` 下的目录链接读取；
Windows 使用 Junction，Linux 使用符号链接。没有复制数据，查询缓存写在网站目录。
原库的问答记录关闭，网站只保存登录用户的记录。
修改 RAG_PROJECT_DIR 后须停服务、检查两个目录链接指向并重新配置，不自动替换已有链接。

## 页面与接口

| 浏览器入口 | 调用的 JSON 接口 | 权限与行为 |
|---|---|---|
| `/` | `POST /api/rag/ask` | 公开；每次独立；登录时保存本人记录 |
| `/register`、`/login` | `POST /api/auth/register`、`login` | 用户名密码，注册后页面自动登录 |
| 所有页面的导航 | `GET /api/auth/me`、`POST /api/auth/logout` | 检查身份和退出 |
| `/account` | `GET /api/rag/records`、`/records/{id}` | 登录后分页查询自己的记录 |
| `/guide` | `POST/GET /api/assistant/conversations` | 教程公开；登录后新建、分页读取对话 |
| `/guide` | `GET/POST /api/assistant/conversations/{id}/messages` | 恢复原始历史、发送消息 |
| `/guide` | `DELETE /api/assistant/conversations/{id}` | 删除本人对话及消息；运行中返回 409 |
| `/api-docs` | 无 | 面向外部调用者：curl、PowerShell、Python 示例、返回结果与错误处理 |
| `/docs` | `/openapi.json` | 开发调试用的 FastAPI 自动接口清单，不在网站主导航展示 |

记录与对话每页可指定 `limit`、`offset`，范围见 `/docs`。
对话消息从最新一页向前读取，每页内部按发送顺序排列；页面提供“加载更早消息”。
无登录返回 401，访问他人的记录或对话返回 404，不暴露归属信息。

## 安装助手的上下文

`assistant_context.py` 维护职责和 32000 字符输入预算，`knowledge.py` 维护公开资料白名单。
每次发送职责、公开知识、已有摘要、当前对话已完成的近期问答和当前问题。
失败消息仍在网页历史中显示，模型历史只使用已完成的问答；失败后可手动重新提交。
新建对话不继承其他对话的任何消息或摘要。

超预算时，将较早的完整问答连同已有摘要交给千问压缩，保留最近六轮完整问答。
摘要和边界只在本轮成功后保存，网页继续显示全部原文。
压缩失败返回 502；六轮与当前问题仍超预算返回 422，提示缩短问题或新建对话。
这两种情况均保留失败原文，不静默裁剪近期内容。

千问客户端单次 HTTP 请求最多 60 秒、不自动重试；助手整体等待最多 180 秒。
每段对话只处理一条消息，运行中重复发送返回 409；全站助手同时最多两个模型任务，
超额返回 503。超时返回 504，迟到的结果不会伪装成成功回答写入历史。
助手没有执行工具，只提供原 RAG 的安装建议。

## 本轮验证

自动测试使用临时 SQLite 和模拟模型，覆盖输入校验、超过 20 秒的等待、健康检查并发、
忙碌与超时名额保留、账号隔离、分页、重启恢复、摘要保留原文和失败状态。
浏览器使用模拟模型核对匿名提问、账号、记录、对话恢复及新建对话，修复了短窗口下的聊天栏滚动。

实际只执行一次原 RAG 默认问答（约 18.4 秒，完整回答、两条引用）和一次千问两轮对话验证
（约 6.3 秒、1.1 秒，第二轮记住前文）。这些是单次本机观察，不是速度承诺或并发性能结论。
临时测试账号与消息不写入正式 `data/site.sqlite3`。

原 RAG 的 README、`config/dashscope.example.json` 与本站 `knowledge/installation.md`
是教程与安装助手共同的资料来源，不扫描私有运行目录。
