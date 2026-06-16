#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:26
"""

import json

import xlrd
from xlutils.copy import copy
from common.setting import ensure_path_sep


def get_excel_data(sheet_name: str, case_name: any) -> list:
    """
    Read data from Excel
    :param sheet_name: the name of the sheet in excel
    :param case_name: test case name
    :return:
    """
    res_list = []

    excel_dire = ensure_path_sep("\\data\\TestLogin.xls")
    work_book = xlrd.open_workbook(excel_dire, formatting_info=True)

    # Open the corresponding sub-sheet
    work_sheet = work_book.sheet_by_name(sheet_name)
    # Read one row
    idx = 0
    for one in work_sheet.col_values(0):
        # Run the test cases that need to be run
        if case_name in one:
            req_body_data = work_sheet.cell(idx, 9).value
            resp_data = work_sheet.cell(idx, 11).value
            res_list.append((req_body_data, json.loads(resp_data)))
        idx += 1
    return res_list


def set_excel_data(sheet_index: int) -> tuple:
    """
    Excel write
    :return:
    """
    excel_dire = '../data/TestLogin.xls'
    work_book = xlrd.open_workbook(excel_dire, formatting_info=True)
    work_book_new = copy(work_book)

    work_sheet_new = work_book_new.get_sheet(sheet_index)
    return work_book_new, work_sheet_new


if __name__ == '__main__':
    get_excel_data("Exception Cases", '111')
