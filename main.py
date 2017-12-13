# -*- coding: utf-8 -*-

"""
@author: djstava
@license: MIT Licence 
@contact: djstava@gmail.com
@site: http://www.xugaoxiang.com
@software: PyCharm
@file: main.py
@time: 10/16/17 5:58 PM
"""

import os
import sys
import time
import datetime
import logging
import subprocess
import struct
import socket
import math

import fcntl
import pymysql
import signal

from threading import Thread

from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects import mysql
from sqlalchemy.orm.exc import NoResultFound

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from flask import Flask

from config import VERSION
from utils.SharkUtils import *
from database.mysqlop import *

logger = logging.getLogger(__name__)
flask_app = Flask(__name__)

def dumpInformation():
    '''
    输出软件基本信息
    :return:
    '''

    print("Shanghai LongJingtech Software, shark_transcode v{}".format(VERSION))
    logger.debug("Shanghai LongJingtech Software, shark_transcode v{}".format(VERSION))

def parseJSON(url):
    '''
    返回解析出来的录制列表、mysql数据库信息及视频服务器信息
    :return:
    '''

    if os.path.exists('config/settings.json'):
        # 如果本地存在配置文件，则解析，否则网络获取
        return SharkUtils.parseSharkJSONFromFile('config/settings.json')
    else:
        # 从网络获取录制信息
        return SharkUtils.parseSharkFromNetwork(url=url)

def startTranscode():
    '''
    开启线程，转码
    :return:
    '''
    
    cmd_connect = 'mysql+pymysql://{}:{}@{}:{}/{}?charset={}' \
                  .format(mysql_dict['username'], mysql_dict['passwd'], \
                          mysql_dict['server'], mysql_dict['port'], \
                          mysql_dict['dbname'], mysql_dict['charset'])

    engine = create_engine(cmd_connect, encoding="utf-8", echo=False, pool_size=100, pool_recycle=3600)

    for i in range(len(service_dict)):
        t = Thread(target=transcodeThread, args=(list(service_dict.keys())[i], engine))
        t.start()

def transcodeThread(serviceName, engine):
    '''
    转码线程
    :param serviceName:
    :return:
    '''

    # tsid & serviceid可以标识一路节目
    tsid = serviceName.split('+')[0]
    serviceid = serviceName.split('+')[1]
    
    while True:
        DBSession = sessionmaker(bind=engine)
        session = DBSession()
        
        try:
            item = session.query(Channel).filter(Channel.ts_id == tsid) \
                                         .filter(Channel.service_id == serviceid) \
                                         .filter(Channel.record_flag == '1') \
                                         .filter(Channel.slice_flag == None) \
                                         .first()
        except NoResultFound:
            print('No item need to transcode.')
            logging.debug('No item need to transcode.')
            time.sleep(3)
            session.close()
            continue
        
        if item:
            print('item st={},tsid={},serviceid={},slice_flag={}'.format(item.start_time, tsid, serviceid, item.slice_flag))
            logging.debug('item st={},tsid={},serviceid={}'.format(item.start_time, tsid, serviceid))
            
            fileName = '{}+{}+{}+.ts'.format(tsid, serviceid, item.start_time)
            url = '/{}/{}'.format(fileName.split('.')[0], srs_dict['suffix'])
            
            if not os.path.exists('{}/{}'.format(srs_dict['tsdir'], fileName)):
                print('file not exist, continue.')
                logging.error('file not exist, continue.')
                
                # 清空数据库中的录制标志位
                session.query(Channel).filter(Channel.ts_id == tsid) \
                                      .filter(Channel.service_id == serviceid) \
                                      .filter(Channel.start_time == item.start_time) \
                                      .update({Channel.record_flag : '0'}, synchronize_session = False)
                session.commit()
                session.close()
                continue
            
            # 切片时间有可能非常长，这里先close
            # session.close()
            
            if (srs_dict['servermode'] == 'local'):
                directory = fileName.split('.')[0]

                if not os.path.exists('{}/{}'.format(srs_dict['slicedir'], directory)):
                    os.mkdir('{}/{}'.format(srs_dict['slicedir'], directory))

            cmd = 'bin/ffmpeg -i {}/{} -loglevel quiet -vcodec libx264 -acodec aac -strict -2 -threads 0 -preset ultrafast -r 25 -crf 23 -vf yadif=3:0,scale=1280:720 -b:v {} -b:a {} -hls_list_size 0 -metadata service_provider="longjingtech" {}/{}/index.m3u8'.format(srs_dict['tsdir'], fileName, srs_dict['vbitrate'], srs_dict['abitrate'], srs_dict['slicedir'], directory)
            # print('slice cmd = {}'.format(cmd))
            # logging.debug('slice cmd = {}'.format(cmd))

            try:
                process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except:
                print('Popen ffmpeg exception.')
                logger.error('Popen ffmpeg exception.')

            transcoding_dict.append(fileName)
            # 等待进程结束，这里不能用wait()
            process.communicate()

            print('=== slice finish, {} ==='.format(fileName))
            logger.debug('=== slice finish, {} ==='.format(fileName))

            # 重新建立session
            # DBSession_update_slice = sessionmaker(bind=engine)
            # session_update_slice = DBSession_update_slice()

            session.query(Channel).filter(Channel.ts_id == tsid) \
                                  .filter(Channel.service_id == serviceid) \
                                  .filter(Channel.start_time == item.start_time) \
                                  .update({Channel.slice_flag: '1', Channel.url: url}, synchronize_session=False)
            session.commit()
            session.close()

            # 删除录制的ts文件
            os.remove("{}/{}".format(srs_dict['tsdir'], fileName))
            transcoding_dict.remove(fileName)
            continue
            
        else:
            time.sleep(1)
            session.close()
            continue

