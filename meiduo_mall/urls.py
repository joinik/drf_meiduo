"""meiduo_mall URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include, re_path


def testlog(request):
    import logging
    logger = logging.getLogger('django')
    logger.info('info信息   用户登录成功')
    logger.info('info信息   用户退出')
    logger.warning('redis空间不足 ')
    logger.error('危险----！！！！')
    logger.info('info信息   用户登录成功')
    return HttpResponse('ok')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('testlog/', testlog),
    path('meiduo_admin/', include('apps.meiduo_admin.urls')),# meiduo后台
    path('', include("apps.users.urls")),
    path('', include("apps.verifications.urls")),
    # areas
    path('', include('apps.areas.urls')),
    # oauth
    path('', include('apps.oauth.urls')),
    # goods
    path('', include('apps.goods.urls')),
    path('', include('apps.contents.urls')),
    # 富⽂文本编辑器器
    # url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    re_path(r'^ckeditor/', include('ckeditor_uploader.urls')),
    # carts
    path('', include('apps.carts.urls')),
    # orders
    path('', include('apps.orders.urls')),
    # payment
    path('', include('apps.payment.urls')),
    # admin
    path("meiduo_admin", include("apps.meiduo_admin.urls"))
]
