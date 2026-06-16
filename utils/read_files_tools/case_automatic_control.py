#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 13:22
"""
import os
from typing import Text, Dict
from common.setting import ensure_path_sep
from utils.read_files_tools.testcase_template import write_testcase_file
from utils.read_files_tools.yaml_control import GetYamlData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.other_tools.exceptions import ValueNotFoundError


class TestCaseAutomaticGeneration:
    """Automatically generate test_case code for automated testing"""

    @staticmethod
    def case_date_path() -> Text:
        """Return the yaml test case file path"""
        return ensure_path_sep("\\data")

    @staticmethod
    def case_path() -> Text:
        """ Path for storing test case code"""
        return ensure_path_sep("\\test_case")

    def file_name(self, file: Text) -> Text:
        """
        Convert the yaml file name to a py file name
        :param file: yaml file path
        :return:  Example: DateDemo.py
        """
        i = len(self.case_date_path())
        yaml_path = file[i:]
        file_name = None
        # Path conversion
        if '.yaml' in yaml_path:
            file_name = yaml_path.replace('.yaml', '.py')
        elif '.yml' in yaml_path:
            file_name = yaml_path.replace('.yml', '.py')
        return file_name

    def get_case_path(self, file_path: Text) -> tuple:
        """
        Generate the corresponding testCase layer code path based on yaml test cases
        :param file_path: yaml test case path
        :return: D:\\Project\\test_case\\test_case_demo.py, test_case_demo.py
        """

        # Split by "\\" to extract the file name
        path = self.file_name(file_path).split(os.sep)
        # Ensure the generated testcase file name starts with test_
        case_name = path[-1] = path[-1].replace(path[-1], "test_" + path[-1])
        new_name = os.sep.join(path)
        return ensure_path_sep("\\test_case" + new_name), case_name

    def get_test_class_title(self, file_path: Text) -> Text:
        """
        Automatically generate class name
        :param file_path:
        :return: sup_apply_list --> SupApplyList
        """
        # Extract file name
        _file_name = os.path.split(self.file_name(file_path))[1][:-3]
        _name = _file_name.split("_")
        _name_len = len(_name)
        # Convert file name format to class name: sup_apply_list --> SupApplyList
        for i in range(_name_len):
            _name[i] = _name[i].capitalize()
        _class_name = "".join(_name)

        return _class_name

    @staticmethod
    def error_message(param_name, file_path):
        """
        Hint message for incorrectly filled test case fields
        :return:
        """
        msg = f"Parameter '{param_name}' not found in test case. Please check whether the corresponding parameter is filled in the newly added test case." \
              "If already filled, the yaml parameter indentation may be incorrect.\n" \
              f"Test case path: {file_path}"
        return msg

    def func_title(self, file_path: Text) -> Text:
        """
        Function name
        :param file_path: yaml test case path
        :return:
        """

        _file_name = os.path.split(self.file_name(file_path))[1][:-3]
        return _file_name

    @staticmethod
    def allure_epic(case_data: Dict, file_path) -> Text:
        """
        Content for allure report decorator @allure.epic("project name")
        :param file_path: test case path
        :param case_data: test case data
        :return:
        """
        try:
            return case_data['case_common']['allureEpic']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureEpic",
                file_path=file_path
            )) from exc

    @staticmethod
    def allure_feature(case_data: Dict, file_path) -> Text:
        """
        Content for allure report decorator @allure.feature("module name")
        :param file_path:
        :param case_data:
        :return:
        """
        try:
            return case_data['case_common']['allureFeature']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureFeature",
                file_path=file_path
            )) from exc

    @staticmethod
    def allure_story(case_data: Dict, file_path) -> Text:
        """
        Content for allure report decorator @allure.story("test feature")
        :param file_path:
        :param case_data:
        :return:
        """
        try:
            return case_data['case_common']['allureStory']
        except KeyError as exc:
            raise ValueNotFoundError(TestCaseAutomaticGeneration.error_message(
                param_name="allureStory",
                file_path=file_path
            )) from exc

    def mk_dir(self, file_path: Text) -> None:
        """ Check if the folder path for generated automation code exists; create it if not """
        # _LibDirPath = os.path.split(self.libPagePath(filePath))[0]

        _case_dir_path = os.path.split(self.get_case_path(file_path)[0])[0]
        if not os.path.exists(_case_dir_path):
            os.makedirs(_case_dir_path)

    @staticmethod
    def case_ids(test_case):
        """
        Get test case IDs
        :param test_case: test case content
        :return:
        """
        ids = []
        for k, v in test_case.items():
            if k != "case_common":
                ids.append(k)
        return ids

    def yaml_path(self, file_path: Text) -> Text:
        """
        Generate dynamic yaml path, mainly for handling multi-level business scenarios
        :param file_path: if business has multiple levels, get each level /test_demo/DateDemo.py
        :return: Login/common.yaml
        """
        i = len(self.case_date_path())
        # Compatible with linux and windows path handling
        yaml_path = file_path[i:].replace("\\", "/")
        return yaml_path

    def get_case_automatic(self) -> None:
        """ Automatically generate test code"""
        file_path = get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True)

        for file in file_path:
            # Skip proxy intercepted yaml files, do not generate test_case code
            if 'proxy_data.yaml' not in file:
                # Check if the required folder path exists; create it if not
                self.mk_dir(file)
                yaml_case_process = GetYamlData(file).get_yaml_data()
                self.case_ids(yaml_case_process)
                write_testcase_file(
                    allure_epic=self.allure_epic(case_data=yaml_case_process, file_path=file),
                    allure_feature=self.allure_feature(yaml_case_process, file_path=file),
                    class_title=self.get_test_class_title(file),
                    func_title=self.func_title(file),
                    case_path=self.get_case_path(file)[0],
                    case_ids=self.case_ids(yaml_case_process),
                    file_name=self.get_case_path(file)[1],
                    allure_story=self.allure_story(case_data=yaml_case_process, file_path=file)
                    )


if __name__ == '__main__':
    TestCaseAutomaticGeneration().get_case_automatic()
