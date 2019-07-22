#!/usr/bin/env python
# -*- coding=utf-8 -*-

import os
import argparse
import subprocess
import urllib2
import json
import time
import sys
import logging
from jinja2 import Environment, FileSystemLoader
from config import config
from ansibleApi import ansibleRun


basedir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - Deploy - %(levelname)s: %(message)s")


def parser():
    '''
    analy parameter
    '''
    Parser = argparse.ArgumentParser()
    Parser.add_argument("-a", "--appname", help="Get app list" )
    Parser.add_argument("-e", "--env", help="Get env name")
    Parser.add_argument("-p", "--project", help="Get project name")
    Parser.add_argument("-t", "--timestamp", help="Get timestamp tag")
    return Parser.parse_args()


def check_health(app, env):
    '''
    request API 
    '''
    api = "http://{app}.{env}.sysadmin.com/actuator/health".format(app=app, env=env)
    try:
        resp = urllib2.urlopen(api)
        jdata = resp.read()
        logging.info("*** check health {} status {}".format(api, json.loads(jdata).get('status')))
        if json.loads(jdata).get('status') == 'UP':
            return True
    except Exception as e:
        logging.info("*** check health {} status {}, {}".format(api, "NotReady", e))
        return False

def jinja2render(jfile, *args, **kwargs):
    '''
    Jinja2 render
    '''
    env = Environment(loader=FileSystemLoader('/'.join([basedir, 'kubernetes', args[0]])))
    template = env.get_template(jfile)
    return template.render(kwargs)



if __name__ == "__main__":
    arg = parser()
    if not os.path.exists("k8s"): os.mkdir("k8s")
    os.chdir("k8s")
    for app in arg.appname.split(","):
        if app in config.get(arg.env).STATS:
            continue
        with open('{}-{}.yml'.format(app, arg.env), 'w') as fp:
            fp.write(jinja2render('{}.j2'.format(app), arg.project, ENV=arg.env, PROJECT=arg.project, TIMESTAMP=arg.timestamp))
        logging.info("*** create deployment {}".format(app))
        if arg.env == "prod":
            host_list = "192.168.66.128,"
        else:
            host_list = "192.168.66.155,"
        task_list = [
            dict(action=dict(module="copy", args="src={}-{}.yml dest=/ddhome/k8s".format(app, arg.env))),
            dict(action=dict(module="shell", args="/usr/local/bin/kubectl apply -f /ddhome/k8s/{}-{}.yml".format(app, arg.env)))
        ]
        ansibleRun(host_list, task_list)
        time.sleep(10)
        ## 确保config与eurake启动成功
        if app in config.get(arg.env).QUEUE:
            check_times = 1
            time.sleep(40)
            while not check_health(app, arg.env):
                time.sleep(5)
                check_times += 1
                if check_times > 30:
                    logging.error("*** check health {} more than 30 times, please check on http://kube-dashboard.sysadmin.com".format(app))
                    sys.exit(2)
            logging.info("*** check health {} UP".format(app))
