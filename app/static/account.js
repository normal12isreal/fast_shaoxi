"use strict";
// /account 只读取当前用户的记录；打开记录详情不会再次调用 RAG。
let offset = 0;
async function loadRecords() {
  try {
    const page = await api(`/api/rag/records?limit=10&offset=${offset}`);
    const container = document.getElementById("records"); container.replaceChildren();
    for (const item of page.items) {
      const details = document.createElement("details"); const heading = document.createElement("summary");
      heading.textContent = `${item.question} · ${new Date(item.created_at).toLocaleString()}`;
      const answer = document.createElement("div"); answer.className = "plain-text";
      details.append(heading, answer);
      details.addEventListener("toggle", async () => {
        if (!details.open || answer.dataset.loaded) return;
        try {
          const record = await api(`/api/rag/records/${item.id}`);
          answer.textContent = record.result ? record.result.answer : `处理状态：${record.status}。${record.error || ""}`;
          if (record.result) {
            for (const source of record.result.sources) {
              const paragraph = document.createElement("p");
              paragraph.textContent = `${source.label}（PDF ${source.pdf_pages.join("、")}）：${source.text}`;
              answer.append(paragraph);
              for (const reference of source.web_sources || []) {
                const line = document.createElement("p"); const link = document.createElement("a");
                link.href = reference.url; link.textContent = reference.title; line.append(link); answer.append(line);
              }
            }
          }
          answer.dataset.loaded = "true";
        } catch (error) {answer.textContent = error.message;}
      });
      container.append(details);
    }
    showStatus("account-status", page.total ? `共 ${page.total} 条记录` : "还没有记录，登录后到首页问一个问题吧。");
    document.getElementById("record-page").textContent = page.total ? `${offset+1}–${offset+page.items.length} / ${page.total}` : "0 / 0";
    document.getElementById("previous-records").disabled = offset === 0;
    document.getElementById("next-records").disabled = offset + 10 >= page.total;
  } catch (error) {
    showStatus("account-status", error.status === 401 ? "请先登录，再查看自己的记录。" : error.message);
  }
}
sessionReady.then(user => {if (user) loadRecords(); else showStatus("account-status", "请先登录，再查看自己的记录。");});
document.getElementById("previous-records").onclick = () => {offset = Math.max(0, offset-10); loadRecords();};
document.getElementById("next-records").onclick = () => {offset += 10; loadRecords();};

