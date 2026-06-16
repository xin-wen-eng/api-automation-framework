#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/4/22 14:49

"""
Assert assertion types
"""

from typing import Any,  Union, Text


def equals(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """Check whether two values are equal"""

    assert check_value == expect_value, message


def less_than(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """Check whether the actual result is less than the expected result"""
    assert check_value < expect_value, message


def less_than_or_equals(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""):

    """Check whether the actual result is less than or equal to the expected result"""
    assert check_value <= expect_value, message


def greater_than(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """Check whether the actual result is greater than the expected result"""
    assert check_value > expect_value, message


def greater_than_or_equals(
        check_value: Union[int, float], expect_value: Union[int, float], message: Text = ""
):
    """Check whether the actual result is greater than or equal to the expected result"""
    assert check_value >= expect_value, message


def not_equals(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """Check whether the actual result is not equal to the expected result"""
    assert check_value != expect_value, message


def string_equals(
        check_value: Text, expect_value: Any, message: Text = ""
):
    """Check whether two strings are equal"""
    assert check_value == expect_value, message


def length_equals(
        check_value: Text, expect_value: int, message: Text = ""
):
    """Check whether the length is equal"""
    assert isinstance(
        expect_value, int
    ), "expect_value must be of type int"
    assert len(check_value) == expect_value, message


def length_greater_than(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """Check whether the length is greater than"""
    assert isinstance(
        expect_value, (float, int)
    ), "expect_value must be of type float/int"
    assert len(str(check_value)) > expect_value, message


def length_greater_than_or_equals(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """Check whether the length is greater than or equal to"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value must be of type float/int"
    assert len(check_value) >= expect_value, message


def length_less_than(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """Check whether the length is less than"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value must be of type float/int"
    assert len(check_value) < expect_value, message


def length_less_than_or_equals(
        check_value: Text, expect_value: Union[int, float], message: Text = ""
):
    """Check whether the length is less than or equal to"""
    assert isinstance(
        expect_value, (int, float)
    ), "expect_value must be of type float/int"
    assert len(check_value) <= expect_value, message


def contains(check_value: Any, expect_value: Any, message: Text = ""):
    """Check whether the expected result content is contained within the actual result"""
    assert isinstance(
        check_value, (list, tuple, dict, str, bytes)
    ), "expect_value must be of type list/tuple/dict/str/bytes"
    assert expect_value in check_value, message


def contained_by(check_value: Any, expect_value: Any, message: Text = ""):
    """Check whether the actual result is contained within the expected result"""
    assert isinstance(
        expect_value, (list, tuple, dict, str, bytes)
    ), "expect_value must be of type list/tuple/dict/str/bytes"

    assert check_value in expect_value, message


def startswith(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """Check whether the beginning of the response content matches the beginning of the expected result content"""
    assert str(check_value).startswith(str(expect_value)), message


def endswith(
        check_value: Any, expect_value: Any, message: Text = ""
):
    """Check whether the end of the response content matches the expected result content"""
    assert str(check_value).endswith(str(expect_value)), message
