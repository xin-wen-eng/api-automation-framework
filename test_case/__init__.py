#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:28
from common.setting import ensure_path_sep
from utils.read_files_tools.get_yaml_data_analysis import CaseData
from utils.read_files_tools.get_all_files_path import get_all_files
from utils.cache_process.cache_control import CacheHandler, _cache_config


def write_case_process():
    """
    Get all test cases and write them into the case pool
    :return:
    """

    # Loop to get the file paths of all stored test cases
    for i in get_all_files(file_path=ensure_path_sep("\\data"), yaml_data_switch=True):
        # Loop to read data from the file
        case_process = CaseData(i).case_process(case_id_switch=True)
        if case_process is not None:
            # Convert data types
            for case in case_process:
                for k, v in case.items():
                    # Check if case_id already exists
                    case_id_exit = k in _cache_config.keys()
                    # If case_id does not exist, write the test case into the cache pool
                    if case_id_exit is False:
                        CacheHandler.update_cache(cache_name=k, value=v)
                        # case_data[k] = v
                    # When case_id is True (exists), raise an exception
                    elif case_id_exit is True:
                        raise ValueError(f"case_id: {k} has duplicate entries, please modify the case_id\n"
                                         f"File path: {i}")


write_case_process()
