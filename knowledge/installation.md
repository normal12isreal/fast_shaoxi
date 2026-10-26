# 安装助手的补充说明

本教程只针对 [学生手册 RAG 项目](https://github.com/normal12isreal/shaoxing_university_handbook_rag)，
不是当前 FastAPI 网站的安装教程。

- 克隆或下载原仓库完整内容，进入原仓库根目录后再执行 README 的命令。
- Windows PowerShell 使用 `.\.venv\Scripts\python.exe`；Linux/macOS 使用 `.venv/bin/python`。
- Windows CMD 跨盘进入目录用 `cd /d 路径`，PowerShell 可直接 `Set-Location 路径`。
- 先检查解释器路径与 Python 版本，再检查包是否安装在相同的虚拟环境。
- 原项目需要百炼北京区域匹配的 API Key、base_url 及模型权限；API Key 只填到本地配置，
  不要粘贴到聊天框。报错内容中的密钥、令牌和个人信息应先删除。
- 仓库自带知识库和向量；正常使用不需要重新解析 PDF、下载 MinerU 或重做全量向量。
- `--no-web` 只关闭网页补查，模型调用仍需联网；查询模型可能产生费用。
- 遇到问题，请提供操作系统、执行的命令、完整错误信息（去除密钥）以及已完成的安装步骤。

助手只提供解释与操作建议，不执行命令，不读取用户电脑文件。
