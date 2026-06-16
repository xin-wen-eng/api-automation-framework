#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 14:18
"""
Assertion type encapsulation, supports JSON response assertion and database assertion
"""
import ast
import json
from typing import Text, Dict, Any, Union
from jsonpath import jsonpath
from utils.other_tools.models import AssertMethod
from utils.logging_tool.log_control import ERROR, WARNING
from utils.read_files_tools.regular_control import cache_regular
from utils.other_tools.models import load_module_functions
from utils.assertion import assert_type
from utils.other_tools.exceptions import JsonpathExtractionFailed, SqlNotFound, AssertTypeError
from utils import config


class Assert:
    """ assert module encapsulation """

    def __init__(self, assert_data: Dict):
        self.assert_data = ast.literal_eval(cache_regular(str(assert_data)))
        self.functions_mapping = load_module_functions(assert_type)

    @staticmethod
    def _check_params(
            response_data: Text,
            sql_data: Union[Dict, None]) -> bool:
        """

        :param response_data: response data
        :param sql_data: database data
        :return:
        """
        if (response_data and sql_data) is not False:
            if not isinstance(sql_data, dict):
                raise ValueError(
                    "Assertion failed, response_data and sql_data must be of dict type, "
                    "please check whether the data corresponding to the interface is correct\n"
                    f"sql_data: {sql_data}, data type: {type(sql_data)}\n"
                )
        return True

    @staticmethod
    def res_sql_data_bytes(res_sql_data: Any) -> Text:
        """ Handle the case where the data type queried from mysql is bytes, convert to str type """
        if isinstance(res_sql_data, bytes):
            res_sql_data = res_sql_data.decode('utf=8')
        return res_sql_data

    def sql_switch_handle(
            self,
            sql_data: Dict,
            assert_value: Any,
            key: Text,
            values: Any,
            resp_data: Dict,
            message: Text) -> None:
        """

        :param sql_data: sql in the test case
        :param assert_value: assertion content
        :param key:
        :param values:
        :param resp_data: expected result
        :param message: expected result
        :return:
        """
        # Check if database switch is off
        if config.mysql_db.switch is False:
            WARNING.logger.warning(
                "Database status detected as off, the program has skipped this assertion for you, assertion value: %s", values
            )
        # Database switch is on
        if config.mysql_db.switch:
            # Follow normal SQL assertion logic
            if sql_data != {'sql': None}:
                res_sql_data = jsonpath(sql_data, assert_value)
                if res_sql_data is False:
                    raise JsonpathExtractionFailed(
                        f"Database assertion jsonpath extraction failed, current jsonpath content: {assert_value}\n"
                        f"Database return content: {sql_data}"
                    )

                # Handle the case where the data type queried from mysql is bytes, convert to str type
                res_sql_data = self.res_sql_data_bytes(res_sql_data[0])
                name = AssertMethod(self.assert_data[key]['type']).name
                self.functions_mapping[name](resp_data[0], res_sql_data, str(message))

            # Handle the case where the test case uses database assertion but no SQL is provided in the case
            else:
                raise SqlNotFound("Please add the SQL statement you want to query in the test case.")

    def assert_type_handle(
            self,
            assert_types: Union[Text, None],
            sql_data: Union[Dict, None],
            assert_value: Any,
            key: Text,
            values: Dict,
            resp_data: Any,
            message: Text
    ) -> None:
        """Handle assertion types"""
        # Determine assertion type
        if assert_types == 'SQL':
            self.sql_switch_handle(
                sql_data=sql_data,
                assert_value=assert_value,
                key=key,
                values=values,
                resp_data=resp_data,
                message=message
            )

        # If assertType is None, use response assertion
        elif assert_types is None:
            name = AssertMethod(self.assert_data[key]['type']).name
            self.functions_mapping[name](resp_data[0], assert_value, message)
        else:
            raise AssertTypeError("Assertion failed, currently only database assertion and response assertion are supported")

    @classmethod
    def _message(cls, value):
        _message = ""
        if jsonpath(obj=value, expr="$.message") is not False:
            _message = value['message']
        return _message

    def assert_equality(
            self,
            response_data: Text,
            sql_data: Dict,
            status_code: int) -> None:
        """  assert assertion handling """
        # Check data type
        if self._check_params(response_data, sql_data) is not False:
            for key, values in self.assert_data.items():
                if key == "status_code":
                    assert status_code == values
                else:
                    assert_value = self.assert_data[key]['value']  # Get the expected value from the yaml file
                    assert_jsonpath = self.assert_data[key]['jsonpath']  # Get the jsonpath data from the yaml assertion
                    assert_types = self.assert_data[key]['AssertType']
                    # Use jsonpath from yaml to get the interface response data for the object
                    resp_data = jsonpath(json.loads(response_data), assert_jsonpath)
                    message = self._message(value=values)
                    # If jsonpath data retrieval fails, it returns False; only execute the following code if retrieval succeeds
                    if resp_data is not False:
                        # Determine assertion type
                        self.assert_type_handle(
                            assert_types=assert_types,
                            sql_data=sql_data,
                            assert_value=assert_value,
                            key=key,
                            values=values,
                            resp_data=resp_data,
                            message=message
                        )
                    else:
                        ERROR.logger.error("JsonPath value retrieval failed %s ", assert_jsonpath)
                        raise JsonpathExtractionFailed(f"JsonPath value retrieval failed {assert_jsonpath}")


if __name__ == '__main__':
    pass
