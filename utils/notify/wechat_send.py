#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/29 14:59
Description: Send Enterprise WeChat notification
"""

import requests
from utils.logging_tool.log_control import ERROR
from utils.other_tools.allure_data.allure_report_data import TestMetrics, AllureFileClean
from utils.times_tool.time_control import now_time
from utils.other_tools.get_local_ip import get_host_ip
from utils.other_tools.exceptions import SendMessageError, ValueTypeError
from utils import config


class WeChatSend:
    """
    Enterprise WeChat message notification
    """

    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.headers = {"Content-Type": "application/json"}

    def send_text(self, content, mentioned_mobile_list=None):
        """
        Send text type notification
        :param content: Text content, max length 2048 bytes, must be utf8 encoded
        :param mentioned_mobile_list: List of phone numbers to mention the corresponding group members (@someone), @all means mention everyone
        :return:
        """
        _data = {"msgtype": "text", "text": {"content": content, "mentioned_list": None,
                                             "mentioned_mobile_list": mentioned_mobile_list}}

        if mentioned_mobile_list is None or isinstance(mentioned_mobile_list, list):
            # Check the data type in the phone number list; if int type, the sent message will be garbled
            if len(mentioned_mobile_list) >= 1:
                for i in mentioned_mobile_list:
                    if isinstance(i, str):
                        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
                        if res.json()['errcode'] != 0:
                            ERROR.logger.error(res.json())
                            raise SendMessageError("Enterprise WeChat 'text type' message send failed")

                    else:
                        raise ValueTypeError("Phone number must be a string type.")
        else:
            raise ValueTypeError("Phone number list must be a list type.")

    def send_markdown(self, content):
        """
        Send MarkDown type message
        :param content: Message content in markdown format
        :return:
        """
        _data = {"msgtype": "markdown", "markdown": {"content": content}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError("Enterprise WeChat 'MarkDown type' message send failed")

    def _upload_file(self, file):
        """
        First upload the file to the temporary media library
        """
        key = config.wechat.webhook.split("key=")[1]
        url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type=file"
        data = {"file": open(file, "rb")}
        res = requests.post(url, files=data).json()
        return res['media_id']

    def send_file_msg(self, file):
        """
        Send file type message
        @return:
        """

        _data = {"msgtype": "file", "file": {"media_id": self._upload_file(file)}}
        res = requests.post(url=config.wechat.webhook, json=_data, headers=self.headers)
        if res.json()['errcode'] != 0:
            ERROR.logger.error(res.json())
            raise SendMessageError("Enterprise WeChat 'file type' message send failed")

    def send_wechat_notification(self):
        """ Send Enterprise WeChat notification """
        text = f"""[{config.project_name} Automation Notification]
                                    >Test Environment: <font color=\"info\">TEST</font>
                                    >Test Owner: @{config.tester_name}
                                    >
                                    > **Execution Results**
                                    ><font color=\"info\">Pass  Rate  : {self.metrics.pass_rate}%</font>
                                    >Total Cases: <font color=\"info\">{self.metrics.total}</font>
                                    >Passed Cases: <font color=\"info\">{self.metrics.passed}</font>
                                    >Failed Cases: `{self.metrics.failed}`
                                    >Broken Cases: `{self.metrics.broken}`
                                    >Skipped Cases: <font color=\"warning\">{self.metrics.skipped}</font>
                                    >Execution Duration: <font color=\"warning\">{self.metrics.time} s</font>
                                    >Time: <font color=\"comment\">{now_time()}</font>
                                    >
                                    >Non-related personnel may ignore this message.
                                    >Test report, click to view>>[Test Report Entry](http://{get_host_ip()}:9999/index.html)"""

        WeChatSend(AllureFileClean().get_case_count()).send_markdown(text)


if __name__ == '__main__':
    WeChatSend(AllureFileClean().get_case_count()).send_wechat_notification()
