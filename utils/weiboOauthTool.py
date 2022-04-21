from django.conf import settings
from urllib.parse import urlencode, parse_qs
import json
import requests


class OAuthWeibo(object):
    """
    QQ认证辅助工具类
    """

    def __init__(self, client_id=None, client_secret=None, redirect_uri=None, state=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.state = state   # 用于保存登录成功后的跳转页面路径

    def get_weibo_url(self):
        # weibo登录url参数组建
        data_dict = {
            'client_id': self.client_id,
            # 'response_type': 'code',
            'redirect_uri': self.redirect_uri,
            'state': self.state
        }

        # 构建url
        weibo_url = 'https://api.weibo.com/oauth2/authorize?' + urlencode(data_dict)

        return weibo_url

    # 获取access_token值
    def get_access_token(self, code):
        # 构建参数数据
        data_dict = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': self.redirect_uri,
        }

        # 构建url
        access_url = 'https://api.weibo.com/oauth2/access_token'

        # 发送请求
        try:
            response = requests.post(url=access_url,data=data_dict)

            # 提取数据
            # {
            #     "access_token": "ACCESS_TOKEN",
            #     "expires_in": 1234,
            #     "remind_in":"798114",
            #     "uid":"12341234"
            # }

            data = response.text

            # 转化为字典
            data = parse_qs(data)
            print('token----body_dict',data)
        except:
            raise Exception('weibo请求失败')

        # 提取access_token
        access_token = data.get('access_token', None)

        if not access_token:
            raise Exception('access_token获取失败')
        print(access_token)
        return access_token

    # 获取open_id值

    def get_uid(self, access_token):

        # 构建请求url
        url = 'https://api.weibo.com/oauth2/get_token_info'
        data = {
            'access_token': access_token,
        }
        # 发送请求
        try:
            response = requests.post(url=url,data=data)

            # 提取数据
            # callback( {"client_id":"YOUR_APPID","openid":"YOUR_OPENID"} );
            # code=asdasd&msg=asjdhui  错误的时候返回的结果
            # {
            #     "uid": 1073880650,
            #     "appkey": 1352222456,
            #     "scope": null,
            #     "create_at": 1352267591,
            #     "expire_in": 157679471
            # }
            data = response.text

        except:
            raise Exception('weibo请求失败')
        # 转化为字典
        try:
            data_dict = json.loads(data)
            # 获取openid
            uuid = data_dict.get('uid')
        except:
            raise Exception('uuid获取失败')

        return uuid
