# 页面响应职责

- `routes.py`：将页面 URL 映射到模板、直接 HTML 或固定下载文件。
- 模板结构在 `../templates/`，浏览器交互与样式在 `../static/`，下载正文在 `../resources/`。
- 保留紧邻代码的中文调用映射注释，改动 URL 或文件位置时同步说明。
- 静态目录挂载归 `app/main.py`；JSON 输入输出归 `app/api/` 与 `app/schemas/`。
- 当前为响应方式演示，不调用 RAG，不引入数据库或业务 service。
- 阅读与手动验证入口见 [网页练习](../../docs/web-demo.md)。
