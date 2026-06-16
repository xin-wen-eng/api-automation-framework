#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:28

"""
Cache file processing
"""

import os
from typing import Any, Text, Union
from common.setting import ensure_path_sep
from utils.other_tools.exceptions import ValueNotFoundError


class Cache:
    """ Set and read cache """
    def __init__(self, filename: Union[Text, None]) -> None:
        # If filename is not empty, operate on the specified file content
        if filename:
            self.path = ensure_path_sep("\\cache" + filename)
        # If filename is None, operate on all file content
        else:
            self.path = ensure_path_sep("\\cache")

    def set_cache(self, key: Text, value: Any) -> None:
        """
        Set cache, only supports setting single dictionary type cache data. If the cache file already exists, replace the previous cache content.
        :return:
        """
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str({key: value}))

    def set_caches(self, value: Any) -> None:
        """
        Set multiple groups of cache data
        :param value: cache content
        :return:
        """
        with open(self.path, 'w', encoding='utf-8') as file:
            file.write(str(value))

    def get_cache(self) -> Any:
        """
        Get cache data
        :return:
        """
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            pass

    def clean_cache(self) -> None:
        """Delete all cache files"""

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"The cache file you want to delete does not exist {self.path}")
        os.remove(self.path)

    @classmethod
    def clean_all_cache(cls) -> None:
        """
        Clear all cache files
        :return:
        """
        cache_path = ensure_path_sep("\\cache")

        # List all files in the directory, generate a list
        list_dir = os.listdir(cache_path)
        for i in list_dir:
            # Loop to delete all contents under the folder
            os.remove(cache_path + i)


_cache_config = {}


class CacheHandler:
    @staticmethod
    def get_cache(cache_data):
        try:
            return _cache_config[cache_data]
        except KeyError:
            raise ValueNotFoundError(f"Cache data for {cache_data} was not found, please check whether the data has been stored in the cache")

    @staticmethod
    def update_cache(*, cache_name, value):
        _cache_config[cache_name] = value
