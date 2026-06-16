#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:21
"""
Log decorator, controls program log output, defaults to True
If set to False, the program will not print logs
"""
import ast
from functools import wraps
from utils.read_files_tools.regular_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR


def log_decorator(switch: bool):
    """
    Encapsulates the log decorator, prints request information
    :param switch: defines the log switch
    :return:
    """
    def decorator(func):
        @wraps(func)
        def swapper(*args, **kwargs):

            # Only print logs when the log switch is enabled
            res = func(*args, **kwargs)
            # Check if the log switch is enabled
            if switch:
                _log_msg = f"\n======================================================\n" \
                               f"Case Title: {res.detail}\n" \
                               f"Request Path: {res.url}\n" \
                               f"Request Method: {res.method}\n" \
                               f"Request Headers:   {res.headers}\n" \
                               f"Request Body: {res.request_body}\n" \
                               f"Response Content: {res.response_data}\n" \
                               f"Response Time: {res.res_time} ms\n" \
                               f"Http Status Code: {res.status_code}\n" \
                               "====================================================="
                _is_run = ast.literal_eval(cache_regular(str(res.is_run)))
                # For normal log output, console prints in green
                if _is_run in (True, None) and res.status_code == 200:
                    INFO.logger.info(_log_msg)
                else:
                    # For failed cases, console prints in red
                    ERROR.logger.error(_log_msg)
            return res
        return swapper
    return decorator
