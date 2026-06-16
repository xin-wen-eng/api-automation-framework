#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
# @Time   : 2022/4/7 17:53
"""
import json
import allure
from utils.other_tools.models import AllureAttachmentType


def allure_step(step: str, var: str) -> None:
    """
    :param step: Step and attachment name
    :param var: Attachment content
    """
    with allure.step(step):
        allure.attach(
            json.dumps(
                str(var),
                ensure_ascii=False,
                indent=4),
            step,
            allure.attachment_type.JSON)


def allure_attach(source: str, name: str, extension: str):
    """
    Upload attachments, images, excel files, etc. to the allure report
    :param source: File path, equivalent to passing a file
    :param name: Attachment name
    :param extension: Attachment extension name
    :return:
    """
    # Get the suffix of the uploaded attachment to determine the corresponding attachment_type enum value
    _name = name.split('.')[-1].upper()
    _attachment_type = getattr(AllureAttachmentType, _name, None)

    allure.attach.file(
        source=source,
        name=name,
        attachment_type=_attachment_type if _attachment_type is None else _attachment_type.value,
        extension=extension
    )


def allure_step_no(step: str):
    """
    Operation step with no attachment
    :param step: Step name
    :return:
    """
    with allure.step(step):
        pass
