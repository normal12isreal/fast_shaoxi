"use strict";

// index.html 的 script 标签 → GET /static/app.js → 浏览器执行本文件。
// defer 保证 HTML 解析后再查找表单；这里的代码在浏览器运行，而不是 Python 服务器。
const form = document.getElementById("echo-form");
const sendButton = document.getElementById("send");
const statusText = document.getElementById("request-status");
const resultText = document.getElementById("result");

form.addEventListener("submit", async (event) => {
  event.preventDefault(); // 阻止原生表单整页跳转，改为下面的 fetch 请求。
  sendButton.disabled = true;
  statusText.textContent = "正在请求…";
  resultText.textContent = "";
  try {
    // data-endpoint 由模板 url_for('echo') 填入，对应 Python 的 POST /examples/echo。
    const response = await fetch(form.dataset.endpoint, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: document.getElementById("message").value }),
    });
    // JSON 响应 → JavaScript 对象 → 可读文本；422 等错误也显示原响应，方便学习。
    const data = await response.json();
    resultText.textContent = JSON.stringify(data, null, 2);
    statusText.textContent = response.ok
      ? `请求成功（HTTP ${response.status}），页面没有刷新。`
      : `请求失败（HTTP ${response.status}），请查看下面的校验详情。`;
  } catch {
    statusText.textContent = "请求未完成，请检查服务是否仍在运行，然后重试。";
  } finally {
    sendButton.disabled = false;
  }
});
// 返回内容仅以 textContent 显示；即使输入看起来像 HTML，也会当普通文字处理。
