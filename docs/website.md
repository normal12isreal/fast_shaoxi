# 网站调用关系

第一阶段建立正式页面，替换旧 `/demo` 示例。

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

原 RAG 的 README、`config/dashscope.example.json` 与本站 `knowledge/installation.md`
是教程与安装助手共同的资料来源，不扫描私有运行目录。
