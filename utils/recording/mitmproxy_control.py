#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/3/28 15:46
"""
from urllib.parse import parse_qs, urlparse
from typing import Any, Union, Text, List, Dict, Tuple
import ast
import os
import mitmproxy.http
from mitmproxy import ctx
from ruamel import yaml


class Counter:
    """
    Proxy recording, intercepts and captures network requests based on the mitmproxy library.
    Converts API request data into yaml test cases.
    Reference: https://blog.wolfogre.com/posts/usage-of-mitmproxy/
    """

    def __init__(self, filter_url: List, filename: Text = './data/proxy_data.yaml'):
        self.num = 0
        self.file = filename
        self.counter = 1
        # URLs to be filtered
        self.url = filter_url

    def response(self, flow: mitmproxy.http.HTTPFlow) -> None:
        """
        mitmproxy packet capture processes responses, aggregates required data here,
        filters URLs containing the specified url and whose response format is json.
        :param flow:
        :return:
        """
        # Store the interface types to be filtered out
        filter_url_type = ['.css', '.js', '.map', '.ico', '.png', '.woff', '.map3', '.jpeg', '.jpg']
        url = flow.request.url
        ctx.log.info("=" * 100)
        # Filter out URLs with suffixes in filter_url_type
        if any(i in url for i in filter_url_type) is False:
            # Store test cases
            if self.filter_url(url):

                data = self.data_handle(flow.request.text)
                method = flow.request.method
                header = self.token_handle(flow.request.headers)
                response = flow.response.text
                case_id = self.get_case_id(url) + str(self.counter)
                cases = {
                    case_id: {
                        "host": self.host_handle(url),
                        "url": self.url_path_handle(url),
                        "method": method,
                        "detail": None,
                        "headers": header,
                        'requestType': self.request_type_handler(method),
                        "is_run": True,
                        "data": data,
                        "dependence_case": None,
                        "dependence_case_data": None,
                        "assert": self.response_code_handler(response),
                        "sql": None
                    }
                }
                # If request parameters are appended to the URL, extract URL parameters and convert to dict
                if "?" in url:
                    cases[case_id]['url'] = self.get_url_handler(url)[1]
                    cases[case_id]['data'] = self.get_url_handler(url)[0]

                ctx.log.info("=" * 100)
                ctx.log.info(cases)

                # If the file does not exist, create it
                try:
                    self.yaml_cases(cases)
                except FileNotFoundError:
                    os.makedirs(self.file)
                self.counter += 1

    @classmethod
    def get_case_id(cls, url: Text) -> Text:
        """
        Extract the corresponding user_id via url.
        :param url:
        :return:
        """
        _url_path = str(url).split('?')[0]
        # Use the last segment of the interface path in the URL as the case_id name
        _url = _url_path.split('/')
        return _url[-1]

    def filter_url(self, url: Text) -> bool:
        """Filter URL"""
        for i in self.url:
            # Check whether the currently intercepted URL is a host configured in addons
            if i in url:
                # If yes, return True
                return True
        # Otherwise return False
        return False

    @classmethod
    def response_code_handler(cls, response) -> Union[Dict, None]:
        """
        Process the API response; the default assertion data is the code field.
        If the API has no code field, return None.
        @param response:
        @return:
        """
        try:
            data = cls.data_handle(response)
            return {"code": {"jsonpath": "$.code", "type": "==",
                             "value": data['code'], "AssertType": None}}
        except KeyError:
            return None
        except NameError:
            return None

    @classmethod
    def request_type_handler(cls, method: Text) -> Text:
        """ Handle request type: params, json, file - adjust according to your company's business logic """
        if method == 'GET':
            # For example, in our company only GET requests use params; all others use json
            return 'params'
        return 'json'

    @classmethod
    def data_handle(cls, dict_str) -> Any:
        """Handle API request/response data, fixing issues with null, true format"""
        try:
            if dict_str != "":
                if 'null' in dict_str:
                    dict_str = dict_str.replace('null', 'None')
                if 'true' in dict_str:
                    dict_str = dict_str.replace('true', 'True')
                if 'false' in dict_str:
                    dict_str = dict_str.replace('false', 'False')
                dict_str = ast.literal_eval(dict_str)
            if dict_str == "":
                dict_str = None
            return dict_str
        except Exception as exc:
            raise exc

    @classmethod
    def token_handle(cls, header) -> Dict:
        """
        Extract request header parameters.
        :param header:
        :return:
        """
        # Here all request header data is intercepted in full.
        # If only certain parameters are needed, add filtering logic here.
        headers = {}
        for key, value in header.items():
            headers[key] = value
        return headers

    def host_handle(self, url: Text) -> Tuple:
        """
        Parse the URL.
        :param url: https://xxxx.test.xxxx.com/#/goods/listShop
        :return: https://xxxx.test.xxxx.com/
        """
        host = None
        # Iterate over the hosts that need to be filtered
        for i in self.url:
            # This checks whether the domain configured in conf.py matches;
            # if so, the test case displays "${{host}}" to dynamically obtain the host.
            # Replace with your own company's host address here.
            if 'https://www.wanandroid.com' in url:
                host = '${{host}}'
            elif i in url:
                host = i
        return host

    def url_path_handle(self, url: Text):
        """
        Parse the url_path.
        :param url: https://xxxx.test.xxxx.com/shopList/json
        :return: /shopList/json
        """
        url_path = None
        # Iterate over the domains to be intercepted
        for path in self.url:
            if path in url:
                url_path = url.split(path)[-1]
        return url_path

    def yaml_cases(self, data: Dict) -> None:
        """
        Write yaml data.
        :param data: test case data
        :return:
        """
        with open(self.file, "a", encoding="utf-8") as file:
            yaml.dump(data, file, Dumper=yaml.RoundTripDumper, allow_unicode=True)
            file.write('\n')

    def get_url_handler(self, url: Text) -> Tuple:
        """
        Convert URL parameters into a dictionary.
        :param url: /trade?tradeNo=&outTradeId=11
        :return: {"outTradeId": 11}
        """
        result = None
        url_path = None
        for i in self.url:
            if i in url:
                query = urlparse(url).query
                # Convert the string to a dictionary
                params = parse_qs(query)
                # The values in the resulting dict are all lists; if a parameter value in the URL is empty, it will not appear in the dict
                result = {key: params[key][0] for key in params}
                url = url[0:url.rfind('?')]
                url_path = url.split(i)[-1]
        return result, url_path


# 1. The local machine must have a proxy configured; the default port is: 8080
# 2. In the console, enter: mitmweb -s .\utils\recording\mitmproxy_control.py -p 8888 to start proxy recording mode


addons = [
    Counter(["https://www.wanandroid.com"])
    ]
