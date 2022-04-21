from rest_framework import serializers

from apps.areas.models import Area


class AreaSerializer(serializers.ModelSerializer):
    """省的序列化器?"""

    class Meta:
        model = Area
        fields = ['id', 'name']


class SubsSerializer(serializers.ModelSerializer):
    # 130000
    # 河北省模型.subs.all()
    """详情视图使用的序列化器"""
    subs = AreaSerializer(many=True)
    # subs = serializers.PrimaryKeyRelatedField()  # 只会序列化出 id
    # subs = serializers.StringRelatedField()  # 序列化的时模型中str方法返回值
    class Meta:
        model = Area
        fields = ['id', 'name', 'subs']





