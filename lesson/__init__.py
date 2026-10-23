"""课程代码目录。

每节课新建一个独立的包，例如 lesson/l1_2_stream/，包内按需新建
api.py（定义 router）、service.py、models.py 等文件。
接口和数据模型会被 common/discovery.py 自动注册，不需要修改其他文件。
"""
