from django.http import HttpResponse, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from django_redis import get_redis_connection

from utils.captcha.captcha import captcha
from celery_tasks.sms.tasks import celery_send_sms_code

"""
图片验证码
前端： 用户点击 图片验证码 生成 UUID，拼接url ， 发送 请求
后端：
    请求 get   地址里的UUID
    路由  get '/image_codes/<uuid>/'
    业务逻辑： 接收uuid ，生成 图片验证码 ，保存到redis 数据库
    响应  返回二进制数据
    
    
"""

class ImageCodeView(View):
    def get(self, request, uuid):

        #  1. 获取uuid，
        print(uuid)
        #   2. 生成验证码图片，二进制数据
        text, image = captcha.generate_captcha()
        print(text)
        #   3. 存到redis UUID作为key
        #   get_redis_connection  获取redis 数据库
        redis_cli = get_redis_connection("image_code")
        #  uuid 为key 120s是过期时间
        redis_cli.setex(uuid,120,text)

        #   4. 返回二进制图片数据
        return HttpResponse(image,content_type='image/jpeg')




"""
前端：用户输入手机号， 点击获取短信验证码， 发送 axiou 请求 

后端：
    接收请求； 参数 1，手机号，2图片验证码，3.uuid， 
    逻辑：    验证参数 图片验证码，生成短信验证码， 存入redis 数据库，  发送短信
    响应  路由 "sms_codes/<mobile>/?image_code=xxx&image_code_id =xxxxx"
"""


class MsmCodeView(View):
    def get(self, request, mobile):
        # 1. 获取参数，
        mobile = mobile
        image_code = request.GET.get('image_code')
        uuid = request.GET.get('image_code_id')

        #  2.  验证参数， 是否存在
        if not all([image_code, uuid]):
            return JsonResponse({'code': 400, 'errmsg': "参数不全"})
        # 3. 图片验证码
        redis_cli = get_redis_connection("image_code")
        redis_image_code = redis_cli.get(uuid)
        # 删除图片验证码
        try:
            redis_cli.delete(uuid)
        except Exception as e:
            print("删除图片验证码")

        # 3.2判断是否过有效期
        if redis_image_code is None:
            return JsonResponse({'code': 400, 'errmsg': "图片验证码过期"})

        # 3.3用户发过来的对比 redis_image_code是二进制 需要decode
        if redis_image_code.decode().lower() != image_code.lower():
            return JsonResponse({'code': 400, 'errmsg': "图片验证码输入错误"})

        # 4. 生成短信验证码
        # 0-999999
        from random import randint
        # "%06d" 让数字保存6位  如果不够 左侧补0
        sms_code = "%06d" % randint(0, 999999)
        print("sms_code", sms_code)

        # 防止发送短信 频繁
        send_flag = redis_cli.get("send_flag_%s" % mobile)
        if send_flag:
            return JsonResponse({'code': 400, 'errmsg': "短信发送过于频繁 "})

        # 创建Redis 管道
        pl = redis_cli.pipeline()


        # 5. 保存短信验证码到redis
        pl.setex("send_flag_%s" % mobile, 60, 1)
        pl.setex("sms_%s" % mobile, 300, sms_code)
        # 执行请求
        pl.execute()

        # 6. 发送短信
        # from celery_tasks.sms.SendMessage import Sms
        # Sms().send_message(mobile, (sms_code,2))
        #  6. 发送短信  使用celery
        print('------->>>')
        # celery_send_sms_code.delay(mobile, sms_code)
        print('>>>>>异步')
        # 7 返回响应
        return JsonResponse({'code': 0, 'errmsg': "ok"})

