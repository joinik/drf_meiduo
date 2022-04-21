import json
from typing import re

from django.core.cache import cache
from django.shortcuts import render

# Create your views here.

from django.http import JsonResponse, HttpResponseBadRequest
from django.views import View
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework_extensions.cache.mixins import CacheResponseMixin

from apps.areas.models import Area
import logging

from apps.areas.serializers import AreaSerializer, SubsSerializer
from apps.users.models import Address
from utils.viewsMixin import LoginRequiredJSONMixin

logger = logging.getLogger('django')

"""
查找省份
前端：用户选择省份或者市 发送请求， 获取下一级信息
后端；
    请求      传递省份，或者市的id
    逻辑      根据id 查area对象，获取下一级信息，转为字典数据
    返回响应; json
"""


# class AreasView(APIView):
#     """省市区数据"""
#
#     def get(self, request):
#         """提供省市区数据"""
#
#         # 判断缓存 里是否有 省份 数据
#         if cache.get('province_list'):
#             print('----------->>>>>>省份缓存')
#             return JsonResponse({'code': 0, 'errmsg': 'OK', 'province_list': cache.get('province_list')})
#
#         # 提供省份数据
#         try:
#             # 查询省份数据
#             # 1. 查询集
#
#             province_model_list = Area.objects.filter(parent__isnull=True)
#             # 2. 序列化器
#             serializers = AreaSerializer(province_model_list, many=True)
#             # 序列化省级数据
#             province_list = serializers.data
#
#         except Exception as e:
#             logger.error(e)
#             return Response({'errmsg': '省份数据错误'}, status=status.HTTP_400_BAD_REQUEST)
#         # 使用 缓存  省份数据
#         cache.set('province_list', province_list, 3600)
#         # 响应省份数据
#
#         return Response({'code': 0, 'errmsg': 'OK', 'province_list': province_list})
#
#
# """
# 查找市区
# 前端：用户选择省份或者市 发送请求， 获取下一级信息
# 后端；
#     请求      传递省份，或者市的id
#     逻辑      根据id 查area对象，获取下一级信息，转为字典数据
#     返回响应; json
# {
#   "code":"0",
#   "errmsg":"OK",
#   "sub_data":{
#       "id":130000,
#       "name":"河北省",
#       "subs":[
#           {
#               "id":130100,
#               "name":"石家庄市"
#           },
#           ......
#       ]
#   }
# }
# """
#
#
# class SubsView(View):
#     """省市区数据"""
#
#     def get(self, request, pk):
#         """提供省市区数据"""
#
#         # 判断缓存 里是否有 区县 数据
#         if cache.get('sub_data_' + pk):
#             print('>>>>>>>>>>市级缓存')
#             return JsonResponse({'code': 0, 'errmsg': 'OK', 'sub_data': cache.get('sub_data_' + pk)})
#         # 提供省份数据
#         try:
#             # 查询省份数据
#             parent_obj = Area.objects.get(id=pk)
#
#             # 获取下一级的所有数据
#             sub_objs = parent_obj.subs.all()
#
#             # 序列化市级数据
#             subs = []
#             for sub in sub_objs:
#                 subs.append({'id': sub.id, 'name': sub.name})
#         except Exception as e:
#             logger.error(e)
#             return JsonResponse({'code': 400, 'errmsg': '市级数据错误'})
#
#         # print(subs)
#         sub_data = {'id': pk, 'name': parent_obj.name, 'subs': subs}
#         cache.set('sub_data_' + pk, sub_data, 3600)
#         # 响应省份数据
#         return JsonResponse({'code': 0, 'errmsg': 'OK', 'sub_data': sub_data})

class AreaViewSet(CacheResponseMixin, ReadOnlyModelViewSet):

    # queryset = Area.objects.all()

    pagination_class = None  # 禁用分页
    # 指定查询集

    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    # 指定序列化器
    # serializer_class =

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaSerializer
        else:
            return SubsSerializer





"""
添加收货地址
前端：用户输入地址信息， 点击保存  发送area id 发送axios请求 
后端：
    接收请求：
    路由；POST /addresses/create/
    业务逻辑：
    响应：
    

"""


