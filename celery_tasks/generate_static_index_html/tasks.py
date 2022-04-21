import logging
from django.conf import settings
from django.core.mail import send_mail

from apps.contents.crons import generate_static_index_html
from celery_tasks.main import app

logger = logging.getLogger('django')


@app.task(name='generic_static_html')
def generic_static_html():
    """
    发送验证邮箱邮件
    :param to_email: 收件人邮箱
    :param subject: 邮箱标题
    :param verify_url: 验证链接
    :return: None
    """

    try:
        print("0-----开始")
        generate_static_index_html()
        print("1-----结束")
    except Exception as e:
        print(e)
