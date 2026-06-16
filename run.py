#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 15:01
import os
import sys
import traceback
import pytest
from utils.other_tools.models import NotificationType
from utils.other_tools.allure_data.allure_report_data import AllureFileClean
from utils.logging_tool.log_control import INFO
from utils.notify.wechat_send import WeChatSend
from utils.notify.ding_talk import DingTalkSendMsg
from utils.notify.send_mail import SendEmail
from utils.notify.lark import FeiShuTalkChatBot
from utils.other_tools.allure_data.error_case_excel import ErrorCaseExcel
from utils import config


def run():
    # Get the project name from the configuration file
    try:
        INFO.logger.info(
            """
                             _    _         _      _____         _
              __ _ _ __ (_)  / \\  _   _| |_ __|_   _|__  ___| |_
             / _` | '_ \\| | / _ \\| | | | __/ _ \\| |/ _ \\/ __| __|
            | (_| | |_) | |/ ___ \\ |_| | || (_) | |  __/\\__ \\ |_
             \\__,_| .__/|_/_/   \\_\\__,_|\\__\\___/|_|\\___||___/\\__|
                  |_|
                  Starting execution of {} project...
                """.format(config.project_name)
        )

        # Check existing test cases; if test code has not been generated, generate it automatically
        # TestCaseAutomaticGeneration().get_case_automatic()

        pytest.main(['-s', '-W', 'ignore:Module already imported:pytest.PytestWarning',
                     '--alluredir', './report/tmp', "--clean-alluredir"])

        """
                   --reruns: number of times to re-run on failure
                   --count: number of times to repeat execution
                   -v: display error location and detailed error information
                   -s: equivalent to pytest --capture=no, can capture output of print functions
                   -q: simplify output information
                   -m: run test cases with specified tags
                   -x: stop running immediately on error
                   --maxfail: set maximum failure count; when this threshold is exceeded, test cases will no longer be executed
                    "--reruns=3", "--reruns-delay=2"
                   """

        os.system(r"allure generate ./report/tmp -o ./report/html --clean")

        allure_data = AllureFileClean().get_case_count()
        notification_mapping = {
            NotificationType.DING_TALK.value: DingTalkSendMsg(allure_data).send_ding_notification,
            NotificationType.WECHAT.value: WeChatSend(allure_data).send_wechat_notification,
            NotificationType.EMAIL.value: SendEmail(allure_data).send_main,
            NotificationType.FEI_SHU.value: FeiShuTalkChatBot(allure_data).post
        }

        if config.notification_type != NotificationType.DEFAULT.value:
            notification_mapping.get(config.notification_type)()

        if config.excel_report:
            ErrorCaseExcel().write_case()

        # After the program runs, automatically launch the report. If you do not want to launch the report, comment out this code
        os.system(f"allure serve ./report/tmp -h 127.0.0.1 -p 9999")

    except Exception:
        # If an exception occurs, send the relevant exception via email
        e = traceback.format_exc()
        send_email = SendEmail(AllureFileClean.get_case_count())
        send_email.error_mail(e)
        raise


if __name__ == '__main__':
    run()