class CreateAddressView(LoginRequiredJSONMixin, View):
    def post(self, request):
        dict_body = json.loads(request.body)

        # 2 提取参数
        receiver = dict_body.get('receiver')
        province_id = dict_body.get('province_id')
        city_id = dict_body.get('city_id')
        district_id = dict_body.get('district_id')
        place = dict_body.get('place')
        mobile = dict_body.get('mobile')
        tel = dict_body.get('tel')
        email = dict_body.get('email')
        print(receiver, province_id, city_id, district_id, place, mobile, )
        # 3 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile, ]):
            return JsonResponse({'code': 0, 'errmsg': '参数不全'})

        # if not re.match(r'^1[345789]\d{9}$', mobile):
        #     return JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})
        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400, 'errmsg': '参数email有误'})

        print('----------------------')
        # 4. 数据库保存数据
        try:
            address = Address.objects.create(user=request.user,
                                             title=receiver,
                                             receiver=receiver,
                                             province_id=province_id,
                                             city_id=city_id,
                                             district_id=district_id,
                                             place=place,
                                             mobile=mobile,
                                             tel=tel,
                                             email=email)
            print('s数据库操作')
            print(address)


        except Exception as e:
            print('地址存入数据库失败')
            return JsonResponse({'code': 400, 'errmsg': 'fail'})

        # 拼接数据
        address_dict = {
            "id": address.id,
            "title": address.title,
            "receiver": address.receiver,
            "province": address.province.name,
            "city": address.city.name,
            "district": address.district.name,
            "place": address.place,
            "mobile": address.mobile,
            "tel": address.tel,
            "email": address.email
        }
        print('address_dict 数据')
        print(address_dict)
        # 5。返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})


"""
展示用户所有的地址数据
前端； 用户界面
"""


class ShowAddressView(LoginRequiredJSONMixin, View):
    def get(self, request):
        # 获取地址信息
        addresses = Address.objects.filter(user=request.user, is_deleted=False)

        # 获取用户的所有地址信息
        addresses_list = []
        for address in addresses:
            addresses_list.append({
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            })
        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'addresses': addresses_list})


"""
删除地址
前端 用户输入地址信息，点击修改 ，发送axios请求
后端
    接收请求： 接收参数   
    业务逻辑：
            验证参数
            进行数据库修改
            返回响应 
    返回响应  json 格式
"""


class DeleteAddressView(LoginRequiredJSONMixin, View):
    def delete(self, request, add_id):
        try:
            # 根据id 查询 address对象
            address = Address.objects.get(id=add_id)
            # 进行 数据库操作
            # 将地址逻辑删除设置为True
            address.is_deleted = True
            address.save()

        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '数据删除地址fail'})

        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})

    # 修改地址信息
    def put(self, request, add_id):

        dict_body = json.loads(request.body)

        # 2 提取参数
        receiver = dict_body.get('receiver')
        province_id = dict_body.get('province_id')
        city_id = dict_body.get('city_id')
        district_id = dict_body.get('district_id')
        place = dict_body.get('place')
        mobile = dict_body.get('mobile')
        tel = dict_body.get('tel')
        email = dict_body.get('email')
        print(receiver, province_id, city_id, district_id, place, mobile, )
        # 3 校验参数
        if not all([receiver, province_id, city_id, district_id, place, mobile, ]):
            return JsonResponse({'code': 0, 'errmsg': '参数不全'})

        rest = re.match(r'^1[3-9]\d{9}$', mobile)
        print(rest.group())
        if not rest:
            return JsonResponse({'code': 400, 'errmsg': '参数mobile有误'})

        if tel:
            if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                return JsonResponse({'code': 400, 'errmsg': '参数tel有误'})
        if email:
            if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                return JsonResponse({'code': 400, 'errmsg': '参数email有误'})

        # 4. 数据库保存数据
        try:
            print('地址数据库修改--------')

            Address.objects.filter(user=request.user, id=add_id).update(title=receiver,
                                                                        receiver=receiver,
                                                                        province_id=province_id,
                                                                        city_id=city_id,
                                                                        district_id=district_id,
                                                                        place=place,
                                                                        mobile=mobile,
                                                                        tel=tel,
                                                                        email=email)
            # 拼接数据
            address = Address.objects.get(id=add_id)
            address_dict = {
                "id": address.id,
                "title": address.title,
                "receiver": address.receiver,
                "province": address.province.name,
                "city": address.city.name,
                "district": address.district.name,
                "place": address.place,
                "mobile": address.mobile,
                "tel": address.tel,
                "email": address.email
            }


        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '地址更新fail'})


        print('address_dict 数据')
        print(address_dict)
        # 5。返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok', 'address': address_dict})


"""
设置默认地址
前端 用户，点击设置 ，发送axios请求
后端
    接收请求： 接收参数   address_id
    业务逻辑：
            验证参数
            进行数据库修改
            返回响应 
    返回响应  json 格式
"""


class DefaultAddressView(LoginRequiredJSONMixin, View):
    def put(self, request, add_id):
        try:
            # 根据id 查询 address对象
            address = Address.objects.get(id=add_id)
            # 进行 默认地址设置
            request.user.default_address = address
            request.user.save()

        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': 'fail'})

        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})


class UpdateTitleView(View):
    def put(self,request,add_id):
        # 接收参数 title
        body_dict = json.loads(request.body)
        title = body_dict.get('title')
        try:
            # 根据 add_id 查询数据库对象address
            address = Address.objects.get(id = add_id)

            # 进行数据库修改
            address.title = title
            address.save()
        except Exception as e:
            print(e)
            return JsonResponse({'code': 400, 'errmsg': '地址title fail'})

        # 返回响应
        return JsonResponse({'code': 0, 'errmsg': 'ok'})



