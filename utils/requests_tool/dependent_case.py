"""
# @Time   : 2022/3/28 16:08
"""
import ast
import json
from typing import Text, Dict, Union, List
from jsonpath import jsonpath
from utils.requests_tool.request_control import RequestControl
from utils.mysql_tool.mysql_control import SetUpMySQL
from utils.read_files_tools.regular_control import regular, cache_regular
from utils.other_tools.jsonpath_date_replace import jsonpath_replace
from utils.logging_tool.log_control import WARNING
from utils.other_tools.models import DependentType
from utils.other_tools.models import TestCase, DependentCaseData, DependentData
from utils.other_tools.exceptions import ValueNotFoundError
from utils.cache_process.cache_control import CacheHandler
from utils import config


class DependentCase:
    """ Handle dependency-related business logic """

    def __init__(self, dependent_yaml_case: TestCase):
        self.__yaml_case = dependent_yaml_case

    @classmethod
    def get_cache(cls, case_id: Text) -> Dict:
        """
        Retrieve data from the cache case pool by case_id
        :param case_id:
        :return: case_id_01
        """
        _case_data = CacheHandler.get_cache(case_id)
        return _case_data

    @classmethod
    def jsonpath_data(
            cls,
            obj: Dict,
            expr: Text) -> list:
        """
        Extract dependent data via jsonpath
        :param obj: object information
        :param expr: jsonpath expression
        :return: extracted content value, returned as an array

        Object: {"data": applyID} --> jsonpath extraction method: $.data.data.[0].applyId
        """

        _jsonpath_data = jsonpath(obj, expr)
        # Check if data was extracted successfully; raise exception if not
        if _jsonpath_data is False:
            raise ValueNotFoundError(
                f"jsonpath extraction failed!\n Extracted data: {obj} \n jsonpath rule: {expr}"
            )
        return _jsonpath_data

    @classmethod
    def set_cache_value(cls, dependent_data: "DependentData") -> Union[Text, None]:
        """
        Check whether the dependency data needs to be stored in cache
        """
        try:
            return dependent_data.set_cache
        except KeyError:
            return None

    @classmethod
    def replace_key(cls, dependent_data: "DependentData"):
        """ Get the content that needs to be replaced """
        try:
            _replace_key = dependent_data.replace_key
            return _replace_key
        except KeyError:
            return None

    def url_replace(
            self,
            replace_key: Text,
            jsonpath_dates: Dict,
            jsonpath_data: list) -> None:
        """
        Replace dynamic parameters in the URL
        # For example: some interface parameters are in the URL without parameter names, /api/v1/work/spu/approval/spuApplyDetails/{id}
        # In that case, write the test case as follows, using $url_params{} for replacement,
        # e.g. /api/v1/work/spu/approval/spuApplyDetails/$url_params{id}
        :param jsonpath_data: data values parsed by jsonpath
        :param replace_key: the replace_key in the test case for data replacement
        :param jsonpath_dates: data values stored by jsonpath
        :return:
        """

        if "$url_param" in replace_key:
            _url = self.__yaml_case.url.replace(replace_key, str(jsonpath_data[0]))
            jsonpath_dates['$.url'] = _url
        else:
            jsonpath_dates[replace_key] = jsonpath_data[0]

    def _dependent_type_for_sql(
            self,
            setup_sql: List,
            dependence_case_data: "DependentCaseData",
            jsonpath_dates: Dict) -> None:
        """
        Handle dependency type as sql - extract dependent parameters from the database
        @param setup_sql: pre-condition SQL statements
        @param dependence_case_data: dependent case data
        @param jsonpath_dates: dependent related test case data
        @return:
        """
        # Check dependency data type - depends on data from sql
        if setup_sql is not None:
            if config.mysql_db.switch:
                setup_sql = ast.literal_eval(cache_regular(str(setup_sql)))
                sql_data = SetUpMySQL().setup_sql_data(sql=setup_sql)
                dependent_data = dependence_case_data.dependent_data
                for i in dependent_data:
                    _jsonpath = i.jsonpath
                    jsonpath_data = self.jsonpath_data(obj=sql_data, expr=_jsonpath)
                    _set_value = self.set_cache_value(i)
                    _replace_key = self.replace_key(i)
                    if _set_value is not None:
                        CacheHandler.update_cache(cache_name=_set_value, value=jsonpath_data[0])
                        # Cache(_set_value).set_caches(jsonpath_data[0])
                    if _replace_key is not None:
                        jsonpath_dates[_replace_key] = jsonpath_data[0]
                        self.url_replace(
                            replace_key=_replace_key,
                            jsonpath_dates=jsonpath_dates,
                            jsonpath_data=jsonpath_data,
                        )
            else:
                WARNING.logger.warning("Database switch detected as off, please verify the configuration")

    def dependent_handler(
            self,
            _jsonpath: Text,
            set_value: Text,
            replace_key: Text,
            jsonpath_dates: Dict,
            data: Dict,
            dependent_type: int
    ) -> None:
        """ Handle data replacement """
        jsonpath_data = self.jsonpath_data(
            data,
            _jsonpath
        )
        if set_value is not None:
            if len(jsonpath_data) > 1:
                CacheHandler.update_cache(cache_name=set_value, value=jsonpath_data)
            else:
                CacheHandler.update_cache(cache_name=set_value, value=jsonpath_data[0])
        if replace_key is not None:
            if dependent_type == 0:
                jsonpath_dates[replace_key] = jsonpath_data[0]
            self.url_replace(replace_key=replace_key, jsonpath_dates=jsonpath_dates,
                             jsonpath_data=jsonpath_data)

    def is_dependent(self) -> Union[Dict, bool]:
        """
        Check whether there is data dependency
        :return:
        """

        # Get the dependent_type value from the test case to determine if dependency execution is needed
        _dependent_type = self.__yaml_case.dependence_case
        # Get dependent case data
        _dependence_case_dates = self.__yaml_case.dependence_case_data
        _setup_sql = self.__yaml_case.setup_sql
        # Check if there is a dependency
        if _dependent_type is True:
            # Read dependency-related test case data
            jsonpath_dates = {}
            # Iterate over all data that needs to be depended on
            try:
                for dependence_case_data in _dependence_case_dates:
                    _case_id = dependence_case_data.case_id
                    # If dependency data is sql, case_id must be written as self; otherwise the program cannot get the case_id
                    if _case_id == 'self':
                        self._dependent_type_for_sql(
                            setup_sql=_setup_sql,
                            dependence_case_data=dependence_case_data,
                            jsonpath_dates=jsonpath_dates)
                    else:
                        re_data = regular(str(self.get_cache(_case_id)))
                        re_data = ast.literal_eval(cache_regular(str(re_data)))
                        res = RequestControl(re_data).http_request()
                        if dependence_case_data.dependent_data is not None:
                            dependent_data = dependence_case_data.dependent_data
                            for i in dependent_data:

                                _case_id = dependence_case_data.case_id
                                _jsonpath = i.jsonpath
                                _request_data = self.__yaml_case.data
                                _replace_key = self.replace_key(i)
                                _set_value = self.set_cache_value(i)
                                # Check dependency data type - depends on data from response
                                if i.dependent_type == DependentType.RESPONSE.value:
                                    self.dependent_handler(
                                        data=json.loads(res.response_data),
                                        _jsonpath=_jsonpath,
                                        set_value=_set_value,
                                        replace_key=_replace_key,
                                        jsonpath_dates=jsonpath_dates,
                                        dependent_type=0
                                    )

                                # Check dependency data type - depends on data from request
                                elif i.dependent_type == DependentType.REQUEST.value:
                                    self.dependent_handler(
                                        data=res.body,
                                        _jsonpath=_jsonpath,
                                        set_value=_set_value,
                                        replace_key=_replace_key,
                                        jsonpath_dates=jsonpath_dates,
                                        dependent_type=1
                                    )

                                else:
                                    raise ValueError(
                                        "The dependent_type is incorrect; only request, response, and sql dependencies are supported\n"
                                        f"Current value: {i.dependent_type}"
                                    )
                return jsonpath_dates
            except KeyError as exc:
                # pass
                raise ValueNotFoundError(
                    f"In dependence_case_data, the parameter {exc} was not found. Please check if it has been filled in. "
                    f"If already filled in, please check for yaml indentation issues"
                ) from exc
            except TypeError as exc:
                raise ValueNotFoundError(
                    "All content under dependence_case_data cannot be empty! "
                    "Please check whether the relevant data has been filled in. If already filled in, please check for indentation issues"
                ) from exc
        else:
            return False

    def get_dependent_data(self) -> None:
        """
        Replace data using jsonpath and dependent data
        :return:
        """
        _dependent_data = DependentCase(self.__yaml_case).is_dependent()
        _new_data = None
        # Check if there is a dependency
        if _dependent_data is not None and _dependent_data is not False:
            # if _dependent_data is not False:
            for key, value in _dependent_data.items():
                # Use jsonpath to determine the location of the data to be replaced
                _change_data = key.split(".")
                # jsonpath data parsing
                # Do not delete this yaml_case
                yaml_case = self.__yaml_case
                _new_data = jsonpath_replace(change_data=_change_data, key_name='yaml_case')
                # Final extracted data, converted to __yaml_case.data
                _new_data += ' = ' + str(value)
                exec(_new_data)
