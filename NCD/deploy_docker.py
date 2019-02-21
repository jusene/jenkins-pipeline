#!/usr/bin/env python
# -*- coding=utf-8 -*-

import argparse
import os
import yaml
import sys
import subprocess
import urllib2
import json
import logging

basedir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - Deploy - %(levelname)s: %(message)s")


# 设置解析参数
def Parser():
    parser = argparse.ArgumentParser()  
    parser.add_argument("-a", '--appname', help="Get deploy appname")
    parser.add_argument("-e", '--env', help="Get deploy env")
    parser.add_argument("-u", '--url', help="Get package url")
    parser.add_argument("-t", '--time', help="Get package timestamp")
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


if __name__ == "__main__":
    args = Parser()
    for app in args.appname.split(','):
        config = manifest(app, args.env)
        hosts = config['hosts']
        jmx = config['jmx']
        for host in hosts:
            subprocess.call("ansible-playbook {playbook} -e env={env} -e url={url} -e time={time} -e host={host}  -e app={app}".format(
                                                                                                            host=host,
                                                                                                            app=app, 
                                                                                                            playbook='/'.join([basedir, 'playbook', 'ansible_java_docker.yml']), 
                                                                                                            env=args.env, 
                                                                                                            url=args.url,
                                                                                                            time=args.time), shell=True)