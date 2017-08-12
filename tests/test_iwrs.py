#! /usr/bin/env python
# -*- coding:utf-8 -*-

""" [NAME] iwrs.py テストコード
"""


import pytest
import iwrs


def test_load_setting_file():
    """ [FUNCTIONS] iwrs.load_setting_file テストコード
    """
    with pytest.raises(OSError):
        iwrs.load_setting_file("")
