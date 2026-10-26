"""手动应用数据库迁移；应用启动也会执行相同操作。"""

from app.db.core import Database

database = Database()
try:
    database.migrate()
    print("数据库已更新到最新迁移。")
finally:
    database.close()
