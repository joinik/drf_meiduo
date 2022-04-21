

from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, jwt_payload_handler, jwt_encode_handler
from django.utils.translation import ugettext as _
from rest_framework_jwt.views import JSONWebTokenAPIView




class AdminJSONWebTokenSerializer(JSONWebTokenSerializer):
    """
    Serializer class used to validate a username and password.

    'username' is identified by the custom UserModel.USERNAME_FIELD.

    Returns a JSON Web Token that can be used to authenticate later calls.
    """
    def validate(self, attrs):
        credentials = {
            self.username_field: attrs.get(self.username_field),
            'password': attrs.get('password')
        }

        if all(credentials.values()):
            user = authenticate(**credentials)

            if user:
                if not user.is_active:
                    msg = _('User account is disabled.')
                    raise serializers.ValidationError(msg)

                # 判断 是否 管理员
                # if not user.is_staff:
                #     msg = _('User account is not staff.')
                #     raise serializers.ValidationError(msg)

                payload = jwt_payload_handler(user)

                return {
                    'token': jwt_encode_handler(payload),
                    'user': user
                }
            else:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg)
        else:
            msg = _('Must include "{username_field}" and "password".')
            msg = msg.format(username_field=self.username_field)
            raise serializers.ValidationError(msg)






class AdminJSONWebTokenView(JSONWebTokenAPIView):
    """
    API View that receives a POST with a user's username and password.

    Returns a JSON Web Token that can be used for authenticated requests.
    """
    # 修改序列化器为AdminJSONWebTokenSerializer
    serializer_class = AdminJSONWebTokenSerializer


# 生成对应的AdminJSONWebTokenView的视图
admin_jwt_token_view = AdminJSONWebTokenView.as_view()

