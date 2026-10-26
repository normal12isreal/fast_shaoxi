"use strict";
// 表单 → 同源账号接口；登录凭据保存在 HttpOnly Cookie，JS 不读取令牌。
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

