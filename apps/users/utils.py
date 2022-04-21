import re

from django.contrib.auth.backends import ModelBackend
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadData
from django.conf import settings

from apps.users.models import User


def generate_verify_email_url(user):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    # serializer = Serializer(密钥, expires_in=3600)

    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    data = {'user_id': user.id, 'email': user.email}
    token = serializer.dumps(data).decode()
    verify_url = settings.EMAIL_VERIFY_URL + '?token=' + token

    return verify_url



def check_verify_email_url(token):
    """
    生成邮箱验证链接
    :param user: 当前登录用户
    :return: verify_url
    """
    # serializer = Serializer(密钥, expires_in=3600)

    serializer = Serializer(settings.SECRET_KEY, expires_in=3600)
    # 解密
    try:
        data = serializer.loads(token)
    except BadData:
        return None
    else:
        user_id = data.get('user_id')
        email = data.get('email')
        print('解密email',email)
        try:
            user = User.objects.get(id=user_id, email=email)
        except User.DoesNotExist:
            return None
        else:
            return user


def get_user_by_account(account):
    """
    通过传入的账号动态获取user 模型对象
    :param account:  有可以是手机号,有可能是用户名
    :return:  user或None
    """
    try:
        if re.match(r'1[3-9]\d{9}$', account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None  # 如果没有查到返回None
    else:
        return user

class UsernameMobileAuthBackend(ModelBackend):
    """修改Django的认证类,为了实现多账号登录"""

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 获取到user
        user = get_user_by_account(username)

        # 判断当前前端传入的密码是否正确
        if user and user.check_password(password):
            # 返回user
            return user

