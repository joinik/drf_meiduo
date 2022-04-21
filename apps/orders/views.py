import json
from decimal import Decimal

from django.db import transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render

# Create your views here.
from django.utils import timezone
from django.views import View
from django_redis import get_redis_connection

from apps.areas.views import logger
from apps.goods.models import SKU
from apps.orders.models import OrderInfo, OrderGoods
from apps.users.models import Address
from utils.viewsMixin import LoginRequiredJSONMixin

from django.shortcuts import render
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from decimal import Decimal
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from apps.goods.models import SKU
from .serializers import OrderSettlementSerializer, CommitOrderSerializer


# Create your views here.

class OrderSettlementView(APIView):
    """去结算"""

    permission_classes = [IsAuthenticated]  # 指定权限,必须是登录用户才能访问此视图中的接口

    def get(self, request):

        # 创建redis连接对象
        redis_conn = get_redis_connection('carts')
        # 获取user对象
        user = request.user
        # huq

        # 获取redis中hash和set两个数据
        cart_dict_redis = redis_conn.hgetall('carts_%d' % user.id)
        selected_ids = redis_conn.smembers('selected_%d' % user.id)

        # 定义一个字典用来保存勾选的商品及count
        cart_dict = {}  # {1: 2, 16: 1}
        # 把hash中那些勾选商品的sku_id和count取出来包装到一个新字典中
        for sku_id_bytes in selected_ids:
            cart_dict[int(sku_id_bytes)] = int(cart_dict_redis[sku_id_bytes])

        try:
            # 把勾选商品的sku模型再获取出来
            skus = SKU.objects.filter(id__in=cart_dict.keys())

        except Exception as e:
            print(e)
            return Response({'code': 400,
                             'errmsg': '数据查询失败'})

        # 遍历skus 查询集取出一个一个的sku模型
        for sku in skus:
            # 给每个sku模型多定义一个count属性
            sku.count = cart_dict[sku.id]

        # 定义一运费
        freight = Decimal('10.00')

        data_dict = {'freight': freight, 'skus': skus}  # 序列化时,可以对 单个模型/查询集/列表/字典 都可以进行序列化器()
        # 创建序列化器进行序列化
        serializer = OrderSettlementSerializer(data_dict)

        return Response(serializer.data)


class CommitOrderView(CreateAPIView):
    """保存订单"""

    serializer_class = CommitOrderSerializer

    # 指定权限
    permission_classes = [IsAuthenticated]

