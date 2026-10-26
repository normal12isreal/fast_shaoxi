# 学生手册 RAG 网站

用 FastAPI 学习网页、HTTP 接口、数据库和模型调用。网站引用原来的
[学生手册 RAG](https://github.com/normal12isreal/shaoxing_university_handbook_rag)，不复制数据或重新生成向量。

## 本地启动

在本目录运行 PowerShell，Python、依赖和缓存都保留在项目内：

```powershell
.\scripts\bootstrap.ps1
.\scripts\dev.ps1
```

打开 <http://127.0.0.1:8000/>，接口文档在 `/docs`。按 Ctrl+C 停止。
如脚本执行受限，可用 `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\dev.ps1`。

## 当前施工阶段

首页 `/`、安装教程 `/guide`、登录 `/login`、注册 `/register`、个人中心 `/account`
已建立。问答、账号和助手按顺序接入，未接通的功能在页面明确标示。
原项目默认位于同级 `student-handbook-rag`，其他位置通过 `RAG_PROJECT_DIR` 指定。
教程与首页读取原项目公开 README，安装补充资料在 `knowledge/installation.md`。

## 验证与阅读入口

```powershell
.\scripts\uv.ps1 run --locked pytest
.\scripts\uv.ps1 run --locked ruff check .
.\scripts\uv.ps1 run --locked ruff format --check .
```

- [文档地图](docs/README.md)：按问题找说明。
- [网站调用关系](docs/website.md)：页面、JSON 接口和处理模块。
- [环境说明](docs/setup.md)：项目内工具与依赖。
- [Agent 导航](AGENTS.md)：维护职责。

本轮只在本地开发，不推送、不部署。
