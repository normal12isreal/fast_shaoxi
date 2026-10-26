"use strict";
// 账号接口接通后，本脚本向同源地址发送用户名和密码，登录凭据保存在 HttpOnly Cookie。
document.getElementById("auth-form").addEventListener("submit", async event => {
  event.preventDefault();
  const button = document.getElementById("auth-submit");
  if (button.disabled) return;
  const mode = event.currentTarget.dataset.mode; button.disabled = true;
  try {
    await api(`/api/auth/${mode}`, {method:"POST", ...jsonRequest({
      username:document.getElementById("username").value, password:document.getElementById("password").value
    })});
    if (mode === "register") await api("/api/auth/login", {method:"POST", ...jsonRequest({
      username:document.getElementById("username").value, password:document.getElementById("password").value
    })});
    const next = new URLSearchParams(location.search).get("next");
    location.assign(next && ["/", "/guide", "/account"].includes(next) ? next : "/account");
  } catch (error) {showStatus("auth-status", error.message);}
  finally {button.disabled = false;}
});

