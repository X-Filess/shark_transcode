# -*- coding: utf-8 -*-


"""
@author: djstava
@license: MIT Licence 
@contact: djstava@gmail.com
@site: http://www.xugaoxiang.com
@software: PyCharm
@file: SharkUtils.py
@time: 7/26/17 3:12 PM
"""

import os
import json
import logging
import requests

logger = logging.getLogger(__name__)


class SharkUtils(object):

    def __init__(self):
        pass

    @classmethod
    def checkTdtInfo(self):
        return os.path.exists('bin/tdtInfo')

    @classmethod
    def checkFfmpeg(self):
        return os.path.exists('bin/ffmpeg')

    @classmethod
    def parseSysJSON(self, path):
        '''
        解析系统配置文件sys.json
        :param path:
        :return:
        '''

        sys_json = {}

        jsonfile = open(path, "rb")
        data = jsonfile.read()
        json_dict = json.loads(data.decode("utf-8"))
        for key in json_dict.keys():
            if key == 'sys':
                try:
                    sys_json = json_dict[key]
                except:
                    print('json sys error.')
                    logger.error('json sys error.')

        jsonfile.close()

        return sys_json

    @classmethod
    def parseSharkJSONFromFile(self, path):
        service_json = {}
        mysql_json = {}
        srs_json = {}

        jsonfile = open(path, "rb")
        data = jsonfile.read()
        json_dict = json.loads(data.decode("utf-8"))
        for key in json_dict.keys():
            if key == 'service':
                try:
                    service_json = json_dict[key]
                except:
                    print('json service error.')
                    logger.error('json service error.')

            elif key == 'config':
                try:
                    mysql_json = json_dict[key]['mysql']
                    srs_json = json_dict[key]['srs']
                except:
                    print('json mysql/srs error.')
                    logger.error('json mysql/srs error.')

        jsonfile.close()

        return service_json, mysql_json, srs_json

    @classmethod
    def parseSharkFromNetwork(self, url):
        '''
        从CMS获取录制配置文件
        :return:
        '''

        if not url:
            return None

        service_json = {}
        mysql_json = {}
        srs_json = {}

        try:
            r = requests.get(url, timeout=3)
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            logger.error(e)

        json_data = r.json()
        print('json from network={}'.format(json_data))
        logger.debug('json from network={}'.format(json_data))

        if json_data['code'] == 1:
            print(type(json_data['data']))

            # 防止非标准的json,将单引号替换成双引号
            json_dict = json.loads(json_data['data'].replace("'", "\""))
            for key in json_dict.keys():
                if key == 'service':
                    try:
                        service_json = json_dict[key]
                    except:
                        print('json service error.')

                elif key == 'config':
                    try:
                        mysql_json = json_dict[key]['mysql']
                        srs_json = json_dict[key]['srs']
                    except:
                        print('json mysql/srs error.')
        else:
            print('json from network error.')
            logger.error('json from network error.')

        return service_json, mysql_json, srs_json