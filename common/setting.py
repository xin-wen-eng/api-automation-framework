#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time   : 2021/11/25 13:07

import os
from typing import Text


def root_path():
    """ Get the root path """
    path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return path


def ensure_path_sep(path: Text) -> Text:
    """Compatible with different OS path separators for Windows and Linux environments """
    if "/" in path:
        path = os.sep.join(path.split("/"))

    if "\\" in path:
        path = os.sep.join(path.split("\\"))

    return root_path() + path
