from django.urls import path, register_converter, re_path
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import refresh_jwt_token


from apps.users.views import UsernameCountView, RegisterView, MobileCountView, UserInfoView, \
    SaveEmailView, VerifyEmailView, UserAuthorizeView, UpdatePassword, AddressViewSet, UserBrowserHistoryView
from utils.myconverters import UsernameConverter, PhoneConverter

register_converter(UsernameConverter, 'user')
register_converter(PhoneConverter, 'phone')

urlpatterns = [
    # 用户名验证
    path('usernames/<user:username>/count/', UsernameCountView.as_view()),
    # 手机号验证
    path('mobiles/<phone:mobile>/count/', MobileCountView.as_view()),
    # 注册类
    path('register/', RegisterView.as_view()),
    # 登录验证 自定义类
    path('authorizations/', UserAuthorizeView.as_view()),
    path('refresh/', refresh_jwt_token),  # 刷新token
    # 用户个人信息
    path('info/', UserInfoView.as_view()),
    # 创建邮箱
    path('emails/', SaveEmailView.as_view()),
    # 验证邮箱
    path('emails/verification/', VerifyEmailView.as_view()),
    # 修改密码
    path('password/', UpdatePassword.as_view()),
    # 商品浏览记录
    re_path(r'^browse_histories/$', UserBrowserHistoryView.as_view()),
]

router = DefaultRouter()
router.register(r'addresses', AddressViewSet, basename='addresses')  # 如果视图集中没有给queryset类属性指定查询集,就必须给base_name传参数,如果不传默认取queryset中指定的查询集模型名小写作为路由别名前缀
urlpatterns += router.urls
