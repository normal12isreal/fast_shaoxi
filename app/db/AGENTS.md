# 数据库职责

- `core.py` 管理 SQLite 连接、外键和迁移；`models.py` 是 ORM 映射。
- 历史表结构在根 `migrations/versions/`；新增字段时新增迁移，不修改已应用的旧迁移。
- 模型调用前关闭数据库事务；完成、失败再开短事务保存状态。
- 用户数据查询必须带 user_id；消息通过所属 conversation 校验归属。
- 迁移、外键删除和用户隔离用临时 SQLite 测试，不操作真实学习记录。
