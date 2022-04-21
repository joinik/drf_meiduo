from django.urls import path

from apps.meiduo_admin.login import admin_jwt_token_view

urlpatterns = [
    path('authorizations/', admin_jwt_token_view),
]