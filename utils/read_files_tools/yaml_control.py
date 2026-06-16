#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 10:51
"""

import os
import ast
import yaml.scanner
from utils.read_files_tools.regular_control import regular


class GetYamlData:
    """ Get data from yaml files """

    def __init__(self, file_dir):
        self.file_dir = str(file_dir)

    def get_yaml_data(self) -> dict:
        """
        Get data from yaml
        :param: fileDir:
        :return:
        """
        # Check if the file exists
        if os.path.exists(self.file_dir):
            data = open(self.file_dir, 'r', encoding='utf-8')
            res = yaml.load(data, Loader=yaml.FullLoader)
        else:
            raise FileNotFoundError("File path does not exist")
        return res

    def write_yaml_data(self, key: str, value) -> int:
        """
        Modify the value in a yaml file while preserving comments
        :param key: dictionary key
        :param value: value to write
        :return:
        """
        with open(self.file_dir, 'r', encoding='utf-8') as file:
            # Create an empty list with no elements
            lines = []
            for line in file.readlines():
                if line != '\n':
                    lines.append(line)
            file.close()

        with open(self.file_dir, 'w', encoding='utf-8') as file:
            flag = 0
            for line in lines:
                left_str = line.split(":")[0]
                if key == left_str and '#' not in line:
                    newline = f"{left_str}: {value}"
                    line = newline
                    file.write(f'{line}\n')
                    flag = 1
                else:
                    file.write(f'{line}')
            file.close()
            return flag


class GetCaseData(GetYamlData):
    """ Get data from test cases """

    def get_different_formats_yaml_data(self) -> list:
        """
        Get yaml data compatible with different formats
        :return:
        """
        res_list = []
        for i in self.get_yaml_data():
            res_list.append(i)
        return res_list

    def get_yaml_case_data(self):
        """
        Get test case data and convert to the specified data format
        :return:
        """

        _yaml_data = self.get_yaml_data()
        # Process data in yaml file with regex
        re_data = regular(str(_yaml_data))
        return ast.literal_eval(re_data)
