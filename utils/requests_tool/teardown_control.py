#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/23 14:22
# @Email   : 1603453211@qq.com
# @File    : teardownControl
# @describe: Post-request processing
"""
import ast
import json
from typing import Dict, Text
from jsonpath import jsonpath
from utils.requests_tool.request_control import RequestControl
from utils.read_files_tools.regular_control import cache_regular, sql_regular, regular
from utils.other_tools.jsonpath_date_replace import jsonpath_replace
from utils.mysql_tool.mysql_control import MysqlDB
from utils.logging_tool.log_control import WARNING
from utils.other_tools.models import ResponseData, TearDown, SendRequest, ParamPrepare
from utils.other_tools.exceptions import JsonpathExtractionFailed, ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler
from utils import config


class TearDownHandler:
    """ Handle yaml-format post-requests """
    def __init__(self, res: "ResponseData"):
        self._res = res

    @classmethod
    def jsonpath_replace_data(
            cls,
            replace_key: Text,
            replace_value: Dict) -> Text:

        """ Use jsonpath to determine the location of data that needs to be replaced """
        _change_data = replace_key.split(".")
        # jsonpath data parsing
        _new_data = jsonpath_replace(
            change_data=_change_data,
            key_name='_teardown_case',
            data_switch=False
        )

        if not isinstance(replace_value, str):
            _new_data += f" = {replace_value}"
        # Final extracted data, converted to _teardown_case[xxx][xxx]
        else:
            _new_data += f" = '{replace_value}'"
        return _new_data

    @classmethod
    def get_cache_name(
            cls,
            replace_key: Text,
            resp_case_data: Dict) -> None:
        """
        Get the cache name and write the extracted data into the cache
        """
        if "$set_cache{" in replace_key and "}" in replace_key:
            start_index = replace_key.index("$set_cache{")
            end_index = replace_key.index("}", start_index)
            old_value = replace_key[start_index:end_index + 2]
            cache_name = old_value[11:old_value.index("}")]
            CacheHandler.update_cache(cache_name=cache_name, value=resp_case_data)
            # Cache(cache_name).set_caches(resp_case_data)

    @classmethod
    def regular_testcase(cls, teardown_case: Dict) -> Dict:
        """Handle dynamic data in test cases"""
        test_case = regular(str(teardown_case))
        test_case = ast.literal_eval(cache_regular(str(test_case)))
        return test_case

    @classmethod
    def teardown_http_requests(cls, teardown_case: Dict) -> "ResponseData":
        """
        Send post-requests
        @param teardown_case: post-request test case
        @return:
        """

        test_case = cls.regular_testcase(teardown_case)
        res = RequestControl(test_case).http_request(
            dependent_switch=False
        )
        return res

    def dependent_type_response(
            self,
            teardown_case_data: "SendRequest",
            resp_data: Dict) -> Text:
        """
        Determine that the dependency type is the response content of the currently executing test case
        :param : teardown_case_data: test case content in teardown
        :param : resp_data: content to be replaced
        :return:
        """
        _replace_key = teardown_case_data.replace_key
        _response_dependent = jsonpath(
            obj=resp_data,
            expr=teardown_case_data.jsonpath
        )
        # If data is extracted, proceed to the next step
        if _response_dependent is not False:
            _resp_case_data = _response_dependent[0]
            data = self.jsonpath_replace_data(
                replace_key=_replace_key,
                replace_value=_resp_case_data
            )
        else:
            raise JsonpathExtractionFailed(
                f"jsonpath extraction failed, replacement content: {resp_data} \n"
                f"jsonpath: {teardown_case_data.jsonpath}"
            )
        return data

    def dependent_type_request(
            self,
            teardown_case_data: Dict,
            request_data: Dict) -> None:
        """
        Determine that the dependency type is request content
        :param : teardown_case_data: test case content in teardown
        :param : request_data: content to be replaced
        :return:
        """
        try:
            _request_set_value = teardown_case_data['set_value']
            _request_dependent = jsonpath(
                obj=request_data,
                expr=teardown_case_data['jsonpath']
            )
            if _request_dependent is not False:
                _request_case_data = _request_dependent[0]
                self.get_cache_name(
                    replace_key=_request_set_value,
                    resp_case_data=_request_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath extraction failed, replacement content: {request_data} \n"
                    f"jsonpath: {teardown_case_data['jsonpath']}"
                )
        except KeyError as exc:
            raise ValueNotFoundError("Missing set_value parameter in teardown, please check if the test case is correct") from exc

    def dependent_self_response(
            self,
            teardown_case_data: "ParamPrepare",
            res: Dict,
            resp_data: Dict) -> None:
        """
        Determine that the dependency type is the response content from the dependent test case ID itself
        :param : teardown_case_data: test case content in teardown
        :param : resp_data: content to be replaced
        :param : res: interface response content
        :return:
        """
        try:
            _set_value = teardown_case_data.set_cache
            _response_dependent = jsonpath(
                obj=res,
                expr=teardown_case_data.jsonpath
            )
            # If data is extracted, proceed to the next step
            if _response_dependent is not False:
                _resp_case_data = _response_dependent[0]
                # Get set_cache and then write the data into the cache
                # Cache(_set_value).set_caches(_resp_case_data)
                CacheHandler.update_cache(cache_name=_set_value, value=_resp_case_data)
                self.get_cache_name(
                    replace_key=_set_value,
                    resp_case_data=_resp_case_data
                )
            else:
                raise JsonpathExtractionFailed(
                    f"jsonpath extraction failed, replacement content: {resp_data} \n"
                    f"jsonpath: {teardown_case_data.jsonpath}")
        except KeyError as exc:
            raise ValueNotFoundError("Missing set_cache parameter in teardown, please check if the test case is correct") from exc

    @classmethod
    def dependent_type_cache(cls, teardown_case: "SendRequest") -> Text:
        """
        Determine that the dependency type is handled from cache
        :param : teardown_case_data: test case content in teardown
        :return:
        """
        if teardown_case.dependent_type == 'cache':
            _cache_name = teardown_case.cache_data
            _replace_key = teardown_case.replace_key
            # Use jsonpath to determine the location of data that needs to be replaced
            _change_data = _replace_key.split(".")
            _new_data = jsonpath_replace(
                change_data=_change_data,
                key_name='_teardown_case',
                data_switch=False
            )
            # jsonpath data parsing
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in _cache_name for i in value_types) is True:
                # _cache_data = Cache(_cache_name.split(':')[1]).get_cache()
                _cache_data = CacheHandler.get_cache(_cache_name.split(':')[1])
                _new_data += f" = {_cache_data}"

            # Final extracted data, converted to _teardown_case[xxx][xxx]
            else:
                # _cache_data = Cache(_cache_name).get_cache()
                _cache_data = CacheHandler.get_cache(_cache_name)
                _new_data += f" = '{_cache_data}'"

            return _new_data

    def send_request_handler(
            self, data: "TearDown",
            resp_data: Dict,
            request_data: Dict
    ) -> None:
        """
        Post-request handler
        @return:
        """
        _send_request = data.send_request
        _case_id = data.case_id
        # _teardown_case = ast.literal_eval(Cache('case_process').get_cache())[_case_id]
        _teardown_case = CacheHandler.get_cache(_case_id)
        for i in _send_request:
            if i.dependent_type == 'cache':
                exec(self.dependent_type_cache(teardown_case=i))
            # Determine data extraction from response content
            if i.dependent_type == 'response':
                exec(
                    self.dependent_type_response(
                        teardown_case_data=i,
                        resp_data=resp_data)
                )
            # Determine data from request
            elif i.dependent_type == 'request':
                self.dependent_type_request(
                    teardown_case_data=i,
                    request_data=request_data
                )

        test_case = self.regular_testcase(_teardown_case)
        self.teardown_http_requests(test_case)

    def param_prepare_request_handler(
            self,
            data: "TearDown",
            resp_data: Dict) -> None:
        """
        Pre-request handler
        @param data:
        @param resp_data:
        @return:
        """
        _case_id = data.case_id
        # _teardown_case = ast.literal_eval(Cache('case_process').get_cache())[_case_id]
        _teardown_case = CacheHandler.get_cache(_case_id)
        _param_prepare = data.param_prepare
        res = self.teardown_http_requests(_teardown_case)
        for i in _param_prepare:
            # Determine the request type is self, get the response of the current case_id itself
            if i.dependent_type == 'self_response':
                self.dependent_self_response(
                    teardown_case_data=i,
                    resp_data=resp_data,
                    res=json.loads(res.response_data)
                )

    def teardown_handle(self) -> None:
        """
        Why do we need to separately distinguish between param_prepare and send_request here?
        Assume we have test case A, and in teardown we need to execute test case B.

        Consider that the user may need to get the response content of teardown test case B, or may need to get the response content of test case A.
        Therefore, we need to distinguish them using keywords here. We need to consider that if we need to get the response of case B, we must first send the request and then get the response data.

        If we need to get the response of interface A, we don't need to send an additional request, so we need to distinguish between param_prepare (pre-request preparation)
        and send_request (send request).
        @return:
        """
        # Get the test case information
        _teardown_data = self._res.teardown
        # Get the interface response content
        _resp_data = self._res.response_data
        # Get the interface request parameters
        _request_data = self._res.yaml_data.data
        # Check if there is no teardown
        if _teardown_data is not None:
            # Iterate through the interfaces in teardown
            for _data in _teardown_data:
                if _data.param_prepare is not None:
                    self.param_prepare_request_handler(
                        data=_data,
                        resp_data=json.loads(_resp_data)
                    )
                elif _data.send_request is not None:
                    self.send_request_handler(
                        data=_data,
                        request_data=_request_data,
                        resp_data=json.loads(_resp_data)
                    )
        self.teardown_sql()

    def teardown_sql(self) -> None:
        """Handle post-teardown SQL"""

        sql_data = self._res.teardown_sql
        _response_data = self._res.response_data
        if sql_data is not None:
            for i in sql_data:
                if config.mysql_db.switch:
                    _sql_data = sql_regular(value=i, res=json.loads(_response_data))
                    MysqlDB().execute(cache_regular(_sql_data))
                else:
                    WARNING.logger.warning("The program detected that your database switch is off, skipping delete SQL: %s", i)
