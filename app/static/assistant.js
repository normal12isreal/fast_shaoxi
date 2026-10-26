"use strict";
// /guide → 对话 JSON 接口 → 服务器保存原始消息；这里只显示历史，不拼接模型上下文。
let currentConversation = "";
let conversationCount = 0;
let conversationTotal = 0;
let messageTotal = 0;
let busy = false;
let signedIn = false;
const visibleMessages = new Map();
const selector = document.getElementById("conversation-list");

function updateControls() {
  document.getElementById("new-conversation").disabled = !signedIn || busy;
  selector.disabled = !signedIn || busy;
  document.getElementById("chat-input").disabled = !signedIn || busy;
  document.getElementById("chat-send").disabled = !signedIn || busy;
  document.getElementById("delete-conversation").disabled = !currentConversation || busy;
  document.getElementById("more-conversations").disabled = busy || conversationCount >= conversationTotal;
  document.getElementById("more-messages").disabled = busy || visibleMessages.size >= messageTotal;
}

function displayMessages(scrollToEnd = true) {
  const container = document.getElementById("messages");
  container.replaceChildren();
  for (const item of [...visibleMessages.values()].sort((a, b) => a.id - b.id)) {
    const bubble = document.createElement("article");
    bubble.className = `message ${item.role} ${item.status}`;
    const heading = document.createElement("strong");
    heading.textContent = item.role === "user" ? "你" : "安装助手";
    const text = document.createElement("div"); text.className = "plain-text"; text.textContent = item.content;
    bubble.append(heading, text);
    if (item.status !== "completed") {
      const state = document.createElement("p"); state.className = "hint";
      state.textContent = `${item.status === "failed" ? "未完成" : "处理中"}：${item.error || "请等待调用结束"}`;
      bubble.append(state);
    }
    container.append(bubble);
  }
  if (!visibleMessages.size) {
    const empty = document.createElement("p"); empty.className = "empty-state";
    empty.textContent = "新对话不会继承其他对话。描述一个安装问题，或粘贴已去除密钥的报错。";
    container.append(empty);
  }
  if (scrollToEnd) container.scrollTop = container.scrollHeight;
}

async function loadConversations(append = false) {
  const page = await api(`/api/assistant/conversations?limit=10&offset=${append ? conversationCount : 0}`);
  if (!append) {
    selector.replaceChildren(new Option("选择或新建对话", ""));
    conversationCount = 0;
  }
  for (const item of page.items) selector.add(new Option(item.title, item.id));
  conversationCount += page.items.length; conversationTotal = page.total;
  selector.value = currentConversation;
  return page.items;
}

async function loadMessages(older = false) {
  if (!currentConversation) return;
  const page = await api(`/api/assistant/conversations/${currentConversation}/messages?limit=20&offset=${older ? visibleMessages.size : 0}`);
  if (!older) visibleMessages.clear();
  for (const item of page.items) visibleMessages.set(item.id, item);
  messageTotal = page.total;
  displayMessages(!older);
  if (page.busy) showStatus("chat-status", "这段对话仍在处理上一条消息，请稍后重新选择对话查看结果。");
}

async function action(work) {
  if (busy) return;
  busy = true; updateControls();
  try { await work(); }
  catch (error) { showStatus("chat-status", error.message); }
  finally { busy = false; updateControls(); }
}

async function createConversation() {
  const conversation = await api("/api/assistant/conversations", {method: "POST"});
  currentConversation = conversation.id;
  visibleMessages.clear(); messageTotal = 0;
  await loadConversations(); displayMessages();
  showStatus("chat-status", "已新建空对话。");
}

document.getElementById("new-conversation").onclick = () => action(createConversation);
selector.onchange = () => action(async () => {
  currentConversation = selector.value;
  visibleMessages.clear(); messageTotal = 0;
  showStatus("chat-status", ""); displayMessages(); await loadMessages();
});
document.getElementById("more-conversations").onclick = () => action(() => loadConversations(true));
document.getElementById("more-messages").onclick = () => action(() => loadMessages(true));
document.getElementById("delete-conversation").onclick = () => {
  if (!currentConversation || !confirm("删除这段对话及其全部消息？")) return;
  action(async () => {
    await api(`/api/assistant/conversations/${currentConversation}`, {method: "DELETE"});
    currentConversation = ""; visibleMessages.clear(); messageTotal = 0;
    await loadConversations(); displayMessages(); showStatus("chat-status", "已删除对话。");
  });
};

document.getElementById("chat-form").onsubmit = event => {
  event.preventDefault();
  const input = document.getElementById("chat-input");
  const content = input.value.trim();
  if (!content || !signedIn || busy) return;
  action(async () => {
    if (!currentConversation) await createConversation();
    showStatus("chat-status", "正在整理上下文并向千问提问，请勿重复发送…");
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 210000);
    try {
      await api(`/api/assistant/conversations/${currentConversation}/messages`, {
        method: "POST", ...jsonRequest({content}), signal: controller.signal,
      });
      input.value = ""; showStatus("chat-status", "回答已保存。");
    } catch (error) {
      showStatus("chat-status", error.name === "AbortError" ? "等待超时，请查看消息状态，后台可能仍在结束。" : error.message);
    } finally {
      clearTimeout(timer);
      // 只刷新历史，不会自动重发问题；失败原文也会显示。
      await loadConversations(); await loadMessages();
    }
  });
};

sessionReady.then(user => {
  signedIn = Boolean(user);
  const notice = document.getElementById("assistant-login");
  if (!user) {
    notice.replaceChildren(document.createTextNode("请先登录，聊天及历史记录仅对你可见。 "));
    const link = document.createElement("a"); link.href = "/login?next=/guide"; link.textContent = "去登录 →";
    notice.append(link); updateControls(); return;
  }
  notice.hidden = true;
  action(async () => {
    const items = await loadConversations();
    if (items.length) {currentConversation = items[0].id; selector.value = currentConversation; await loadMessages();}
    else displayMessages();
  });
});

