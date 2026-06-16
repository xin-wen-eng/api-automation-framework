#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/29 14:43
"""
Decorator for tracking request execution duration. If the request response time exceeds the threshold,
the program will output a red log message indicating that the http request has timed out. The default duration is 3000ms.
"""
from utils.logging_tool.log_control import ERROR


def execution_duration(number: int):
    """
    Decorator for measuring function execution time
    :param number: expected function run duration
    :return:
    """

    def decorator(func):
        def swapper(*args, **kwargs):
            res = func(*args, **kwargs)
            run_time = res.res_time
            # Calculate timestamp at millisecond level; if time exceeds number, print function name and run time
            if run_time > number:
                ERROR.logger.error(
                    "\n==============================================\n"
                    "Test case execution time is too long, please pay attention.\n"
                    "Function run time: %s ms\n"
                    "Test case related data: %s\n"
                    "================================================="
                    , run_time, res)
            return res
        return swapper
    return decorator
