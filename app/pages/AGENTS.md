# 页面响应职责

- `routes.py`：将页面 URL 映射到模板。
- 模板结构在 `../templates/`，浏览器交互与样式在 `../static/`。
- 保留紧邻代码的中文调用映射注释，改动 URL 或文件位置时同步说明。
- 静态目录挂载归 `app/main.py`；JSON 输入输出归 `app/api/` 与 `app/schemas/`。
- 页面不直接调用模型；JavaScript 通过 JSON API 调用实际业务。
- 阅读与手动验证入口见 [网站调用关系](../../docs/website.md)。
