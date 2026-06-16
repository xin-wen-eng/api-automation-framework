#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:47
"""

import time
from typing import Text
from datetime import datetime


def count_milliseconds():
    """
    Calculate time
    :return:
    """
    access_start = datetime.now()
    access_end = datetime.now()
    access_delta = (access_end - access_start).seconds * 1000
    return access_delta


def timestamp_conversion(time_str: Text) -> int:
    """
    Timestamp conversion, convert date format to timestamp
    :param time_str: time
    :return:
    """

    try:
        datetime_format = datetime.strptime(str(time_str), "%Y-%m-%d %H:%M:%S")
        timestamp = int(
            time.mktime(datetime_format.timetuple()) * 1000.0
            + datetime_format.microsecond / 1000.0
        )
        return timestamp
    except ValueError as exc:
        raise ValueError('Date format error, the required format is "%Y-%m-%d %H:%M:%S" ') from exc


def time_conversion(time_num: int):
    """
    Convert timestamp to date
    :param time_num:
    :return:
    """
    if isinstance(time_num, int):
        time_stamp = float(time_num / 1000)
        time_array = time.localtime(time_stamp)
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time


def now_time():
    """
    Get current time, date format: 2021-12-11 12:39:25
    :return:
    """
    localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    return localtime


def now_time_day():
    """
    Get current time, date format: 2021-12-11
    :return:
    """
    localtime = time.strftime("%Y-%m-%d", time.localtime())
    return localtime


def get_time_for_min(minute: int) -> int:
    """
    Get the timestamp N minutes from now
    @param minute: minutes
    @return: timestamp N minutes from now
    """
    return int(time.time() + 60 * minute) * 1000


def get_now_time() -> int:
    """
    Get current timestamp, integer
    @return: current timestamp
    """
    return int(time.time()) * 1000
