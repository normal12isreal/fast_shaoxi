"use strict";
// 首页表单 → POST /api/rag/ask → JSON → 页面答案和引用。210 秒是浏览器等待上限。
document.getElementById("ask-form").addEventListener("submit", async event => {
  event.preventDefault();
  const button = document.getElementById("ask-button");
  const question = document.getElementById("question").value.trim();
  if (!question || button.disabled) return;
  button.disabled = true; document.getElementById("answer").hidden = true;
  showStatus("ask-status", "正在检索和生成回答，通常约 20 秒，请勿重复提交…");
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 210000);
  try {
    const data = await api("/api/rag/ask", {method:"POST", ...jsonRequest({question}), signal:controller.signal});
    document.getElementById("answer").hidden = false;
    document.getElementById("answer-text").textContent = data.answer;
    document.getElementById("answer-meta").textContent = `${data.status} · ${data.elapsed_seconds.toFixed(1)} 秒`;
    const warnings = document.getElementById("answer-warnings");
    warnings.hidden = data.complete && !data.warnings.length && data.status === "answered";
    warnings.textContent = "此回答可能需要澄清、依据有限或未完整生成，请结合状态和引用核对。";
    const sources = document.getElementById("sources"); sources.replaceChildren();
    for (const source of data.sources) {
      const details = document.createElement("details");
      const title = document.createElement("summary"); title.textContent = `${source.label} · PDF 页码 ${source.pdf_pages.join("、") || "无"}`;
      const text = document.createElement("p"); text.className = "plain-text"; text.textContent = source.text;
      details.append(title, text);
      for (const reference of source.web_sources || []) {
        const link = document.createElement("a"); link.href = reference.url; link.textContent = reference.title;
        const line = document.createElement("p"); line.append(link); details.append(line);
      }
      sources.append(details);
    }
    showStatus("ask-status", `已完成 · 请求编号 ${data.request_id}`);
  } catch (error) {
    showStatus("ask-status", error.name === "AbortError" ? "等待超过 210 秒；服务端可能仍在处理，请稍后再试。" : error.message);
  } finally {clearTimeout(timer); button.disabled = false;}
});

