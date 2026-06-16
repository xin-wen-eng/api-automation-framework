"""
Send Lark notification
"""
import json
import logging
import time
import datetime
import requests
import urllib3
from utils.other_tools.allure_data.allure_report_data import TestMetrics
from utils import config


urllib3.disable_warnings()

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


def is_not_null_and_blank_str(content):
    """
  Non-empty string
  :param content: string
  :return: non-empty - True, empty - False
  """
    return bool(content and content.strip())


class FeiShuTalkChatBot:
    """Lark bot notification"""
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics

    def send_text(self, msg: str):
        """
    Message type is text
    :param msg: message content
    :return: returns the message sending result
    """
        data = {"msg_type": "text", "at": {}}
        if is_not_null_and_blank_str(msg):  # incoming msg is non-empty
            data["content"] = {"text": msg}
        else:
            logging.error("text type, message content cannot be empty!")
            raise ValueError("text type, message content cannot be empty!")

        logging.debug('text type: %s', data)
        return self.post()

    def post(self):
        """
    Send message (content UTF-8 encoded)
    :return: returns the message sending result
    """
        rich_text = {
            "email": "1603453211@qq.com",
            "msg_type": "post",
            "content": {
                "post": {
                    "zh_cn": {
                        "title": "[Automation Test Notification]",
                        "content": [
                            [
                                {
                                    "tag": "a",
                                    "text": "Test Report",
                                    "href": "https://192.168.xx.72:8080"
                                },
                                {
                                    "tag": "at",
                                    "user_id": "ou_18eac85d35a26f989317ad4f02e8bbbb"
                                    # "text":"Chen Ruinan"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "Tester       : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{config.tester_name}"
                                }
                            ],
                            [
                                {
                                    "tag": "text",
                                    "text": "Environment  : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{config.env}"
                                }
                            ],
                            [{
                                "tag": "text",
                                "text": "Pass    Rate  : "
                            },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.pass_rate} %"
                                }],  # pass rate

                            [{
                                "tag": "text",
                                "text": "Passed Cases : "
                            },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.passed}"
                                }],  # number of passed cases

                            [{
                                "tag": "text",
                                "text": "Failed Cases : "
                            },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.failed}"
                                }],  # number of failed cases
                            [{
                                "tag": "text",
                                "text": "Error  Cases : "
                            },
                                {
                                    "tag": "text",
                                    "text": f"{self.metrics.failed}"
                                }],  # number of broken cases
                            [
                                {
                                    "tag": "text",
                                    "text": "Time         : "
                                },
                                {
                                    "tag": "text",
                                    "text": f"{datetime.datetime.now().strftime('%Y-%m-%d')}"
                                }
                            ],

                            [
                                {
                                    "tag": "img",
                                    "image_key": "d640eeea-4d2f-4cb3-88d8-c964fab53987",
                                    "width": 300,
                                    "height": 300
                                }
                            ]
                        ]
                    }
                }
            }
        }
        headers = {'Content-Type': 'application/json; charset=utf-8'}

        post_data = json.dumps(rich_text)
        response = requests.post(
                config.lark.webhook,
                headers=headers,
                data=post_data,
                verify=False
        )
        result = response.json()

        if result.get('StatusCode') != 0:
            time_now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            result_msg = result['errmsg'] if result.get('errmsg', False) else 'Unknown error'
            error_data = {
                "msgtype": "text",
                "text": {
                            "content": f"[Notice-Auto Notification] Lark bot message sending failed, time: {time_now}, "
                                       f"reason: {result_msg}, please follow up promptly, thank you!"
                },
                "at": {
                            "isAtAll": False
                        }
                    }
            logging.error("Message sending failed, auto notification: %s", error_data)
            requests.post(config.lark.webhook, headers=headers, data=json.dumps(error_data))
        return result
