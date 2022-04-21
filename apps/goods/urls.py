from django.urls import path, re_path

from apps.goods import views
from apps.goods.views import ListView, HotGoodsView, DetailView, DetailVisitView

urlpatterns = [
    path('list/<category_id>/skus/', ListView.as_view()),
    path('hot/<category_id>/', HotGoodsView.as_view()),
    path('search/', views.MySearchView()),
    re_path(r'detail/(?P<sku_id>\d+)/', DetailView.as_view()),
    re_path(r'detail/visit/(?P<category_id>\d+)/', DetailVisitView.as_view()),
    # path(r'browse_histories/', UserBrowseHistory.as_view()),

]