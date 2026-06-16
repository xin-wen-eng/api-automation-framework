#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/8 21:37
# @Email   : 1603453211@qq.com
# @File    : error_case_excel
# @describe:
"""

import json
import shutil
import ast
import xlwings
from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.notify.wechat_send import WeChatSend
from utils.other_tools.allure_data.allure_report_data import AllureFileClean


# TODO still needs to handle dynamic values
class ErrorTestCase:
    """ Collect error excel cases """
    def __init__(self):
        self.test_case_path = ensure_path_sep("\\report\\html\\data\\test-cases\\")

    def get_error_case_data(self):
        """
        Collect data for all failed test cases
        @return:
        """
        path = get_all_files(self.test_case_path)
        files = []
        for i in path:
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                # Collect data for failed test cases
                if date['status'] == 'failed' or date['status'] == 'broken':
                    files.append(date)
        print(files)
        return files

    @classmethod
    def get_case_name(cls, test_case):
        """
        Collect test case names
        @return:
        """
        name = test_case['name'].split('[')
        case_name = name[1][:-1]
        return case_name

    @classmethod
    def get_parameters(cls, test_case):
        """
        Get the parameters content from the allure report, data before the request
        Used to handle cases where test case execution fails before a request is sent
        @return:
        """
        parameters = test_case['parameters'][0]['value']
        return ast.literal_eval(parameters)

    @classmethod
    def get_test_stage(cls, test_case):
        """
        Get the data after the request from the allure report
        @return:
        """
        test_stage = test_case['testStage']['steps']
        return test_stage

    def get_case_url(self, test_case):
        """
        Get the url of the test case
        @param test_case:
        @return:
        """
        # Check whether the data in the test case steps is abnormal
        if test_case['testStage']['status'] == 'broken':
            # If in an abnormal state, get the pre-request data
            _url = self.get_parameters(test_case)['url']
        else:
            # Otherwise get the data from the request step; since dependencies may result in multiple sets, only take the last set
            _url = self.get_test_stage(test_case)[-7]['name'][7:]
        return _url

    def get_method(self, test_case):
        """
        Get the request method used in the test case
        @param test_case:
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _method = self.get_parameters(test_case)['method']
        else:
            _method = self.get_test_stage(test_case)[-6]['name'][6:]
        return _method

    def get_headers(self, test_case):
        """
        Get the request headers from the test case
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _headers = self.get_parameters(test_case)['headers']
        else:
            # If the test case request succeeded, get the request header info from the allure attachment
            _headers_attachment = self.get_test_stage(test_case)[-5]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _headers_attachment)
            with open(path, 'r', encoding='utf-8') as file:
                _headers = json.load(file)
        return _headers

    def get_request_type(self, test_case):
        """
        Get the request type of the test case
        @param test_case:
        @return:
        """
        request_type = self.get_parameters(test_case)['requestType']
        return request_type

    def get_case_data(self, test_case):
        """
        Get the test case content
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _case_data = self.get_parameters(test_case)['data']
        else:
            _case_data_attachments = self.get_test_stage(test_case)[-4]['attachments'][0]['source']
            path = ensure_path_sep("\\report\\html\\data\\attachments\\" + _case_data_attachments)
            with open(path, 'r', encoding='utf-8') as file:
                _case_data = json.load(file)
        return _case_data

    def get_dependence_case(self, test_case):
        """
        Get dependent test cases
        @param test_case:
        @return:
        """
        _dependence_case_data = self.get_parameters(test_case)['dependence_case_data']
        return _dependence_case_data

    def get_sql(self, test_case):
        """
        Get sql data
        @param test_case:
        @return:
        """
        sql = self.get_parameters(test_case)['sql']
        return sql

    def get_assert(self, test_case):
        """
        Get assertion data
        @param test_case:
        @return:
        """
        assert_data = self.get_parameters(test_case)['assert_data']
        return assert_data

    @classmethod
    def get_response(cls, test_case):
        """
        Get the response content data
        @param test_case:
        @return:
        """
        if test_case['testStage']['status'] == 'broken':
            _res_date = test_case['testStage']['statusMessage']
        else:
            try:
                res_data_attachments = \
                    test_case['testStage']['steps'][-1]['attachments'][0]['source']
                path = ensure_path_sep("\\report\\html\\data\\attachments\\" + res_data_attachments)
                with open(path, 'r', encoding='utf-8') as file:
                    _res_date = json.load(file)
            except FileNotFoundError:
                # No response data was extracted from the program, return None
                _res_date = None
        return _res_date

    @classmethod
    def get_case_time(cls, test_case):
        """
        Get the test case run duration
        @param test_case:
        @return:
        """

        case_time = str(test_case['time']['duration']) + "ms"
        return case_time

    @classmethod
    def get_uid(cls, test_case):
        """
        Get the uid from the allure report
        @param test_case:
        @return:
        """
        uid = test_case['uid']
        return uid


