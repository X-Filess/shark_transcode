# -*- coding: utf-8 -*-

"""
@author: djstava
@license: MIT Licence 
@contact: djstava@gmail.com
@site: http://www.xugaoxiang.com
@software: PyCharm
@file: setting.py
@time: 7/26/17 2:50 PM
"""

from logging.handlers import RotatingFileHandler

LOG_SETTING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "stream": "ext://sys.stdout"
        },

        "info_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "simple",
            "filename": "info.log",
            "maxBytes": 1048576000,
            "backupCount": 50,
            "encoding": "utf8"
        },

        "error_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "simple",
            "filename": "errors.log",
            "maxBytes": 104857600,
            "backupCount": 20,
            "encoding": "utf8"
        },

        "debug_file_handler": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "DEBUG",
            "formatter": "simple",
            "filename": "debug.log",
            "maxBytes": 104857600,
            "backupCount": 20,
            "encoding": "utf8"
        }
    },

    "loggers": {
        "my_module": {
            "level": "ERROR",
            "handlers": ["console"],
            "propagate": "no"
        }
    },

    "root": {
        "level": "DEBUG",
        "handlers": ["console", "error_file_handler", "debug_file_handler"]
    }
}