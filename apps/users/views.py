import json
import re
from datetime import datetime

from django.contrib.auth import login, authenticate, logout

# Create your views here.
from django.views import View
from django_redis import get_redis_connection
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, GenericViewSet, ModelViewSet
from rest_framework_jwt.settings import api_settings
from rest_framework_jwt.views import ObtainJSONWebToken

from apps.carts.utils import merge_cart_cookie_to_redis
from apps.goods.models import SKU
from apps.users.models import User, Address
from apps.users.serializers import CreateUserSerializer, UserDetailSerializer, EmailSerializer, AddressTitleSerializer, \
    UserAddressSerializer, SKUSerializer, UserBrowserHistorySerializer
from apps.users.utils import generate_verify_email_url, check_verify_email_url
from celery_tasks.email.tasks import logger
from utils.viewsMixin import LoginRequiredJSONMixin

"""
判断用户名是否重复
前端： 用户输入用户名， 失去焦点， 发送一个axios(ajax)请求
后端：
	接收请求，： 接收用户
	路由； get /usernames/<username>/count/
	业务逻辑：
		根据用户名，查询数据库， 查询当前数量， 数量大于0说明已经注册过了
	响应：json格式
		{"count":1, "code": "0", "errmsg": "ok"}
  
"""


class UsernameCountView(APIView):
    def get(self, request, username):
        # print(username)
        count = User.objects.filter(username=username).count()
        return Response({"count": count, "code": "0", "errmsg": "ok"})


"""
判断手机号是否重复注册
前端：用户输入手机号，失去焦点， 发送一个axios(ajax)请求
后端：
    接收请求，： 接收用户
	路由； get mobiles/<phone:mobile>/count/
	业务逻辑：
		根据手机号，查询数据库， 查询当前数量， 数量大于0说明已经注册过了
	响应：json格式
		{"count":1, "code": "0", "errmsg": "ok"}
"""


class MobileCountView(APIView):
    def get(self, request, mobile):
        # print(mobile)
        count = User.objects.filter(mobile=mobile).count()
        data = {"count": count, "code": "0", "errmsg": "ok"}
        return Response(data)


"""
注册
前端: 用户输入 用户名，密码，确认密码 ，手机号，同意协议， 点击注册按钮 发送axios 请求
后端：
    接受请求： 接收json 数据
    路由  post '/register/'
    业务逻辑：验证数据，保存到数据库
    响应 json 格式
        {"code": "0", "errmsg": "ok"}
        {"code": "400", "errmsg": "register fail"}
        
    
"""


class RegisterView(CreateAPIView):
    serializer_class = CreateUserSerializer


"""
登陆

前端： 用户输入用户名/手机号， 密码 ， 是否记住denglu

后端：
    接受 请求 ：  Post  接收 json数据 验证 用户名， 密码
    逻辑：
        从 数据库取出 用户名 密码  进行验证
        记住登录状态，
    路由： post '/login/'
    响应： 
        json格式
        {"code":"0","errmsg":"ok"}
        {"code":"400","errmsg":"fail"}

"""

jwt_response_payload_handler = api_settings.JWT_RESPONSE_PAYLOAD_HANDLER


class UserAuthorizeView(ObtainJSONWebToken):
    """自定义账号密码登录视图,实现购物车登录合并"""

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = jwt_response_payload_handler(token, user, request)
            response = Response(response_data)
            if api_settings.JWT_AUTH_COOKIE:
                expiration = (datetime.utcnow() +
                              api_settings.JWT_EXPIRATION_DELTA)
                response.set_cookie(api_settings.JWT_AUTH_COOKIE,
                                    token,
                                    expires=expiration,
                                    httponly=True)
            # 账号登录时合并购物车
            merge_cart_cookie_to_redis(request, user, response)

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# RetrieveAPIView 获取一个对象的信息
class UserInfoView(RetrieveAPIView):
    """用户中心"""
    # 指定序列化器
    serializer_class = UserDetailSerializer
    # 视图权限  定权限,只有通过认证的用户才能访问当前视图
    permission_classes = [IsAuthenticated]

    # 返回模型对象
    def get_object(self):
        return self.request.user

    # def get(self, request):
    #     """提供个人信息界面"""

    # 获取界面需要的数据,进行拼接
    # info_data = {
    #     'username': request.user.username,
    #     'mobile': request.user.mobile,
    #     'email': request.user.email,
    #     'email_active': request.user.email_active
    # }
    #
    # # 返回响应
    # return Response({'code': 0,
    #                      'errmsg': 'ok',
    #                      'info_data': info_data})


"""
添加邮箱

前端： 用户输入邮箱，用户点击保存，发送请求

后端：
    接收请求   
    业务逻辑:
        验证邮箱 参数， 
    路由 put '/emails/' 
    响应：json数据
        {'code': 0, 'errmsg': '添加邮箱成功'}
        {'code': 400, 'errmsg': '邮箱错误'}
        
"""
from django import http


