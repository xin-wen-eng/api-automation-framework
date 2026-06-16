"""
Desc : Custom function calls
# @Time : 2022/4/2 9:32 AM
# @Author : Yu Shaoqi
"""
import re
import datetime
import random
from datetime import date, timedelta, datetime
from jsonpath import jsonpath
from faker import Faker
from utils.logging_tool.log_control import ERROR


class Context:
    """ Regex replacement """
    def __init__(self):
        self.faker = Faker(locale='zh_CN')

    @classmethod
    def random_int(cls) -> int:
        """
        :return: Random number
        """
        _data = random.randint(0, 5000)
        return _data

    def get_phone(self) -> int:
        """
        :return: Randomly generated phone number
        """
        phone = self.faker.phone_number()
        return phone

    def get_id_number(self) -> int:
        """

        :return: Randomly generated ID card number
        """

        id_number = self.faker.ssn()
        return id_number

    def get_female_name(self) -> str:
        """

        :return: Female name
        """
        female_name = self.faker.name_female()
        return female_name

    def get_male_name(self) -> str:
        """

        :return: Male name
        """
        male_name = self.faker.name_male()
        return male_name

    def get_email(self) -> str:
        """

        :return: Generate email
        """
        email = self.faker.email()
        return email

    @classmethod
    def self_operated_id(cls):
        """Self-operated store ID """
        operated_id = 212
        return operated_id

    @classmethod
    def get_time(cls) -> str:
        """
        Calculate current time
        :return:
        """
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return now_time

    @classmethod
    def today_date(cls):
        """Get today's date at midnight"""

        _today = date.today().strftime("%Y-%m-%d") + " 00:00:00"
        return str(_today)

    @classmethod
    def time_after_week(cls):
        """Get the time one week later at midnight"""

        _time_after_week = (date.today() + timedelta(days=+6)).strftime("%Y-%m-%d") + " 00:00:00"
        return _time_after_week

    @classmethod
    def host(cls) -> str:
        from utils import config
        """ Get the API domain """
        return config.host

    @classmethod
    def app_host(cls) -> str:
        from utils import config
        """Get the app host"""
        return config.app_host


def sql_json(js_path, res):
    """ Extract json data from sql """
    _json_data = jsonpath(res, js_path)[0]
    if _json_data is False:
        raise ValueError(f"Failed to get jsonpath from sql {res}, {js_path}")
    return jsonpath(res, js_path)[0]


def sql_regular(value, res=None):
    """
    This handles dependent data in sql, replacing values by getting the jsonpath value from the API response
    :param res: return result used by jsonpath
    :param value:
    :return:
    """
    sql_json_list = re.findall(r"\$json\((.*?)\)\$", value)

    for i in sql_json_list:
        pattern = re.compile(r'\$json\(' + i.replace('$', "\$").replace('[', '\[') + r'\)\$')
        key = str(sql_json(i, res))
        value = re.sub(pattern, key, value, count=1)

    return value


def cache_regular(value):
    from utils.cache_process.cache_control import CacheHandler

    """
    Read cache contents using regex
    Example: $cache{login_init}
    :param value:
    :return:
    """
    # Use regex to get the value inside $cache{login_init} --> login_init
    regular_dates = re.findall(r"\$cache\{(.*?)\}", value)

    # The result is a list, iterate over the data
    for regular_data in regular_dates:
        value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
        if any(i in regular_data for i in value_types) is True:
            value_types = regular_data.split(":")[0]
            regular_data = regular_data.split(":")[1]
            # pattern = re.compile(r'\'\$cache{' + value_types.split(":")[0] + r'(.*?)}\'')
            pattern = re.compile(r'\'\$cache\{' + value_types.split(":")[0] + ":" + regular_data + r'\}\'')
        else:
            pattern = re.compile(
                r'\$cache\{' + regular_data.replace('$', "\$").replace('[', '\[') + r'\}'
            )
        try:
            # cache_data = Cache(regular_data).get_cache()
            cache_data = CacheHandler.get_cache(regular_data)
            # Use sub method to replace the already retrieved content
            value = re.sub(pattern, str(cache_data), value)
        except Exception:
            pass
    return value


def regular(target):
    """
    New version
    Use regex to replace request data
    :return:
    """
    try:
        regular_pattern = r'\${{(.*?)}}'
        while re.findall(regular_pattern, target):
            key = re.search(regular_pattern, target).group(1)
            value_types = ['int:', 'bool:', 'list:', 'dict:', 'tuple:', 'float:']
            if any(i in key for i in value_types) is True:
                func_name = key.split(":")[1].split("(")[0]
                value_name = key.split(":")[1].split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                regular_int_pattern = r'\'\${{(.*?)}}\''
                target = re.sub(regular_int_pattern, str(value_data), target, 1)
            else:
                func_name = key.split("(")[0]
                value_name = key.split("(")[1][:-1]
                if value_name == "":
                    value_data = getattr(Context(), func_name)()
                else:
                    value_data = getattr(Context(), func_name)(*value_name.split(","))
                target = re.sub(regular_pattern, str(value_data), target, 1)
        return target

    except AttributeError:
        ERROR.logger.error("Corresponding replacement data not found, please check if the data is correct %s", target)
        raise


if __name__ == '__main__':
    a = "${{host()}} aaa"
    b = regular(a)
