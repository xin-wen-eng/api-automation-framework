#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2022/3/28 10:56
"""
Log encapsulation, supports setting different log level colors
"""
import logging
from logging import handlers
from typing import Text
import colorlog
import time
from common.setting import ensure_path_sep


class LogHandler:
    """ Log printing encapsulation"""
    # Log level relationship mapping
    level_relations = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    def __init__(
            self,
            filename: Text,
            level: Text = "info",
            when: Text = "D",
            fmt: Text = "%(levelname)-8s%(asctime)s%(name)s:%(filename)s:%(lineno)d %(message)s"
    ):
        self.logger = logging.getLogger(filename)

        formatter = self.log_color()

        # Set log format
        format_str = logging.Formatter(fmt)
        # Set log level
        self.logger.setLevel(self.level_relations.get(level))
        # Output to screen
        screen_output = logging.StreamHandler()
        # Set the format displayed on screen
        screen_output.setFormatter(formatter)
        # Write to file # handler that automatically generates files at specified time intervals
        time_rotating = handlers.TimedRotatingFileHandler(
            filename=filename,
            when=when,
            backupCount=3,
            encoding='utf-8'
        )
        # Set the format written to file
        time_rotating.setFormatter(format_str)
        # Add objects to logger
        self.logger.addHandler(screen_output)
        self.logger.addHandler(time_rotating)
        self.log_path = ensure_path_sep('\\logs\\log.log')

    @classmethod
    def log_color(cls):
        """ Set log colors """
        log_colors_config = {
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red',
        }

        formatter = colorlog.ColoredFormatter(
            '%(log_color)s[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s',
            log_colors=log_colors_config
        )
        return formatter


now_time_day = time.strftime("%Y-%m-%d", time.localtime())
INFO = LogHandler(ensure_path_sep(f"\\logs\\info-{now_time_day}.log"), level='info')
ERROR = LogHandler(ensure_path_sep(f"\\logs\\error-{now_time_day}.log"), level='error')
WARNING = LogHandler(ensure_path_sep(f'\\logs\\warning-{now_time_day}.log'))

if __name__ == '__main__':
    ERROR.logger.error("test")
