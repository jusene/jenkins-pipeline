#!/usr/bin/env python
#-*- coding=utf-8 -*-

import requests
import argparse
import yaml
import random
import time
import sys
import health
import threading
from logger import log
from health import marathon_check


__author__ = zhanggx
logger = log()

class SaltApi(object):
    def __init__(self, salturl, saltname, saltpassword):
        self.__salturl = salturl
        self.__saltname = saltname
        self.__password = saltpassword

    def token(self, prefix='login'):
        json_body = {"eauth": "pam", "username": self.__saltname, "password": self.__password}
        resp = requests.post('/'.join((self.__salturl, prefix)), json=json_body)
        try:
            self.__token = resp.json()['return'][0]['token']
        except KeyError  as e:
            logger.exception('KeyError')
            sys.exit(2)

    def postrequest(self, json_body):
        self.token()
        header = {"X-Auth-Token":self.__token}
        resp = requests.post(self.__salturl, headers=header, json=json_body)
        return resp.json()

    def remote_execute(self, tgt, arg=None, fun='cmd.run'):
        self.token()
        header = {"X-Auth-Token": self.__token}
        print(header)
        json_body = {"client": "local", "tgt": tgt, "fun": fun, "arg": arg}
        print(self.__salturl)
        resp = requests.post(self.__salturl, headers=header, json=json_body)
        try:
            return resp.json()
        except KeyError:
            logger.exception('{0}执行出错，请检查minion是否正常!'.format(tgt))
            sys.exit(2)

def parser_args():
    paser = argparse.ArgumentParser()
    paser.add_argument('-a', '--app', help='appname info', action="store")
    paser.add_argument('-e', '--env', help='deploy env', action='store')
    paser.add_argument('-u', '--url', help='package resource url', action='store')
    paser.add_argument('-w', '--war', help='war package name', action='store')
    args = paser.parse_args()
    return args

def parser_conf(conf):
    with open(conf,encoding='utf-8') as fp:
        try:
            return yaml.load(fp)
        except Exception:
            logger.exception("yaml配置错误，请检查deploy.yaml文件!")
            sys.exit(2)

def main():
    logger = log()
    basedir = os.path.abspath('.')
    # 读取配置
    data = parser_conf(basedir+'/deploy.yaml')
    # 解析参数
    args = parser_args()
    app = args.app
    env = args.env
    url = args.url
    war = args.war

    if not app or not env or not url or not war:
        logger.error('参数解析失败,app: {0},env: {1},url: {2},war: {3}'.format(app, env, url,war))
        sys.exit(2)
    # 调度api接口
    api = SaltApi(data['salturl'], data['saltusername'], data['saltpassword'])
    try:
        project = data[app][env]['project']
        hosts = data[app][env]['host']
        pillar = {"projectname": project,'appname': app, 'url': url, 'warname': war}
    except Exception as e:
        logger.exception("无法找到app相应的属性，请检查deploy.yaml中{}的配置！".format(app))
        sys.exit(2)

    # 检查minion上是否有正在执行的任务
    for host in hosts:
        job_count = 1
        while job_count < 10:
            host_running = api.remote_execute(tgt=host['hostname'], fun='saltutil.running')
            if not host_running:
                try:
                    json_body = [{
                        "client": "local_async",
                        "tgt": host["hostname"],
                        "fun": "state.sls",
                        "kwarg": {"mods": '.'.join(('base', app, env)), "pillar": pillar}
                    }]
                    jid = api.postrequest(json_body)
                    logger.info('{0}:Executed command with job ID: {1}'.format(host['hostname'], jid))
                    break
                except Exception as e:
                    logger.exception('无法调用salt-minion...')
                    sys.exit(2)
            else:
                for k, v in host_running.items():
                    if k == 'jid':
                        logger.info('{0}:客户端正在执行任务，任务id为{1}'.format(host['hostname'],v))
                job_count += 1
                time.sleep(30)
                if job_count == 9:
                    logger.info('9次检查发现jid仍然在运行，清除僵死jid!')
                    api.remote_execute(host["hostname"],fun="saltutil.kill_job",arg=v)

    # 调度marathon api接口启动docker
    marathost = hosts[random.choice(range(len(hosts)))]['hostname']
    # 检查容器是否为marathon应用
    check_app = api.remote_execute(marathost,arg='ls /xinguang/{0}/bin/tomcat/{1}'.format(app,app+'.json'))
    if check_app['return'][0][marathost] == app+'.json':
        # 检查docker是否已经存在了
        check_marathon = requests.get('/'.join((data['marathonurl','v2','apps',env,project,app])))
        if 'message' in check_marathon.json():
            api.remote_execute(marathost, arg='curl -X POST {0} -d @{1} -H "Content-type: application/json"'.format(
                '/'.join((data['marathonurl'],'v2','apps')),"/xinguang/{}/bin/tomcat".format(app)))
        else:
            requests.delete('/'.join((data['marathonurl','v2','apps',env,project,app])))
            time.sleep(10)
            api.remote_execute(marathost, arg='curl -X POST {0} -d @{1} -H "Content-type: application/json"'.format(
                '/'.join((data['marathonurl'], 'v2', 'apps')), "/xinguang/{}/bin/tomcat".format(app)))
    else:
        logger.info('此项目不是marathon部署项目，无法完成请求！')
        sys.exit(2)


    # 健康状态检查
    time.sleep(60)
    docker_count = 1
    while docker_count < 10:
        result = marathon_check(env, project, app)
        time.sleep(30)
        if not result:
            logger.info('第{}次检查健康状态，未成功，请等待...'.format(docker_count))
            docker_count += 1

    logger.error('检测服务多次，未成功部署成功，应用服务已经报错，请自行查看应用启动日志!')
    sys.exit(1)

if __name__ == "__main__":
    main()
