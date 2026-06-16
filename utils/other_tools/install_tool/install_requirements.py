#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
# @Time    : 2022/5/10 14:02
# @Email   : 1603453211@qq.com
# @File    : install_requirements
# @describe: Check whether the program updates dependency libraries each time; if updated, install automatically
"""
import os
import chardet
from common.setting import ensure_path_sep
from utils.logging_tool.log_control import INFO
from utils import config

os.system("pip3 install chardet")


class InstallRequirements:
    """ Automatically detect and install the latest dependency libraries """

    def __init__(self):
        self.version_library_comparisons_path = ensure_path_sep("\\utils\\other_tools\\install_tool\\") \
                                                + "version_library_comparisons.txt"
        self.requirements_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                                 + os.sep + "requirements.txt"

        self.mirror_url = config.mirror_source
        # On initialization, retrieve the latest version library

        # os.system("pip freeze > {0}".format(self.requirements_path))

    def read_version_library_comparisons_txt(self):
        """
        Get the default version comparison file
        @return:
        """
        with open(self.version_library_comparisons_path, 'r', encoding="utf-8") as file:
            return file.read().strip(' ')

    @classmethod
    def check_charset(cls, file_path):
        """Get the character set of the file"""
        with open(file_path, "rb") as file:
            data = file.read(4)
            charset = chardet.detect(data)['encoding']
        return charset

    def read_requirements(self):
        """Get the installation file"""
        file_data = ""
        with open(
                self.requirements_path,
                'r',
                encoding=self.check_charset(self.requirements_path)
        ) as file:

            for line in file:
                if "[0m" in line:
                    line = line.replace("[0m", "")
                file_data += line

        with open(
                self.requirements_path,
                "w",
                encoding=self.check_charset(self.requirements_path)
        ) as file:
            file.write(file_data)

        return file_data

    def text_comparison(self):
        """
        Version library comparison
        @return:
        """
        read_version_library_comparisons_txt = self.read_version_library_comparisons_txt()
        read_requirements = self.read_requirements()
        if read_version_library_comparisons_txt == read_requirements:
            INFO.logger.info("No updated version library detected in the program, automatic library installation has been skipped")
        # If different files are found in the program, install
        else:
            INFO.logger.info("An updated dependency library was detected in the program, automatic installation has been performed")
            os.system(f"pip3 install -r {self.requirements_path}")
            with open(self.version_library_comparisons_path, "w",
                      encoding=self.check_charset(self.requirements_path)) as file:
                file.write(read_requirements)


if __name__ == '__main__':
    InstallRequirements().text_comparison()
