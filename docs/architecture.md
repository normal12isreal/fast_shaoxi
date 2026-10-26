# 代码职责与阅读顺序

先读 `app/main.py` 看装配，再按需要进入某条调用链，不必一次看完所有文件。

```text
app/
  main.py                 直接创建 FastAPI，生命周期管理实际资源
  pages/routes.py         页面 URL → Jinja2 模板
  templates/              首页、安装教程、账号、个人中心
  static/                 浏览器提交表单、显示结果和样式
  api/router.py           汇总 JSON 路由
  api/routes/             health、auth、rag、assistant
  schemas/                HTTP 输入输出与约束
  services/
    knowledge.py          页面与助手共用的公开资料白名单
    execution.py          线程池、执行名额和 HTTP 等待上限
    rag.py                项目内 RAG 加载和单次调用
    auth.py               密码、会话身份和同源校验
    records.py            登录用户问答记录的短事务
    assistant.py          对话归属、运行状态与消息保存
    assistant_context.py  职责、资料、摘要和最近六轮的组织
    qwen.py               独立的千问多轮 HTTP 调用
  db/                     SQLite 连接与 ORM 模型
migrations/               可重复执行的数据库版本演进
rag/                      上游运行代码、公开配置和已有索引，保留来源及许可
knowledge/                安装补充资料，不存模型密钥
tests/                    临时数据库、模拟模型和对外行为验证
scripts/                  项目内工具、启动、迁移与外部调用示例
```

页面加载与提问是两次独立请求：`GET /` → 页面模板；
`static/home.js` 提交 `POST /api/rag/ask` → schema 校验 → RAG service
→ 工作线程执行原 `HandbookRAG.ask()` → 响应模型过滤 → JSON → 页面。
注册登录由 `api/routes/auth.py` 接收 HTTP，`services/auth.py` 提供可复用身份校验。
个人记录只能按当前用户查询，数据库事务不跨模型等待。

`main.py` 保留直接创建应用，没有应用工厂或配置类。
`app.state` 只持有需要生命周期的数据库、RAG 及助手资源。
services 按实际规则拆分，不强制一张表一个 repository，也不逐层重复转发。

安装助手调用链：`static/assistant.js` → `api/routes/assistant.py` →
`services/assistant.py` 保存待处理消息并申请名额 → 工作线程组织上下文、调用千问 →
短事务保存回答 → JSON 回到页面。HTTP 超时只把记录标为失败，线程结束前不会释放对话。
首页问答和助手分别维护自己的执行池，互相不传聊天历史。

新增接口维护路由、schema 和必要测试；新增配置同步环境说明。
只有实际职责边界变化才补文档导航。部署配置等后续学到服务器阶段再加。
