# -*- coding: utf-8 -*-


"""
@author: djstava
@license: MIT Licence 
@contact: djstava@gmail.com
@site: http://www.xugaoxiang.com
@software: PyCharm
@file: __init__.py.py
@time: 7/26/17 2:50 PM
"""

VERSION = '1.0.3'

import logging.config
from .setting import LOG_SETTING

logging.config.dictConfig(LOG_SETTING)