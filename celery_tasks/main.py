# celery启动文件
import os
from datetime import timedelta

from celery import Celery

# 为celery使用django配置文件进行设置
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meiduo_mall.settings")

# 创建celery实例
app = Celery('meiduo_mall')

# 设置
app.config_from_object("celery_tasks.config")


# 自动检测任务
app.autodiscover_tasks(["celery_tasks.sms","celery_tasks.email",])

# 声明定时任务
# app.conf.beat_schedule = {
#     u'generate_static_index': {		# 任务名，可以自定义
#         "task": "celery_tasks.generate_static_index_html.tasks.generic_static_html",	# 任务函数
#         "schedule": timedelta(minutes=1),	# 定时每30秒执行一次(从开启任务时间计算)
#         # "args": (1, 3),		# 传未定义的不定长参数
#         # 'kwargs': ({'name':'张三'}),	# 传已定义的不定长参数
#     },
    # u'inputsysapp_tasks_delete': {
    #     "task": "inputsysapp.tasks.delete",
    #     "schedule": crontab(minute='*/1'),		# 定时每1分钟执行一次(每分钟的0秒开始执行)
    #     # "args": (),
    #     # 'kwargs': (),
    # },
# }