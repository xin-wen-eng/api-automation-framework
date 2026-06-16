#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/30 14:12
import pytest
import time
import allure
import requests
import ast
from common.setting import ensure_path_sep
from utils.requests_tool.request_control import cache_regular
from utils.logging_tool.log_control import INFO, ERROR, WARNING
from utils.other_tools.models import TestCase
from utils.read_files_tools.clean_files import del_file
from utils.other_tools.allure_data.allure_tools import allure_step, allure_step_no
from utils.cache_process.cache_control import CacheHandler


@pytest.fixture(scope="session", autouse=False)
def clear_report():
    """If the clean command cannot delete the report, manually delete it here"""
    del_file(ensure_path_sep("\\report"))


@pytest.fixture(scope="session", autouse=True)
def work_login_init():
    """
    Get the login cookie
    :return:
    """

    url = "https://www.wanandroid.com/user/login"
    data = {
        "username": 18800000001,
        "password": 123456
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # Request the login interface

    res = requests.post(url=url, data=data, verify=True, headers=headers)
    response_cookie = res.cookies

    cookies = ''
    for k, v in response_cookie.items():
        _cookie = k + "=" + v + ";"
        # Get the cookie content from the login response; the cookie is a dict type, convert it to the corresponding format
        cookies += _cookie
        # Write the cookie from the login interface into the cache, where login_cookie is the cache name
    CacheHandler.update_cache(cache_name='login_cookie', value=cookies)


def pytest_collection_modifyitems(items):
    """
    When test case collection is complete, display the collected item name and node_id Chinese characters in the console
    :return:
    """
    for item in items:
        item.name = item.name.encode("utf-8").decode("unicode_escape")
        item._nodeid = item.nodeid.encode("utf-8").decode("unicode_escape")

    # Expected test case order
    # print("Collected test cases: %s" % items)
    appoint_items = ["test_get_user_info", "test_collect_addtool", "test_Cart_List", "test_ADD", "test_Guest_ADD",
                     "test_Clear_Cart_Item"]

    # Specify execution order
    run_items = []
    for i in appoint_items:
        for item in items:
            module_item = item.name.split("[")[0]
            if i == module_item:
                run_items.append(item)

    for i in run_items:
        run_index = run_items.index(i)
        items_index = items.index(i)

        if run_index != items_index:
            n_data = items[run_index]
            run_index = items.index(n_data)
            items[items_index], items[run_index] = items[run_index], items[items_index]


def pytest_configure(config):
    config.addinivalue_line("markers", 'smoke')
    config.addinivalue_line("markers", 'regression test')


@pytest.fixture(scope="function", autouse=True)
def case_skip(in_data):
    """Handle skipped test cases"""
    in_data = TestCase(**in_data)
    if ast.literal_eval(cache_regular(str(in_data.is_run))) is False:
        allure.dynamic.title(in_data.detail)
        allure_step_no(f"Request URL: {in_data.is_run}")
        allure_step_no(f"Request method: {in_data.method}")
        allure_step("Request headers: ", in_data.headers)
        allure_step("Request data: ", in_data.data)
        allure_step("Dependency data: ", in_data.dependence_case_data)
        allure_step("Expected data: ", in_data.assert_data)
        pytest.skip()


def pytest_terminal_summary(terminalreporter):
    """
    Collect test results
    """

    _PASSED = len([i for i in terminalreporter.stats.get('passed', []) if i.when != 'teardown'])
    _ERROR = len([i for i in terminalreporter.stats.get('error', []) if i.when != 'teardown'])
    _FAILED = len([i for i in terminalreporter.stats.get('failed', []) if i.when != 'teardown'])
    _SKIPPED = len([i for i in terminalreporter.stats.get('skipped', []) if i.when != 'teardown'])
    _TOTAL = terminalreporter._numcollected
    _TIMES = time.time() - terminalreporter._sessionstarttime
    INFO.logger.error(f"Total test cases: {_TOTAL}")
    INFO.logger.error(f"Error test cases: {_ERROR}")
    ERROR.logger.error(f"Failed test cases: {_FAILED}")
    WARNING.logger.warning(f"Skipped test cases: {_SKIPPED}")
    INFO.logger.info("Test execution duration: %.2f" % _TIMES + " s")

    try:
        _RATE = _PASSED / _TOTAL * 100
        INFO.logger.info("Test pass rate: %.2f" % _RATE + " %")
    except ZeroDivisionError:
        INFO.logger.info("Test pass rate: 0.00 %")
