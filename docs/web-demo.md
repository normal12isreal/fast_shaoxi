# 网页响应练习

启动方式见 [根 README](../README.md)，打开 `/demo` 开始。当前只演示响应方式，
不连接 RAG，不调用模型 API，不保存数据。两张图片是仓库内的 SVG 占位图。

## 从哪个文件开始看

1. [main.py](../app/main.py)：Uvicorn 加载 `app`；`create_app()` 装配 API、页面和静态目录。
2. [页面路由](../app/pages/routes.py)：看三个 URL 分别返回什么。
3. [页面模板](../app/templates/index.html)：看 `{{ app_name }}` 与 `url_for(...)` 的来源。
4. [浏览器脚本](../app/static/app.js)：看表单如何变成一次 JSON 请求。
5. [echo 路由](../app/api/routes/examples.py) 与 [schema](../app/schemas/examples.py)：
   看输入校验和输出字段。

代码旁的中文注释说明 URL、函数与文件的映射。`include_router()` 是启动时注册处理函数，
并不意味着每次打开页面都会执行所有接口；运行时由请求的方法和路径选择具体入口。

## 五种响应的实际调用链

| 操作 | 调用映射 | 浏览器收到什么 |
|---|---|---|
| 打开 `/demo` | `demo_page()` → `templates/index.html`，填入配置中的网站名称 | HTML |
| 打开图片或加载 CSS、JS | `/static/` → `main.py` 挂载 → `app/static/` 下的相对文件 | 原文件内容 |
| 表单发送文字 | `app.js` → `POST /examples/echo` → `EchoRequest` → `echo()` → `EchoResponse` | JSON |
| 点击直接 HTML 链接 | `plain_html()` → Python 中的 HTML 字符串 | HTML |
| 点击下载 | `download_map()` → `resources/request-map.txt` | 带附件文件名的文本响应 |

模板和直接 HTML 都返回 `text/html`。区别在于内容怎样生成：模板把数据填入独立文件，
直接 HTML 示例把内容写在函数中。不要把模板理解为浏览器会执行的 Python 代码。

`url_for('echo')` 中的 `echo` 对应注册的函数名；`url_for('static', path=...)` 中的
`static` 对应挂载时的名称。模板把这些地址放入 HTML；浏览器再按地址发起请求。

`StaticFiles` 根据 URL 前缀和相对路径找文件，不自动生成文件列表；不存在的文件返回 404。
只公开 `app/static/`，配置、模板和整个项目目录都不对外挂载。
下载路由只提供固定文件，和公开整个文件夹是两种不同的方式。

## 在浏览器中观察

1. 打开开发者工具的 Network 面板，再刷新 `/demo`。观察 HTML、CSS、JS、两张 SVG
   是不同请求；浏览器也可能额外请求 favicon。
2. 输入中文并发送。观察 Fetch/XHR 中的请求体和 JSON 响应，整个页面没有重新加载。
3. 输入 `<b>你好</b>`，结果应显示为普通文本，不变成加粗 HTML。
4. 在 `/docs` 调用 echo：发送 `{"message":""}`，观察 422 和字段错误位置。
   页面表单会先通过浏览器的 required/maxlength 做一层检查，不能替代后端校验。
5. 打开两张图片链接，地址只有文件名不同，却共用同一份静态目录挂载。
6. 打开直接 HTML 链接，随后返回；下载文本并打开，对照里面的调用说明。

本轮不是完整 RAG 网站；下一步在确认这些链路后，再讨论独立的问答接口。
