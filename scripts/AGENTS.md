# 本地工具职责

- `bootstrap.ps1`：校验并下载固定版本 uv，安装项目 Python，同步锁定依赖。
- `uv.ps1`：统一设置项目内安装、缓存和临时目录，再转发 uv 参数；退出时恢复调用者环境。
- `dev.ps1`：开发服务器入口，默认仅绑定 `127.0.0.1`。
- `toolchain.json`：uv 下载版本及官方发布资产 SHA-256；升级时一起更新。
- 不修改系统 PATH、注册表、系统 Python、用户 PowerShell profile 或全局包。
- 修改下载/环境逻辑后验证实际路径；说明同步到 [环境文档](../docs/setup.md)。
