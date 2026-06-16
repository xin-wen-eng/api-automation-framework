#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 13:22
"""
import os


def get_all_files(file_path, yaml_data_switch=False) -> list:
    """
    Get file paths
    :param file_path: directory path
    :param yaml_data_switch: whether to filter files to yaml format, True means filter
    :return:
    """
    filename = []
    # Get all sub-file names under all files
    for root, dirs, files in os.walk(file_path):
        for _file_path in files:
            path = os.path.join(root, _file_path)
            if yaml_data_switch:
                if 'yaml' in path or '.yml' in path:
                    filename.append(path)
            else:
                filename.append(path)
    return filename
