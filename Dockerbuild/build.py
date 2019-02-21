#!/usr/bin/env python
# -*- coding=utf-8 -*-

import argparse
import os
import subprocess
import multiprocessing
import sys
import logging
from jinja2 import FileSystemLoader, Environment
from config import config

basedir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - Build - %(levelname)s: %(message)s")

# 设置解析参数
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", '--appname', help="Get deploy appname")
    parser.add_argument("-e", '--env', help="Get deploy env")
    parser.add_argument("-t", '--time', help="Get package timestamp")
    parser.add_argument("-p", '--project', help="Get project name")
    parser.add_argument("-v", '--version', help="Get project version")
    args = parser.parse_args()
    return args
      
# 构建docker
def DockerBuild(project, app, tag, build_dir):
    logging.info('****** Build Docker {} ******'.format(app))
    os.chdir(build_dir)
    retcode = subprocess.call("docker build -t {registry}/{project}/{app}:{tag} .".format(
                                                                                        registry=conf.DOCKER_REGISTRY, 
                                                                                        project=conf.PROJECT_NAME[project], 
                                                                                        app=app,
                                                                                        tag=tag), shell=True)
    if retcode != 0:
        logging.error('****** Build Docker {} ERROR !******'.format(app))
        sys.exit(2)
    retcode = subprocess.call("docker push {registry}/{project}/{app}:{tag}".format(
                                                                            registry=conf.DOCKER_REGISTRY,
                                                                            project=conf.PROJECT_NAME[project], 
                                                                            app=app,
                                                                            tag=tag), shell=True)
    if retcode != 0:
        logging.error('****** Push Docker {} ERROR !******'.format(app))
        sys.exit(3)
    os.chdir(basedir)

# jinja2模板渲染
def Jinja2Render(Jfile):
    env = Environment(loader=FileSystemLoader('/'.join([basedir,'templates'])))
    template = env.get_template(Jfile)
    return template


if __name__ == "__main__":
    arg = Parser()
    conf = config.get(arg.env)
    process_pool = []
    needcert = False
    for app in arg.appname.split(','):
        build_dir = '_'.join([app, 'docker'])
        if not os.path.exists(build_dir): os.mkdir(build_dir) 
        # 寻找jar包
        subprocess.call('find . -name %s-zjhw.jar -type f -exec mv -f {} %s \;' % (app, build_dir),shell=True)
        os.chdir(build_dir)
        if app in ["iot-service-lab"]:
            subprocess.call("mv ../cert .", shell=True)
            needcert = True
        # 生成docker-entrypoint.sh启动文件
        with open('docker-entrypoint.sh','w') as fp:
            template = Jinja2Render('docker-entrypoint.j2')
            fp.write(template.render(PROJECT=arg.project, VERSION=arg.version, APP=app))
        # 生成Dockerfile
        with open('Dockerfile', 'w') as fp:
            template = Jinja2Render('Dockerfile.j2')
            fp.write(template.render(PROJECT=arg.project, VERSION=arg.version, APP=app, CERT=needcert))
        
        # 生成线程
        p1 = multiprocessing.Process(target=DockerBuild, args=(arg.project, app, arg.time, build_dir))
        # 加入线程池
        process_pool.append(p1)
        os.chdir(basedir)
    
    # 线程并发构建
    for p in process_pool:
        p.start()


    

