#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:30
"""
DingTalk notification wrapper
"""
import base64
import hashlib
import hmac
import time
import urllib.parse
from typing import Any, Text
from dingtalkchatbot.chatbot import DingtalkChatbot, FeedLink
from utils.other_tools.get_local_ip import get_host_ip
from utils.other_tools.allure_data.allure_report_data import AllureFileClean, TestMetrics
from utils import config


class DingTalkSendMsg:
    """ Send DingTalk notification """
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.timeStamp = str(round(time.time() * 1000))

    def xiao_ding(self):
        sign = self.get_sign()
        # Get DingTalk configuration from yaml file
        webhook = config.ding_talk.webhook + "&timestamp=" + self.timeStamp + "&sign=" + sign
        return DingtalkChatbot(webhook)

    def get_sign(self) -> Text:
        """
        Generate secret key based on timestamp + "sign"
        :return:
        """
        string_to_sign = f'{self.timeStamp}\n{config.ding_talk.secret}'.encode('utf-8')
        hmac_code = hmac.new(
            config.ding_talk.secret.encode('utf-8'),
            string_to_sign,
            digestmod=hashlib.sha256).digest()

        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return sign

    def send_text(
            self,
            msg: Text,
            mobiles=None
    ) -> None:
        """
        Send text message
        :param msg: text content
        :param mobiles: phone numbers to mention
        :return:
        """
        if not mobiles:
            self.xiao_ding().send_text(msg=msg, is_at_all=True)
        else:
            if isinstance(mobiles, list):
                self.xiao_ding().send_text(msg=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles type error, not a list type.")

    def send_link(
            self,
            title: Text,
            text: Text,
            message_url: Text,
            pic_url: Text
    ) -> None:
        """
        Send link notification
        :return:
        """
        self.xiao_ding().send_link(
                title=title,
                text=text,
                message_url=message_url,
                pic_url=pic_url
            )

    def send_markdown(
            self,
            title: Text,
            msg: Text,
            mobiles=None,
            is_at_all=False
    ) -> None:
        """

        :param is_at_all:
        :param mobiles:
        :param title:
        :param msg:
        markdown format
        """

        if mobiles is None:
            self.xiao_ding().send_markdown(title=title, text=msg, is_at_all=is_at_all)
        else:
            if isinstance(mobiles, list):
                self.xiao_ding().send_markdown(title=title, text=msg, at_mobiles=mobiles)
            else:
                raise TypeError("mobiles type error, not a list type.")

    @staticmethod
    def feed_link(
            title: Text,
            message_url: Text,
            pic_url: Text
    ) -> Any:
        """ FeedLink secondary wrapper """
        return FeedLink(
            title=title,
            message_url=message_url,
            pic_url=pic_url
        )

    def send_feed_link(self, *arg) -> None:
        """Send feed_link """

        self.xiao_ding().send_feed_card(list(arg))

    def send_ding_notification(self):
        """ Send DingTalk report notification """
        # If there are failed test cases, mention everyone
        is_at_all = False
        if self.metrics.failed + self.metrics.broken > 0:
            is_at_all = True
        text = f"#### {config.project_name} Automation Notification  " \
               f"\n\n>Python Script Task: {config.project_name}" \
               f"\n\n>Environment: TEST\n\n>" \
               f"Executor: {config.tester_name}" \
               f"\n\n>Execution Result: {self.metrics.pass_rate}% " \
               f"\n\n>Total Cases: {self.metrics.total} " \
               f"\n\n>Passed Cases: {self.metrics.passed}" \
               f" \n\n>Failed Cases: {self.metrics.failed} " \
               f" \n\n>Broken Cases: {self.metrics.broken} " \
               f"\n\n>Skipped Cases: {self.metrics.skipped}" \
               f" ![screenshot](" \
               f"https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png" \
               f")\n" \
               f" > ###### Test Report [Details](http://{get_host_ip()}:9999/index.html) \n"
        DingTalkSendMsg(AllureFileClean().get_case_count()).send_markdown(
            title="[API Automation Notification]",
            msg=text,
            is_at_all=is_at_all
        )


if __name__ == '__main__':
    DingTalkSendMsg(AllureFileClean().get_case_count()).send_ding_notification()
