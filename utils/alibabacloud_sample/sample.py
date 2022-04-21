# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import sys

from typing import List
from Tea.core import TeaCore

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_console.client import Client as ConsoleClient

from alibabacloud_tea_util.client import Client as UtilClient


class Sample:

    def __new__(cls, *args, **kwargs):
        # if cls._instance is None:
        #     cls._instance = super().__new__(cls, *args, **kwargs)

        if not hasattr(Sample, "_instance"):  # 是否有_instance属性
            cls._instance = super().__new__(cls, *args, **kwargs)
            # 创建一个SmsSDK对象 这里只执行一次 所以SmsSDK对象只有一个
            cls._instance.sms_sdk = SmsSDK(accId, accToken, appId)

        return cls._instance

    def __init__(self):
        pass

    @staticmethod
    def create_client(
        access_key_id: str,
        access_key_secret: str,
    ) -> Dysmsapi20170525Client:
        """
        使用AK&SK初始化账号Client
        @param access_key_id:
        @param access_key_secret:
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            # 您的AccessKey ID,
            access_key_id="LTAI5tAfx7Crx9gGSFSwNHwC",
            # 您的AccessKey Secret,
            access_key_secret="kOpFsFFar3CYyNCEWxjqOQuoUVJwbV"
        )
        # 访问的域名
        config.endpoint = 'dysmsapi.aliyuncs.com'
        return Dysmsapi20170525Client(config)

    @staticmethod
    def main(
        args: List[str],
    ) -> None:
        client = Sample.create_client('ACCESS_KEY_ID', 'ACCESS_KEY_SECRET')
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=args[0],
            sign_name=args[1],
            template_code=args[2]
        )
        resp = client.send_sms(send_sms_request)
        ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))

    @staticmethod
    async def main_async(
        args: List[str],
    ) -> None:
        client = Sample.create_client('ACCESS_KEY_ID', 'ACCESS_KEY_SECRET')
        send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
            phone_numbers=args[0],
            sign_name=args[1],
            template_code=args[2]
        )
        resp = await client.send_sms_async(send_sms_request)
        print(">>>>>>")
        print(resp.body)
        # ConsoleClient.log(UtilClient.to_jsonstring(TeaCore.to_map(resp)))


if __name__ == '__main__':
    Sample.main_async(["17708764930", "meiduo个人", "DjangoTest01"])
    # Sample.main(sys.argv[1:])
