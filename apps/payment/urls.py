



from django.urls import path, re_path
from apps.payment.views import PaymentView

urlpatterns = [
    re_path('payment/(?P<order_id>\d+)/', PaymentView.as_view()),
    # path("payment/status/", PaymentStatusView.as_view())

]