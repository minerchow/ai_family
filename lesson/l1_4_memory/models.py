"""把本节的 MySQL 消息表映射成 Python 对象。"""
from tortoise import fields, models

# 每条记录保存一条用户发言或模型回答。
class MemoryMessage(models.Model):
    # 数据库自动生成编号，编号越大发言越晚。
    id = fields.BigIntField(primary_key=True)
    # user 表示用户，assistant 表示模型，不是登录权限角色。
    role = fields.CharField(max_length=20)
    # 保存问题或回答的完整文字。
    content = fields.TextField()

    # 告诉 ORM 使用哪张已经建好的表。
    class Meta:
        # 名称必须与建表 SQL 一致。
        table = "memory_message"