#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 15:28

"""
redis cache operation encapsulation
"""
from typing import Text, Any
import redis


class RedisHandler:
    """ redis cache read/write encapsulation """

    def __init__(self):
        self.host = '127.0.0.0'
        self.port = 6379
        self.database = 0
        self.password = 123456
        self.charset = 'UTF-8'
        self.redis = redis.Redis(
            self.host,
            port=self.port,
            password=self.password,
            decode_responses=True,
            db=self.database
        )

    def set_string(
            self, name: Text,
            value, exp_time=None,
            exp_milliseconds=None,
            name_not_exist=False,
            name_exit=False) -> None:
        """
        Write str to cache (single)
        :param name: cache name
        :param value: cache value
        :param exp_time: expiration time (seconds)
        :param exp_milliseconds: expiration time (milliseconds)
        :param name_not_exist: if set to True, the current set operation is only executed when name does not exist (add)
        :param name_exit: if set to True, the current set operation is only executed when name exists (modify)
        :return:
        """
        self.redis.set(
            name,
            value,
            ex=exp_time,
            px=exp_milliseconds,
            nx=name_not_exist,
            xx=name_exit
        )

    def key_exit(self, key: Text):
        """
        Check whether a key exists in redis
        :param key:
        :return:
        """

        return self.redis.exists(key)

    def incr(self, key: Text):
        """
        Use the incr method to handle concurrency issues
        When the key does not exist, it is first initialized to 0, and each call increments it by 1
        :return:
        """
        self.redis.incr(key)

    def get_key(self, name: Any) -> Text:
        """
        Read cache
        :param name:
        :return:
        """
        return self.redis.get(name)

    def set_many(self, *args, **kwargs):
        """
        Batch set
        Supports the following ways to batch set cache
        eg: set_many({'k1': 'v1', 'k2': 'v2'})
            set_many(k1="v1", k2="v2")
        :return:
        """
        self.redis.mset(*args, **kwargs)

    def get_many(self, *args):
        """Get multiple values"""
        results = self.redis.mget(*args)
        return results

    def del_all_cache(self):
        """Clear all current data"""
        for key in self.redis.keys():
            self.del_cache(key)

    def del_cache(self, name):
        """
        Delete cache
        :param name:
        :return:
        """
        self.redis.delete(name)
