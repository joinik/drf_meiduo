from django.conf.urls import url
from django.urls import path

from . import views
from .views import OauthView, QQLoginUrlView, WEIBOLoginUrlView, WeiboOauthView

urlpatterns = [
    path('qq/authorization/', QQLoginUrlView.as_view()),
    path('weibo/authorization/', WEIBOLoginUrlView.as_view()),
    path('oauth_callback/', OauthView.as_view()),
    # path('oauth_callback/', WeiboOauthView.as_view()),

]