def spaceMonitorJob():
    '''
    当磁盘(切片存储的目录)利用率超过90%,程序退出
    :return:
    '''

    try:
        st = os.statvfs(srs_dict['slicedir'])
        total = st.f_blocks * st.f_frsize
        used = (st.f_blocks - st.f_bfree) * st.f_frsize
    except FileNotFoundError:
        print('check slicedir space error.')
        logger.error('check slicedir space error.')
        sched.remove_job(job_id='id_space_monitor')
        sched.shutdown(wait=False)
        sys.exit(-3)

    if used / total > float(srs_dict['spacethreshold']):
        print('No enough space, threshold: {}.'.format(float(srs_dict['spacethreshold'])))
        logger.debug('No enough space, threshold: {}.'.format(float(srs_dict['spacethreshold'])))
        sched.remove_job(job_id='id_space_monitor')
        sched.shutdown(wait=False)

        # 杀掉进程
        os.killpg(os.getpgid(os.getpid()), signal.SIGKILL)

        exit(-3)

def get_local_ip(ifname):
    '''
    获取IP地址
    :param ifname:
    :return:
    '''
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    inet = fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', ifname[:15].encode('utf8')))
    ret = socket.inet_ntoa(inet[20:24])
    return ret

@flask_app.route('/')
def index():
    '''
    web接口返回数据
    :return:
    '''

    ret_dict = {}
    ret_dict['Status'] = "Running"
    ret_dict['Service'] = service_dict
    ret_dict['Database'] = mysql_dict
    ret_dict['Srs'] = srs_dict
    ret_dict['Recording'] = transcoding_dict
    return str(ret_dict)

if __name__ == '__main__':
    '''
    工程入口函数
    '''

    # settings.json中的频道列表
    service_dict = {}

    # 数据库信息列表
    mysql_dict = {}

    # srs参数列表
    srs_dict = {}

    # 记录当前正在录制的节目
    transcoding_dict = []

    # 输出软件基本信息
    dumpInformation()

    if not SharkUtils.checkFfmpeg():
        print('ffmpeg not found.')
        logger.error('ffmpeg not found.')
        exit(-1)

    # 获取系统配置文件
    sys_dict = SharkUtils.parseSysJSON('config/sys.json')
    print('sys json: {}'.format(sys_dict))
    logging.info('sys json: {}'.format(sys_dict))

    # 获取参数列表, 优先本地，其次网络
    service_dict, mysql_dict, srs_dict = parseJSON(url=sys_dict['api'])
    if not len(service_dict):
        print('No service to record.')
        logger.error('No service to record.')
        exit(-1)

    if not len(mysql_dict):
        print('No mysql info.')
        logger.error('No mysql info.')
        exit(-1)

    if not len(srs_dict):
        print('No srs info.')
        logger.error('No srs info.')
        exit(-1)
    
    # 开始转码
    startTranscode()

    # 开启磁盘空间检测
    sched = BackgroundScheduler()
    intervalTrigger = IntervalTrigger(minutes=5)
    sched.add_job(spaceMonitorJob, trigger=intervalTrigger, id='id_space_monitor')
    sched.start()

    # 禁止apscheduler屏幕输出
    logging.getLogger('apscheduler.executors.default').propagate = False

    # 启动flask web服务
    flask_app.run(host=get_local_ip(ifname=srs_dict['interfacename']), port=srs_dict['webport'])