# UpdateAPIView 使用三级视图 更新 邮箱验证
class SaveEmailView(UpdateAPIView):
    """添加邮箱"""
    permission_classes = [IsAuthenticated]
    serializer_class = EmailSerializer

    def get_object(self):
        """重写此方法返回 要展示的用户模型对象"""
        return self.request.user
    # def put(self, request):
    #     """实现添加邮箱逻辑"""
    #     # 接收参数
    #     json_dict = json.loads(request.body.decode())
    #     email = json_dict.get('email')
    #
    #     # 校验参数
    #     if not email:
    #         return http.JsonResponse({'code': 400,
    #                                   'errmsg': '缺少email参数'})
    #     if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
    #         return http.JsonResponse({'code': 400,
    #                                   'errmsg': '参数email有误'})
    #
    #     # 赋值email字段
    #     try:
    #         request.user.email = email
    #         request.user.save()
    #     except Exception as e:
    #         logger.error(e)
    #         return http.JsonResponse({'code': 400, 'errmsg': '添加邮箱失败'})
    #
    #     # 异步发送验证邮件
    #     from celery_tasks.email.tasks import send_verify_email
    #     # 生成验证链接
    #     # verify_url = '邮件验证链接'
    #     verify_url = generate_verify_email_url(request.user)
    #
    #
    #     send_verify_email.delay(to_email=email, verify_url=verify_url)
    #
    #     # 响应添加邮箱结果
    #     return http.JsonResponse({'code': 0, 'errmsg': '添加邮箱成功'})


"""验证邮箱"""


class VerifyEmailView(APIView):

    def put(self, request):
        print('-----验证邮箱-----')
        # 1, 获取token
        token = request.GET.get('token')
        # 2. 解密token
        user = check_verify_email_url(token)
        # 3. 数据库验证，
        try:
            user = User.objects.filter(id=user.id, email=user.email).get()
        except Exception as e:
            print(e)
            return Response({'code': 400, 'errmsg': '参数有误'})

        # 4. 设置邮箱已激活
        try:
            user.email_active = True
            user.save()
        except Exception as e:
            print(e)
        return Response({'code': 0, 'errmsg': '邮箱激活成功'}, status=status.HTTP_200_OK)


"""修改密码"""


class UpdatePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        # 接收参数
        body_dict = json.loads(request.body)
        old_password = body_dict.get('old_password')
        new_password = body_dict.get('new_password')
        new_password2 = body_dict.get('new_password2')
        # 进行参数 校验
        if not all([old_password, new_password, new_password2]):
            return Response(data={'errmsg': '参数有误'}, status=status.HTTP_400_BAD_REQUEST)

        if old_password == new_password or new_password2 != new_password or old_password == new_password2:
            return Response(data={'errmsg': '参数有误'}, status=status.HTTP_400_BAD_REQUEST)

        # 与原始密码对比
        result = request.user.check_password(old_password)
        if not result:
            return Response(data={
                'errmsg': '原始密码不正确'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 进行数据库查询
            user = User.objects.get(id=request.user.id)
            user.set_password(new_password2)
            user.save()
        # 进行数据修改
        except Exception as e:
            print(e)
            return Response({'errmsg': '密码修改fail'}, status=status.HTTP_400_BAD_REQUEST)

        http = Response({'errmsg': '密码修改成功'}, status=status.HTTP_200_OK)

        # 返回响应
        return http

"""地址类视图集"""
# class AddressViewSet(ModelViewSet):
class AddressViewSet(UpdateModelMixin, GenericViewSet):
    """用户收货地址增删改查"""
    permission_classes = [IsAuthenticated]
    serializer_class = UserAddressSerializer

    def get_queryset(self):
        return self.request.user.addresses.filter(is_deleted=False)

    def create(self, request):
        user = request.user
        # count = user.addresses.all().count()
        count = Address.objects.filter(user=user).count()
        # 用户收货地址数量有上限  最多只能有20
        if count >= 20:
            return Response({'message': '收货地址数量上限'}, status=status.HTTP_400_BAD_REQUEST)

        # 创建序列化器进行反序列化
        serializer = self.get_serializer(data=request.data)
        # print("request数据",request.data)
        # serializer = self.serializer_class(data=request.data)
        # 调用序列化器的is_valid()
        serializer.is_valid(raise_exception=True)
        # 调用序列化器的save()
        serializer.save()
        # 响应
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # GET /addresses/
    def list(self, request, *args, **kwargs):
        """
        用户地址列表数据
        """
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        # serializer = self.serializer_class(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'default_address_id': user.default_address_id,
            'limit': 20,
            'addresses': serializer.data,
        })

    def destroy(self, request, *args, **kwargs):
        """
        处理删除
        """
        address = self.get_object()

        # 进行逻辑删除
        address.is_deleted = True
        address.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

        # put /addresses/pk/title/
        # 需要请求体参数 title

    @action(methods=['put'], detail=True)
    def title(self, request, pk=None):
        """
        修改标题
        """
        address = self.get_object()
        serializer = AddressTitleSerializer(instance=address, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # put /addresses/pk/status/
    @action(methods=['put'], detail=True)
    def status(self, request, pk=None):
        """
        设置默认地址
        """
        address = self.get_object()
        request.user.default_address = address
        request.user.save()
        return Response({'message': 'OK'}, status=status.HTTP_200_OK)








"""浏览历史"""
class UserBrowserHistoryView(CreateAPIView):
    """用户商品浏览记录"""
    # 指定序列化器
    serializer_class = UserBrowserHistorySerializer
    permission_classes = [IsAuthenticated]  # 指定权限

    def get(self, request):
        """查询商品浏览记录"""

        # 创建redis连接对象
        redis_conn = get_redis_connection('history')
        # 获取当前请求的用户
        user = request.user

        # 获取redis中当前用户的浏览记录列表数据
        sku_ids = redis_conn.lrange('history_%d' % user.id, 0, -1)

        # 把sku_id对应的sku模型查询 出来
        # SKU.objects.filter(id__in=sku_ids)  # 用此方式获取sku模型顺序就乱了
        sku_list = []
        for sku_id in sku_ids:
            sku = SKU.objects.get(id=sku_id)
            sku_list.append(sku)
        # 创建序列化器进行序列化器
        serializer = SKUSerializer(sku_list, many=True)

        # 响应
        return Response(serializer.data)