"use strict";
// 页面脚本共用：fetch → JSON；错误统一转成可显示的文字，不输出服务端异常详情。
window.api = async function (path, options = {}) {
  const response = await fetch(path, options);
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    const message = Array.isArray(detail) ? detail.map(x => x.msg).join("；")
      : typeof detail === "string" ? detail : "请求未完成，请稍后重试";
    const error = new Error(message);
    error.status = response.status;
    throw error;
  }
  return data;
};
window.jsonRequest = (body) => ({headers: {"Content-Type": "application/json"}, body: JSON.stringify(body)});
window.showStatus = (id, message) => { document.getElementById(id).textContent = message; };
window.sessionReady = window.api("/api/auth/me").then(user => {
  const nav = document.getElementById("user-nav");
  nav.replaceChildren();
  const name = document.createElement("span"); name.textContent = user.username;
  const logout = document.createElement("button"); logout.className = "secondary"; logout.textContent = "退出";
  logout.onclick = async () => {
    try { await window.api("/api/auth/logout", {method:"POST"}); location.assign("/"); }
    catch (error) { logout.textContent = error.message; }
  };
  nav.append(name, logout); return user;
}).catch(() => null);

