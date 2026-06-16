#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:44
Description: Collect allure reports
"""

import json
from typing import List, Text
from common.setting import ensure_path_sep
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.other_tools.models import TestMetrics


class AllureFileClean:
    """allure report data cleaning, extracting data required by the business"""

    @classmethod
    def get_testcases(cls) -> List:
        """ Get the execution status of all test cases in allure reports"""
        # Collect all data into files
        files = []
        for i in get_all_files(ensure_path_sep("\\report\\html\\data\\test-cases")):
            with open(i, 'r', encoding='utf-8') as file:
                date = json.load(file)
                files.append(date)
        return files

    def get_failed_case(self) -> List:
        """ Get the titles and code paths of all failed test cases"""
        error_case = []
        for i in self.get_testcases():
            if i['status'] == 'failed' or i['status'] == 'broken':
                error_case.append((i['name'], i['fullName']))
        return error_case

    def get_failed_cases_detail(self) -> Text:
        """ Return all relevant content for failed test cases """
        date = self.get_failed_case()
        values = ""
        # If there are failed test cases, return the content
        if len(date) >= 1:
            values = "Failed cases:\n"
            values += "        **********************************\n"
            for i in date:
                values += "        " + i[0] + ":" + i[1] + "\n"
        return values

    @classmethod
    def get_case_count(cls) -> "TestMetrics":
        """ Count the number of test cases """
        try:
            file_name = ensure_path_sep("\\report\\html\\widgets\\summary.json")
            with open(file_name, 'r', encoding='utf-8') as file:
                data = json.load(file)
            _case_count = data['statistic']
            _time = data['time']
            keep_keys = {"passed", "failed", "broken", "skipped", "total"}
            run_case_data = {k: v for k, v in data['statistic'].items() if k in keep_keys}
            # Check if total number of test cases run is greater than 0
            if _case_count["total"] > 0:
                # Calculate the test case pass rate
                run_case_data["pass_rate"] = round(
                    (_case_count["passed"] + _case_count["skipped"]) / _case_count["total"] * 100, 2
                )
            else:
                # If no test cases were run, the pass rate is 0.0
                run_case_data["pass_rate"] = 0.0
            # Collect the test case run duration
            run_case_data['time'] = _time if run_case_data['total'] == 0 else round(_time['duration'] / 1000, 2)
            return TestMetrics(**run_case_data)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "The program detected that you have not generated an allure report. "
                "This is usually caused by an incorrect allure environment configuration. "
                "For details, please refer to the following blog post: "
                "https://blog.csdn.net/weixin_43865008/article/details/124332793"
            ) from exc


if __name__ == '__main__':
    AllureFileClean().get_case_count()
