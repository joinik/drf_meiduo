from django.db import models


class BaseModel(models.Model):
    """为模型类 补充通用字段"""
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建数据的时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新数据的时间')


    class Meta:
        abstract = True    # 抽象， 迁移时不创建 表  只是继承