#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/22 13:45
"""

from typing import Union, Text, Dict, List
from utils.read_files_tools.yaml_control import GetYamlData
from utils.other_tools.models import TestCase
from utils.other_tools.exceptions import ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler
from utils import config
import os


class CaseData:
    """
    yaml data parsing, validates whether the data is filled in correctly
    """

    def __init__(self, file_path):
        self.file_path = file_path

    def __new__(cls, file_path):
        if os.path.exists(file_path) is True:
            return object.__new__(cls)
        else:
            raise FileNotFoundError("Test case path not found")

    def case_process(
            self,
            case_id_switch: Union[None, bool] = None):
        """
        After data cleansing, returns all test cases in the yaml file
        @param case_id_switch: determines whether data cleansing needs to extract case_id, mainly used for compatibility with the test case pool data
        :return:
        """
        dates = GetYamlData(self.file_path).get_yaml_data()
        case_lists = []
        for key, values in dates.items():
            # Data in the common config differs from test case data and needs to be handled separately
            if key != 'case_common':
                case_date = {
                    'method': self.get_case_method(case_id=key, case_data=values),
                    'is_run': self.get_is_run(key, values),
                    'url': self.get_case_host(case_id=key, case_data=values),
                    'detail': self.get_case_detail(case_id=key, case_data=values),
                    'headers': self.get_headers(case_id=key, case_data=values),
                    'requestType': self.get_request_type(key, values),
                    'data': self.get_case_dates(key, values),
                    'dependence_case': self.get_dependence_case(key, values),
                    'dependence_case_data': self.get_dependence_case_data(key, values),
                    "current_request_set_cache": self.get_current_request_set_cache(values),
                    "sql": self.get_sql(key, values),
                    "assert_data": self.get_assert(key, values),
                    "setup_sql": self.setup_sql(values),
                    "teardown": self.tear_down(values),
                    "teardown_sql": self.teardown_sql(values),
                    "sleep": self.time_sleep(values),
                }
                if case_id_switch is True:
                    case_lists.append({key: TestCase(**case_date).dict()})
                else:
                    # Regex processing: if the test case needs to read data from cache, read cache first
                    case_lists.append(TestCase(**case_date).dict())
        return case_lists

    def get_case_host(
            self, case_id: Text,
            case_data: Dict) -> Text:
        """
        Get the host for the test case
        :return:
        """
        try:
            _url = case_data['url']
            _host = case_data['host']
            if _url is None or _host is None:
                raise ValueNotFoundError(
                    f"The url or host in the test case cannot be empty!\n "
                    f"Case ID: {case_id} \n "
                    f"Case path: {self.file_path}"
                )
            return _host + _url
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(data_name="url or host", case_id=case_id)
            ) from exc

    def get_case_method(
            self, case_id: Text,
            case_data: Dict) -> Text:
        """
        Get the request method for the test case: GET/POST/PUT/DELETE
        :return:
        """
        try:
            _case_method = case_data['method']
            _request_method = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']
            if _case_method.upper() not in _request_method:
                raise ValueNotFoundError(
                    f"method currently only supports {_request_method} request methods, please contact the administrator to add new ones. "
                    f"{self.raise_value_error(data_name='request method', case_id=case_id, detail=_case_method)}"
                )
            return _case_method.upper()

        except AttributeError as exc:
            raise ValueNotFoundError(
                f"method currently only supports {['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTION']} request methods, "
                f"please contact the administrator to add new ones! "
                f"{self.raise_value_error(data_name='request method', case_id=case_id, detail=case_data['method'])}"
            ) from exc
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(data_name="method", case_id=case_id)
            ) from exc

    @classmethod
    def get_current_request_set_cache(cls, case_data: Dict) -> Dict:
        """Store the current request's test case data into cache"""
        try:
            return case_data['current_request_set_cache']
        except KeyError:
            ...

    def get_case_detail(
            self,
            case_id: Text,
            case_data: Dict) -> Text:
        """
        Get the test case description
        :return:
        """
        try:
            return case_data['detail']
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="detail")
            ) from exc

    def get_headers(
            self,
            case_id: Text,
            case_data: Dict) -> Dict:
        """
        Get the information from the test case request headers
        :return:
        """
        try:
            _header = case_data['headers']
            return _header
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="headers")
            ) from exc

    def raise_value_error(
            self, data_name: Text,
            case_id: Text,
            detail: [Text, list, Dict]) -> Text:
        """
        Exception message for all incorrectly filled test case fields
        :param data_name: parameter name
        :param case_id: test case ID
        :param detail: parameter content
        :return:
        """
        detail = f"The {data_name} in the test case is filled in incorrectly!\n " \
                 f"Case ID: {case_id} \n" \
                 f" Case path: {self.file_path}\n" \
                 f"Current value: {detail}"

        return detail

    def raise_value_null_error(
            self, data_name: Text,
            case_id: Text) -> Text:
        """
        Exception message for empty parameter names in test cases
        :param data_name: parameter name
        :param case_id: test case ID
        :return:
        """
        detail = f"Parameter {data_name} not found in the test case. If already filled, please check for indentation issues." \
                 f"Case ID: {case_id} " \
                 f"Case path: {self.file_path}"
        return detail

    def get_request_type(self, case_id: Text, case_data: Dict) -> Text:
        """
        Get the request type: params, data, json
        :return:
        """

        _types = ['JSON', 'PARAMS', 'FILE', 'DATA', "EXPORT", "NONE"]

        try:
            _request_type = str(case_data['requestType'])
            # Validate whether the user-filled requestType conforms to the specification
            if _request_type.upper() not in _types:
                raise ValueNotFoundError(
                    self.raise_value_error(
                        data_name='requestType',
                        case_id=case_id,
                        detail=_request_type
                    )
                )
            return _request_type.upper()
        # Exception handling
        except AttributeError as exc:
            raise ValueNotFoundError(
                self.raise_value_error(
                    data_name='requestType',
                    case_id=case_id,
                    detail=case_data['requestType'])
            ) from exc
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="requestType")
            ) from exc

    def get_is_run(
            self,
            case_id: Text,
            case_data: Dict) -> Text:
        """
        Get the execution status; both true and None will execute
        :return:
        """
        try:
            return case_data['is_run']
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="is_run")
            ) from exc

    def get_dependence_case(
            self,
            case_id: Text,
            case_data: Dict) -> Dict:
        """
        Get whether there are dependent test cases
        :return:
        """
        try:
            _dependence_case = case_data['dependence_case']
            return _dependence_case
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="dependence_case")
            ) from exc

    # TODO validate the values in dependence_case_data
    def get_dependence_case_data(
            self,
            case_id: Text,
            case_data: Dict) -> Union[Dict, None]:
        """
        Get the dependent test case data
        :return:
        """
        # If the test case has dependencies, return the dependency data; otherwise return None
        if self.get_dependence_case(case_id=case_id, case_data=case_data):
            try:
                _dependence_case_data = case_data['dependence_case_data']
                # If the test case is set to require a dependent case but dependence_case_data has no data filled in, raise an exception
                if _dependence_case_data is None:
                    raise ValueNotFoundError(f"dependence_case_data is missing the required dependency data! "
                                             f"If already filled, please check for indentation issues."
                                             f"Case ID: {case_id}"
                                             f"Case path: {self.file_path}")

                return _dependence_case_data
            except KeyError as exc:
                raise ValueNotFoundError(
                    self.raise_value_null_error(case_id=case_id, data_name="dependence_case_data")
                ) from exc
        else:
            return None

    def get_case_dates(
            self,
            case_id: Text,
            case_data: Dict) -> Dict:
        """
        Get the request data
        :param case_id:
        :param case_data:
        :return:
        """
        try:
            _dates = case_data['data']
            # # Handle date values in request parameters that lack quotes, causing incorrect data
            # if _dates is not None:
            #     def data_type(value):
            #         if isinstance(value, dict):
            #             for k, v in value.items():
            #                 if isinstance(v, dict):
            #                     data_type(v)
            #                 else:
            #                     if isinstance(v, datetime.date):
            #                         value[k] = str(v)
            #     data_type(_dates)
            return _dates

        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="data")
            ) from exc

    # TODO validate the values in assert
    def get_assert(
            self,
            case_id: Text,
            case_data: Dict):
        """
        Get the data that needs to be asserted
        :return:
        """
        try:
            _assert = case_data['assert']
            if _assert is None:
                raise self.raise_value_error(data_name="assert", case_id=case_id, detail=_assert)
            return case_data['assert']
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="assert")
            ) from exc

    def get_sql(
            self,
            case_id: Text,
            case_data: Dict) -> Union[list, None]:
        """
        Get the assertion SQL in the test case
        :return:
        """
        try:
            _sql = case_data['sql']
            # Check if the database switch is enabled and sql is not empty
            if config.mysql_db.switch and _sql is None:
                return None
            return case_data['sql']
        except KeyError as exc:
            raise ValueNotFoundError(
                self.raise_value_null_error(case_id=case_id, data_name="sql")
            ) from exc

    @classmethod
    def setup_sql(cls, case_data: Dict) -> Union[list, None]:
        """
        Get the setup SQL; if the test case needs to read SQL from the database as parameters, fill in setup_sql
        :return:
        """
        try:
            _setup_sql = case_data['setup_sql']
            return _setup_sql
        except KeyError:
            return None

    @classmethod
    def tear_down(cls, case_data: Dict) -> Union[Dict, None]:
        """
        Get the teardown request data
        """
        try:
            _teardown = case_data['teardown']
            return _teardown
        except KeyError:
            return None

    @classmethod
    def teardown_sql(cls, case_data: Dict) -> Union[list, None]:
        """
        Get the setup SQL; if the test case needs to read SQL from the database as parameters, fill in setup_sql
        :return:
        """
        try:
            _teardown_sql = case_data['teardown_sql']
            return _teardown_sql
        except KeyError:
            return None

    @classmethod
    def time_sleep(cls, case_data: Dict) -> Union[int, float, None]:
        """ Set the sleep duration """
        try:
            _sleep_time = case_data['sleep']
            return _sleep_time
        except KeyError:
            return None


class GetTestCase:

    @staticmethod
    def case_data(case_id_lists: List):
        case_lists = []
        for i in case_id_lists:
            _data = CacheHandler.get_cache(i)
            case_lists.append(_data)

        return case_lists


if __name__ == '__main__':
    a = CaseData(r'D:\work_code\pytest-auto-api2\data\Collect\collect_addtool.yaml').case_process()
    print(a)
