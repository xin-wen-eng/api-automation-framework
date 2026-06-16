#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/29 14:57
Description: Send email
"""

import smtplib
from email.mime.text import MIMEText
from utils.other_tools.allure_data.allure_report_data import TestMetrics, AllureFileClean
from utils import config


class SendEmail:
    """ Send email """
    def __init__(self, metrics: TestMetrics):
        self.metrics = metrics
        self.allure_data = AllureFileClean()
        self.CaseDetail = self.allure_data.get_failed_cases_detail()

    @classmethod
    def send_mail(cls, user_list: list, sub, content: str) -> None:
        """

        @param user_list: Sender email address
        @param sub:
        @param content: Content to send
        @return:
        """
        user = "Xin Wen" + "<" + config.email.send_user + ">"
        message = MIMEText(content, _subtype='plain', _charset='utf-8')
        message['Subject'] = sub
        message['From'] = user
        message['To'] = ";".join(user_list)
        server = smtplib.SMTP()
        server.connect(config.email.email_host)
        server.login(config.email.send_user, config.email.stamp_key)
        server.sendmail(user, user_list, message.as_string())
        server.close()

    def error_mail(self, error_message: str) -> None:
        """
        Email notification for execution exceptions
        @param error_message: Error information
        @return:
        """
        email = config.email.send_list
        user_list = email.split(',')  # For multiple email recipients, add directly in the config file  '806029174@qq.com'

        sub = config.project_name + " API Automation Execution Exception Notification"
        content = f"Automation test execution complete. An exception was found in the program, please be advised. Error details are as follows:\n{error_message}"
        self.send_mail(user_list, sub, content)

    def send_main(self) -> None:
        """
        Send email
        :return:
        """
        email = config.email.send_list
        user_list = email.split(',')  # For multiple email recipients, add directly in the yaml file  '806029174@qq.com'

        sub = config.project_name + " API Automation Report"
        content = f"""
        Dear colleagues, hello:
            Automation test cases have finished executing. The results are as follows:
            Total cases run: {self.metrics.total}
            Passed cases: {self.metrics.passed}
            Failed cases: {self.metrics.failed}
            Broken cases: {self.metrics.broken}
            Skipped cases: {self.metrics.skipped}
            Pass rate: {self.metrics.pass_rate} %

        {self.allure_data.get_failed_cases_detail()}

        **********************************
        Jenkins address: https://121.xx.xx.47:8989/login
        For details, please log in to the Jenkins platform. Personnel not involved may disregard this message. Thank you.
        """
        self.send_mail(user_list, sub, content)


if __name__ == '__main__':
    SendEmail(AllureFileClean().get_case_count()).send_main()
