from alipay import AliPay, AliPayConfig
from django.conf import settings
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import render

# Create your views here.
from django.views import View
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.orders.models import OrderInfo
from apps.payment.models import Payment
from utils.viewsMixin import LoginRequiredJSONMixin

"""支付宝支付视图"""
class PaymentView(APIView):
    """订单支付功能"""
    permission_classes = [IsAuthenticated]
    def get(self, request, order_id):
        # 查询要支付的订单

        user = request.user
        try:
            order = OrderInfo.objects.get(order_id=order_id, user=user, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID'])

        except OrderInfo.DoesNotExist:
            return Response({'message': '订单有误'}, status=status.HTTP_400_BAD_REQUEST)


        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 创建支付宝对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥，
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',
            debug=True,
            verbose=True,   # 是否输出
            config=AliPayConfig(timeout=15),  # 操作时间
        )


        print("执行》》》》》》》")

        # 生成登录支付宝连接
        # 3.0 接口方法
        order_string = alipay.client_api(
            "alipay.trade.page.pay",
            biz_content={
                "subject": "美多商城%s" % order_id,
                "out_trade_no": order_id,
                "total_amount": str(order.total_amount),
                "product_code": "FAST_INSTANT_TRADE_PAY",
            },
            return_url=settings.ALIPAY_RETURN_URL,
        )

        # 响应登录支付宝连接
        # 真实环境电脑网站支付网关：https://openapi.alipay.com/gateway.do? + order_string
        # 沙箱环境电脑网站支付网关：https://openapi.alipaydev.com/gateway.do? + order_string
        alipay_url = settings.ALIPAY_URL + "?" + order_string
        # print("alipay_url")
        # print(alipay_url)
        return Response({'code': 0, 'errmsg': 'OK', 'alipay_url': alipay_url})



"""支付状态"""
class PaymentStatusView(APIView):
    def put(self, request):

        # 获取前端以查询字符串方式传入的数据
        queryDict = request.query_params
        # 将queryDict类型转换成字典(要将中间的sign 从里面移除,然后进行验证)
        data = queryDict.dict()
        # 将sign这个数据从字典中移除
        sign = data.pop('sign')

        # 创建alipay支付宝对象
        app_private_key_string = open(settings.APP_PRIVATE_KEY_PATH).read()
        alipay_public_key_string = open(settings.ALIPAY_PUBLIC_KEY_PATH).read()
        # 创建支付宝对象
        alipay = AliPay(
            appid=settings.ALIPAY_APPID,
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥，
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',
            debug=True,
            verbose=True,  # 是否输出
            config=AliPayConfig(timeout=15),  # 操作时间
        )
        # 调用alipay SDK中  的verify方法进行验证支付结果是否支付宝回传回来的
        success = alipay.verify(data, sign)
        if success:
            # 取出美多商城订单编号  再取出支付宝交易号
            order_id = data.get('out_trade_no')  # 美多订单编号
            trade_no = data.get('trade_no')  # 支付宝交易号
            # 把两个编号绑定到一起存储mysql
            Payment.objects.create(
                order_id=order_id,
                trade_id=trade_no
            )
            # 修改支付成功后的订单状态
            OrderInfo.objects.filter(order_id=order_id, status=OrderInfo.ORDER_STATUS_ENUM['UNPAID']).update(
                status=OrderInfo.ORDER_STATUS_ENUM['UNSEND'])
        else:
            return Response({'message': '非法请求'}, status=status.HTTP_403_FORBIDDEN)

        # 把支付宝交易响应回给前端
        return Response({'trade_id': trade_no})


