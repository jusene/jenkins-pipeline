#!/usr/bin/env python
# -*- coding=utf-8 -*-

import argparse
import os
import sys
import subprocess
import urllib2
import json
import logging
from check import check
import time

basedir = os.path.dirname(os.path.abspath(__file__))


# 设置解析参数
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", '--appname', help="Get deploy appname")
    parser.add_argument("-e", '--env', help="Get deploy env")
    parser.add_argument("-u", '--url', help="Get package url")
    parser.add_argument("-t", '--time', help="Get package timestamp")
    parser.add_argument("-p", '--project', help="Get project name")
    parser.add_argument("-v", '--version', help="Get project version")
    parser.add_argument("-d", "--dir", default=None, help="Get nginx dir name")
    parser.add_argument("-f", "--first", default=None, help="Get node first deploy")
    parser.add_argument("-n", "--node", default=None, help="Get node name")
    args = parser.parse_args()
    return args


# 设置资源解析
def manifest(appname, env):
    header = {"User-Agent": "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
              "Accept": "application/json"}
    request = urllib2.Request("http://192.168.55.156:5000/deploy?app={app}&env={env}".format(app=appname, env=env),
                              headers=header)
    resp = urllib2.urlopen(request)
    config = json.loads(resp.read())
    return config


# 设置应用方法
class Deploy(object):
    def __init__(self, args):
        self.apps = args.appname
        self.env = args.env
        self.url = args.url
        self.time = args.time
        self.project = args.project
        self.version = args.version
        self.directory = args.dir
        self.first = args.first
        self.node = args.node

    def nodejs(self, host, app):
        logging.info('****** Deploy NodeJS App ******')
        retcode = subprocess.call(
            'ansible-playbook {playbook} -e host={ho} -e url={url} -e app={app} -e time={time} -e project={project} \
            -e env={env} -e version={version} -e dir={dir} -e node={node} -e first={first}'.format(
                playbook='/'.join([basedir, 'playbook', 'ansible_node.yml']),
                ho=host,
                url=self.url,
                app=app,
                time=self.time,
                project=self.project,
                version=self.version,
                env=self.env,
                dir=self.directory,
                node=self.node,
                first=self.first), shell=True)
        return retcode

    def java(self, host, app, jmx):
        logging.info('****** Deploy Java App ******')
        retcode = subprocess.call(
            'ansible-playbook {playbook} -e host={ho} -e url={url} -e app={app} -e time={time} -e project={project} \
             -e env={env} -e version={version} -e jmx={jmx}'.format(
                playbook='/'.join([basedir, 'playbook', 'ansible_java.yml']),
                ho=host,
                url=self.url,
                app=app,
                time=self.time,
                project=self.project,
                version=self.version,
                env=self.env,
                jmx=jmx), shell=True)
        # 健康检查
        if app not in ["iot-registe", "iot-turbine"] and self.project not in ["bigdata",]:
            health = check(host, app, self.env)
            check_times = 1
            while True:
                status = health.health_check()
                if status == "UP":
                    logging.info('****** {app} health check UP'.format(app=app))
                    return 0
                else:
                    check_times += 1
                    time.sleep(5)
                if check_times >= 10:
                    logging.error('****** {app} health check more than 10 times, still false.'.format(app=app))
                    return 2
        else:
            return retcode

    def js(self, host, app):
        logging.info('****** Deploy JavaScript App ******')
        retcode = subprocess.call(
            'ansible-playbook {playbook} -e host={ho} -e url={url} -e app={app} -e time={time} -e project={project} \
             -e env={env} -e version={version} -e dir={dir}'.format(
                playbook='/'.join([basedir, 'playbook', 'ansible_js.yml']),
                ho=host,
                url=self.url,
                app=app,
                time=self.time,
                project=self.project,
                version=self.version,
                env=self.env,
                dir=self.directory), shell=True)
        return retcode


if __name__ == "__main__":
    args = Parser()
    deploy = Deploy(args)
    for app in deploy.apps.split(','):
        config = manifest(app, deploy.env)
        hosts = config['hosts']
        jmx = config['jmx']
        for host in hosts:
            if deploy.directory is None:
                retcode = deploy.java(host, app, jmx)
            else:
                if deploy.node is None:
                    retcode = deploy.js(host, app)
                else:
                    retcode = deploy.nodejs(host, app)
            if retcode != 0:
                sys.exit(2)
