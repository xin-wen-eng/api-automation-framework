#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/26 18:27
"""
mysql encapsulation, supports insert, delete, update, and query
"""
import ast
import datetime
import decimal
from warnings import filterwarnings
import pymysql
from typing import List, Union, Text, Dict
from utils import config
from utils.logging_tool.log_control import ERROR
from utils.read_files_tools.regular_control import sql_regular
from utils.read_files_tools.regular_control import cache_regular
from utils.other_tools.exceptions import DataAcquisitionFailed, ValueTypeError

# Ignore MySQL warning messages
filterwarnings("ignore", category=pymysql.Warning)


class MysqlDB:
    """ mysql encapsulation """
    if config.mysql_db.switch:

        def __init__(self):

            try:
                # Establish database connection
                self.conn = pymysql.connect(
                    host=config.mysql_db.host,
                    user=config.mysql_db.user,
                    password=config.mysql_db.password,
                    port=config.mysql_db.port
                )

                # Use the cursor method to get an operation cursor that can execute sql statements and return results as a dictionary
                self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            except AttributeError as error:
                ERROR.logger.error("Database connection failed, reason: %s", error)

        def __del__(self):
            try:
                # Close cursor
                self.cur.close()
                # Close connection
                self.conn.close()
            except AttributeError as error:
                ERROR.logger.error("Database connection failed, reason: %s", error)

        def query(self, sql, state="all"):
            """
                Query
                :param sql:
                :param state:  all is the default to query all
                :return:
                """
            try:
                self.cur.execute(sql)

                if state == "all":
                    # Query all
                    data = self.cur.fetchall()
                else:
                    # Query single record
                    data = self.cur.fetchone()
                return data
            except AttributeError as error_data:
                ERROR.logger.error("Database connection failed, reason: %s", error_data)
                raise

        def execute(self, sql: Text):
            """
                Update, delete, insert
                :param sql:
                :return:
                """
            try:
                # Use execute to operate sql
                rows = self.cur.execute(sql)
                # Commit transaction
                self.conn.commit()
                return rows
            except AttributeError as error:
                ERROR.logger.error("Database connection failed, reason: %s", error)
                # If transaction fails, rollback data
                self.conn.rollback()
                raise

        @classmethod
        def sql_data_handler(cls, query_data, data):
            """
            Handle data format for certain types of sql query results
            @param query_data: sql data returned from query
            @param data: data pool
            @return:
            """
            # Put all content returned by sql into the object
            for key, value in query_data.items():
                if isinstance(value, decimal.Decimal):
                    data[key] = float(value)
                elif isinstance(value, datetime.datetime):
                    data[key] = str(value)
                else:
                    data[key] = value
            return data


class SetUpMySQL(MysqlDB):
    """ Handle setup sql """

    def setup_sql_data(self, sql: Union[List, None]) -> Dict:
        """
            Handle setup request sql
            :param sql:
            :return:
            """
        sql = ast.literal_eval(cache_regular(str(sql)))
        try:
            data = {}
            if sql is not None:
                for i in sql:
                    # When the assertion type is a query type,
                    if i[0:6].upper() == 'SELECT':
                        sql_date = self.query(sql=i)[0]
                        for key, value in sql_date.items():
                            data[key] = value
                    else:
                        self.execute(sql=i)
            return data
        except IndexError as exc:
            raise DataAcquisitionFailed("sql data query failed, please check if the setup_sql statement is correct") from exc


class AssertExecution(MysqlDB):
    """ Handle assertion sql data """

    def assert_execution(self, sql: list, resp) -> dict:
        """
         Execute sql, responsible for handling scenarios in yaml files where assertions need to execute multiple sql statements,
         and will ultimately return all data in object form
        :param resp: interface response data
        :param sql: sql
        :return:
        """
        try:
            if isinstance(sql, list):

                data = {}
                _sql_type = ['UPDATE', 'update', 'DELETE', 'delete', 'INSERT', 'insert']
                if any(i in sql for i in _sql_type) is False:
                    for i in sql:
                        # Check if there is a regex in sql, if so extract the relevant data via jsonpath
                        sql = sql_regular(i, resp)
                        if sql is not None:
                            # Process assertion sql one by one in a for loop
                            query_data = self.query(sql)[0]
                            data = self.sql_data_handler(query_data, data)
                        else:
                            raise DataAcquisitionFailed(f"This sql query returned no data, {sql}")
                else:
                    raise DataAcquisitionFailed("Assertion sql must be a query sql")
            else:
                raise ValueTypeError("sql data type is incorrect, expected list")
            return data
        except Exception as error_data:
            ERROR.logger.error("Database connection failed, reason: %s", error_data)
            raise error_data


if __name__ == '__main__':
    a = MysqlDB()
    b = a.query(sql="select * from `test_obp_configure`.lottery_prize where activity_id = 3")
    print(b)