class ErrorCaseExcel:
    """ Collect failed test cases and organize them into an excel report """
    def __init__(self):
        _excel_template = ensure_path_sep("\\utils\\other_tools\\allure_data\\Automation Exception Test Cases.xlsx")
        self._file_path = ensure_path_sep("\\Files\\" + "Automation Exception Test Cases.xlsx")
        # if os.path.exists(self._file_path):
        #     os.remove(self._file_path)

        shutil.copyfile(src=_excel_template, dst=self._file_path)
        # Open the program (open only, do not create new)
        self.app = xlwings.App(visible=False, add_book=False)
        self.w_book = self.app.books.open(self._file_path, read_only=False)

        # Select worksheet:
        self.sheet = self.w_book.sheets['Exception Cases']  # or select by index
        self.case_data = ErrorTestCase()

    def background_color(self, position: str, rgb: tuple):
        """
        Set background color for excel cell
        @param rgb: rgb color rgb=(0, 255, 0)
        @param position: position, e.g. A1, B1...
        @return:
        """
        # Locate the cell position
        rng = self.sheet.range(position)
        excel_rgb = rng.color = rgb
        return excel_rgb

    def column_width(self, position: str, width: int):
        """
        Set column width
        @return:
        """
        rng = self.sheet.range(position)
        # Column width
        excel_column_width = rng.column_width = width
        return excel_column_width

    def row_height(self, position, height):
        """
        Set row height
        @param position:
        @param height:
        @return:
        """
        rng = self.sheet.range(position)
        excel_row_height = rng.row_height = height
        return excel_row_height

    def column_width_adaptation(self, position):
        """
        Auto-fit all column widths in excel
        @return:
        """
        rng = self.sheet.range(position)
        auto_fit = rng.columns.autofit()
        return auto_fit

    def row_width_adaptation(self, position):
        """
        Set all row widths to auto-fit in excel
        @return:
        """
        rng = self.sheet.range(position)
        row_adaptation = rng.rows.autofit()
        return row_adaptation

    def write_excel_content(self, position: str, value: str):
        """
        Write content to excel
        @param value:
        @param position:
        @return:
        """
        self.sheet.range(position).value = value

    def write_case(self):
        """
        Write failed test case data into the case
        @return:
        """

        _data = self.case_data.get_error_case_data()
        # Only write if there is data
        if len(_data) > 0:
            num = 2
            for data in _data:
                self.write_excel_content(position="A" + str(num), value=str(self.case_data.get_uid(data)))
                self.write_excel_content(position='B' + str(num), value=str(self.case_data.get_case_name(data)))
                self.write_excel_content(position="C" + str(num), value=str(self.case_data.get_case_url(data)))
                self.write_excel_content(position="D" + str(num), value=str(self.case_data.get_method(data)))
                self.write_excel_content(position="E" + str(num), value=str(self.case_data.get_request_type(data)))
                self.write_excel_content(position="F" + str(num), value=str(self.case_data.get_headers(data)))
                self.write_excel_content(position="G" + str(num), value=str(self.case_data.get_case_data(data)))
                self.write_excel_content(position="H" + str(num), value=str(self.case_data.get_dependence_case(data)))
                self.write_excel_content(position="I" + str(num), value=str(self.case_data.get_assert(data)))
                self.write_excel_content(position="J" + str(num), value=str(self.case_data.get_sql(data)))
                self.write_excel_content(position="K" + str(num), value=str(self.case_data.get_case_time(data)))
                self.write_excel_content(position="L" + str(num), value=str(self.case_data.get_response(data)))
                num += 1
            self.w_book.save()
            self.w_book.close()
            self.app.quit()
            # Only send WeCom notification if there is data
            WeChatSend(AllureFileClean().get_case_count()).send_file_msg(self._file_path)


if __name__ == '__main__':
    ErrorCaseExcel().write_case()
