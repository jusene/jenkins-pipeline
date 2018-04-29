#!/usr/bin/env python
#!-*- coding=utf-8 -*-

import requests
import yaml
import sys
import os
import time
from logger import log

basedir = os.path.abspath('.')
logger = log()
class check(object):
    def __init__(self):
        try:
            with open(basedir+'/deploy.yaml') as fp:
                self.marathonurl = yaml.load(fp)['marathonurl']
        except Exception as e:
            logger.exception('获取marathon url失败，请检查deploy.yaml')
            sys.exit(2)
    def getRequest(self,env,project,app):
        try:
            resp = requests.get('/'.join((self.marathonurl,'v2/apps',env,project,app)),headers={'Content-type':'application/json'})
            return resp.json()
        except Exception as e:
            logger.exception('''
--------------------------------------------
无法获取Marathon api信息，此appid不存在或错误的appid!
请联系管理员进行处理！
--------------------------------------------                      
''')
            sys.exit(2)

def marathon_check(env,project,app):
    marathon = check()
    status = marathon.getRequest(env, project, app)
    try:
        host = status['app']['tasks'][0]['host']
    except Exception as e:
        logger.exception('''
无法获得主机资源，请联系管理员查看mesos的资源情况!
        ''')
        sys.exit(2)

    if status['app']['tasks'][0]['state'] == 'TASK_RUNNING' and status['app']['tasksUnhealthy'] == 0:
        memory = status['app']['mem']
        cpu = status['app']['cpus']
        url = status['app']['labels']['HAPROXY_0_VHOST']
        logger.info('''
----------------------------------------------
服务健康状态检查正常，服务正常启动!
----------------------------------------------
################容器部署详细情况#################
服务器内存:   {0:>5}M
服务器cpu:   {1:>5}C
服务访问地址: {2:>5} 
服务器主机:  {3:>5}
##############################################
        '''.format(memory, cpu, url, host))
        time.sleep(10)
        sys.exit(0)
    else:
        logger.info('''
-----------------------------------------------
服务正在部署中，请稍后...
服务部署服务器host: {0}
-----------------------------------------------
'''.format(host))
        return False
marathon_check('dev','jutong','axe')