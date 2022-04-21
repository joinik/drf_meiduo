from django.urls import path


from apps.verifications.views import ImageCodeView, MsmCodeView

urlpatterns = [
    path('image_codes/<uuid>/', ImageCodeView.as_view()),
    path('sms_codes/<mobile>/', MsmCodeView.as_view()),
]


