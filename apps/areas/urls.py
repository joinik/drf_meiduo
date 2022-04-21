from django.urls import path, re_path
from rest_framework.routers import DefaultRouter

from apps.areas.views import AreaViewSet

#

urlpatterns = [
    # path('areas/', AreasView.as_view()),
    # re_path(r'^areas/(?P<pk>[1-9]\d+)/$', SubsView.as_view()),

]
router = DefaultRouter()
router.register(r'areas', AreaViewSet, basename='area')  # 如果视图集中没有给queryset类属性指定查询集,就必须给base_name传参数,如果不传默认取queryset中指定的查询集模型名小写作为路由别名前缀
urlpatterns += router.urls