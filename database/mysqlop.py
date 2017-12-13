# -*- coding: utf-8 -*-


"""
@author: djstava
@license: MIT Licence 
@contact: djstava@gmail.com
@site: http://www.xugaoxiang.com
@software: PyCharm
@file: mysqlop.py
@time: 7/27/17 11:24 AM
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, INTEGER, String, SMALLINT
import pymysql

# 创建对象的基类:
Base = declarative_base()

# 定义Channel对象:
class Channel(Base):

    # 表名
    __tablename__ = 'events'

    # structure
    ts_id = Column(INTEGER, primary_key=True)
    service_id = Column(INTEGER)
    event_id = Column(INTEGER)
    event_name = Column(String)
    start_time = Column(INTEGER)
    end_time = Column(INTEGER)
    url = Column(String)
    record_flag = Column(SMALLINT)
    slice_flag = Column(SMALLINT)

    def __init__(self, ts_id, service_id, event_id, event_name, start_time, end_time, url, record_flag, slice_flag):
        self.ts_id = ts_id
        self.service_id = service_id
        self.event_id = event_id
        self.event_name = event_name
        self.start_time = start_time
        self.end_time = end_time
        self.url = url
        self.record_flag = record_flag
        self.slice_flag = slice_flag