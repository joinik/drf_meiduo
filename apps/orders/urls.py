



from django.urls import path

from apps.orders.views import OrderSettlementView, CommitOrderView

urlpatterns = [
    path('orders/settlement/', OrderSettlementView.as_view()),
    # path('orders/commit/', OrderCommitView.as_view()),
    path('orders/commit/', CommitOrderView.as_view()),

]