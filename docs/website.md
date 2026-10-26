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
账号页面用于注册、登录和查看自己的手册问答记录。当前按钮按施工进度开放。
完整行为以路由、schema、测试和运行中的 `/docs` 为准。

公开问答的调用顺序：`static/home.js` 或外部程序 → `api/routes/rag.py`
→ `services/rag.py` → `services/execution.py` 的工作线程 → 原 `HandbookRAG.ask()`。
只传本次问题，不传历史；保留原库的默认检索、证据判断和复核。
输出通过 `schemas/rag.py` 筛选，内部文件路径、配置和记录路径不公开。

原代码从 `RAG_PROJECT_DIR` 引用，配置与索引通过 `.runtime/rag-view/` 下的目录链接读取；
Windows 使用 Junction，Linux 使用符号链接。没有复制数据，查询缓存写在网站目录。
原库的问答记录关闭，网站以后只保存登录用户的记录。
修改 RAG_PROJECT_DIR 后须停服务、检查两个目录链接指向并重新配置，不自动替换已有链接。

原 RAG 的 README、`config/dashscope.example.json` 与本站 `knowledge/installation.md`
是教程与安装助手共同的资料来源，不扫描私有运行目录。