# class OrderSettlementView(LoginRequiredJSONMixin, View):
#     """结算订单"""
#
#     def get(self, request):
#         """提供订单结算页面"""
#
#         # 登录的用户
#         user = request.user
#
#         # 获取所有 地址信息
#         addresses = Address.objects.filter(user=user, is_deleted=False)
#
#         # 从redis 购物车中查询被勾选的商品信息
#         redis_conn = get_redis_connection('carts')
#         #  redis_hash 获取所有的商品 信息
#         redis_cart = redis_conn.hgetall("carts_%s" % user.id)
#         #  redis_set 获取所有的商品 选中 信息
#         cart_selected = redis_conn.smembers('selected_%s' % user.id)
#
#         cart = {}
#
#         for sku_id in cart_selected:
#             cart[int(sku_id)] = int(redis_cart[sku_id])
#
#         # 查询商品信息
#         sku_list = []
#         skus = SKU.objects.filter(id__in=cart.keys())
#         for sku in skus:
#             sku_list.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'default_image_url': sku.default_image.url,
#                 'count': cart[sku.id],
#                 'price': sku.price
#             })
#
#         # 补充运费
#         freight = Decimal('10.00')
#
#         # 地址信息
#         addresses_list = []
#         for address in addresses:
#             addresses_list.append({
#                 'id': address.id,
#                 'province': address.province.name,
#                 'city': address.city.name,
#                 'district': address.district.name,
#                 'place': address.place,
#                 'receiver': address.receiver,
#                 'mobile': address.mobile
#             })
#
#         # 渲染界面
#         context = {
#             'addresses': addresses_list,
#             'skus': sku_list,
#             'freight': str(freight),
#         }
#
#         return JsonResponse({'code': 0,
#                              'errmsg': 'ok',
#                              'context': context})
#
#
# class OrderCommitView(LoginRequiredJSONMixin, View):
#     """订单提交"""
#
#     def post(self, request):
#         """保存订单信息和订单商品信息"""
#         # 获取当前要保存的订单数据
#         json_dict = json.loads(request.body.decode())
#         address_id = json_dict.get('address_id')
#         pay_method = json_dict.get('pay_method')
#         # 校验参数
#         if not all([address_id, pay_method]):
#             return HttpResponseBadRequest('缺少必传参数')
#         # 判断address_id是否合法
#         try:
#             address = Address.objects.get(id=address_id)
#         except Exception:
#             return HttpResponseBadRequest('参数address_id错误')
#         # 判断pay_method是否合法
#         if pay_method not in [OrderInfo.PAY_METHODS_ENUM['CASH'], OrderInfo.PAY_METHODS_ENUM['ALIPAY']]:
#             return HttpResponseBadRequest('参数pay_method错误')
#
#         # 获取登录用户
#         user = request.user
#         # 生成订单编号：年月日时分秒+用户编号
#         # 以Django setting 时区的时间
#         order_id = timezone.localtime().strftime('%Y%m%d%H%M%S') + ('%09d' % user.id)
#         # status = OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
#         #     'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
#         # print(status)
#         # 显式的开启一个事务
#         with transaction.atomic():
#             # 创建事务保存点
#             save_id = transaction.savepoint()
#
#             # 暴力回滚
#             try:
#
#
#                 # 保存订单基本信息 OrderInfo（一）
#                 order = OrderInfo.objects.create(
#                     order_id=order_id,
#                     user=user,
#                     address=address,
#                     total_count=0,
#                     total_amount=Decimal('0'),
#                     freight=Decimal('10.00'),
#                     pay_method=pay_method,
#                     # 如果是支付宝 那么状态就是待付款 否则是待发货
#                     status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'] if pay_method == OrderInfo.PAY_METHODS_ENUM[
#                         'ALIPAY'] else OrderInfo.ORDER_STATUS_ENUM['UNSEND']
#                 )
#                 print(order)
#
#             except Exception as e:
#                 print(e)
#                 return HttpResponseBadRequest('订单保存失败')
#
#             try:
#                 # 从redis读取购物车中被勾选的商品信息
#                 redis_conn = get_redis_connection('carts')
#                 redis_cart = redis_conn.hgetall('carts_%s' % user.id)
#                 selected = redis_conn.smembers('selected_%s' % user.id)
#                 carts = {}
#                 for sku_id in selected:
#                     carts[int(sku_id)] = int(redis_cart[sku_id])
#                 sku_ids = carts.keys()
#
#                 try:
#                     # new_cart_dict 是所有选中的商品的id和数量 并且是转为int后的
#                     skus = SKU.objects.filter(id__in=sku_ids)
#                 except Exception as e:
#                     # 回滚到保存点
#                     transaction.savepoint_rollback(save_id)
#                     print(e)
#                     return JsonResponse({'code': 400,
#                                          'errmsg': '数据查询失败'})
#
#                 # 遍历购物车中被勾选的商品信息
#                 for sku in skus:
#                     while True:
#                         # 读取原始库存
#                         origin_stock = sku.stock
#                         origin_sales = sku.sales
#
#                         # 判断SKU库存
#                         sku_count = carts[sku.id]
#                         if sku_count > sku.stock:
#                             # 回滚到保存点
#                             print("回滚")
#                             transaction.savepoint_rollback(save_id)
#                             return JsonResponse({'code': 400, 'errmsg': '库存不足'})
#
#                         # # SKU减少库存，增加销量
#                         # sku.stock -= sku_count
#                         # sku.sales += sku_count
#                         # sku.save()
#
#                         # 乐观锁更新库存和销量
#                         new_stock = origin_stock - sku_count
#                         new_sales = origin_sales + sku_count
#                         result = SKU.objects.filter(id=sku_id, stock=origin_stock).update(stock=new_stock, sales=new_sales)
#                         # 如果下单失败，但是库存足够时，继续下单，直到下单成功或者库存不足为止
#                         if result == 0:
#                             continue
#
#                         # 保存订单商品信息 OrderGoods（多）
#                         OrderGoods.objects.create(
#                             order=order,
#                             sku=sku,
#                             count=sku_count,
#                             price=sku.price,
#                         )
#
#                         # 保存商品订单中总价和总数量
#                         order.total_count += sku_count
#                         order.total_amount += (sku_count * sku.price)
#
#                         # 下单成功或者失败就跳出循环
#                         break
#
#                 # 添加邮费和保存订单信息
#                 order.total_amount += order.freight
#                 order.save()
#
#             except Exception as e:
#                 logger.error(e)
#                 transaction.savepoint_rollback(save_id)
#                 return JsonResponse({'code': 400, 'errmsg': '下单失败'})
#             # 提交订单成功，显式的提交一次事务
#             transaction.savepoint_commit(save_id)
#         # 清除购物车中已结算的商品
#         pl = redis_conn.pipeline()
#         pl.hdel('carts_%s' % user.id, *selected)
#         pl.srem('selected_%s' % user.id, *selected)
#         pl.execute()
#
#         # 响应提交订单结果
#         return JsonResponse({'code': 0, 'errmsg': '下单成功', 'order_id': order.order_id})
