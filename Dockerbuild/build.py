#!/usr/bin/env python
# -*- coding=utf-8 -*-

import argparse
import os
import subprocess
import multiprocessing
import sys
import logging
import celery
import shutil
from jinja2 import FileSystemLoader, Environment
from config import config

ce = celery.Celery('proj',
                 broker = "amqp://rabbitadmin:rabbitadmin@192.168.55.91:5672//celery",
                 backend = "amqp://rabbitadmin:rabbitadmin@192.168.55.91:5672//celery"
)

basedir = os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, format="%(asctime)s - Build - %(levelname)s: %(message)s")
err = multiprocessing.Queue()
fin = multiprocessing.Queue()

# 设置解析参数
def Parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", '--appname', help="Get deploy appname")
    parser.add_argument("-e", '--env', help="Get deploy env")
    parser.add_argument("-t", '--time', help="Get package timestamp")
    parser.add_argument("-p", '--project', help="Get project name")
    parser.add_argument("-v", '--version', help="Get project version")
    parser.add_argument("-d", "--dir", default=None, help="Get dir name")
    args = parser.parse_args()
    return args
      
# 构建docker
def DockerBuild(project, app, tag, build_dir, env):
    logging.info('****** Build Docker {} ******'.format(app))
    os.chdir(build_dir)
    if env == 'prod':
        REGISTRY = conf.DOCKER_REGISTRY_PRO
    else:
        REGISTRY = conf.DOCKER_REGISTRY
    retcode = subprocess.call("docker build -t {registry}/{project}-{env}/{app}:{tag} .".format(
                                                                                        env=env,
                                                                                        registry=REGISTRY, 
                                                                                        project=project,
                                                                                        app=app,
                                                                                        tag=tag), shell=True)
    if retcode != 0:
        err.put(app)
    else:
        subprocess.call("docker push {registry}/{project}-{env}/{app}:{tag}".format(
                                                                            env=env,
                                                                            registry=REGISTRY,
                                                                            project=project, 
                                                                            app=app,
                                                                            tag=tag), shell=True)
    
    if project == "iot" and env == "cloud":
        logging.info("****** PUSH HUAWEI CLOUD REGISTRY ******")
        subprocess.call("docker tag {registry}/{project}-{env}/{app}:{tag} swr.cn-east-2.myhuaweicloud.com/zwzhbg/{app}".format(
                                                                                                                                  env=env,
                                                                                                                                  registry=REGISTRY,
                                                                                                                                  project=project,
                                                                                                                                  app=app,
                                                                                                                                  tag=tag), shell=True)
        subprocess.call("docker push swr.cn-east-2.myhuaweicloud.com/zwzhbg/{app}".format(app=app), shell=True)
    fin.put(1)
    os.chdir(basedir)

# jinja2模板渲染
def Jinja2Render(Jfile):
    env = Environment(loader=FileSystemLoader('/'.join([basedir,'templates'])))
    template = env.get_template(Jfile)
    return template


if __name__ == "__main__":
    arg = Parser()
    conf = config.get(arg.env)
    if arg.dir is None:
        process_pool = []
        for app in arg.appname.split(','):

            # 大数据与ai项目stat包处理, 无需构建docker
            if app in config.get(arg.env).STATS:
                jar = app+"-zjhw.jar"
                src = config.get(arg.env).HOST_IP
                srcpath = basedir+"/spring-cloud-{}-labs/{}/target".format(app.split('-')[0], app)
                dest = config.get(arg.env).stat_target
                destpath = '/ddhome/bin/{a}-lab-stat/lib/{a}-lab-stat.jar'.format(a=app.split('-')[0])
                logging.info("*** Copy {} to {}:{}".format(jar, dest, destpath))
                ce.send_task("proj.tasks.statCopy", [jar, src, srcpath, dest, destpath])
                continue

            build_dir = '_'.join([app, 'docker'])
            if not os.path.exists(build_dir): os.mkdir(build_dir) 
            # 寻找jar包
            jar_name = "{app}-zjhw.jar".format(app=app)
            for root, dirs, files in os.walk(".", topdown=False):
                if jar_name in files:
                    try:
                        shutil.move(os.path.join(root, jar_name), build_dir)
                    except shutil.Error:
                        pass
            
            os.chdir(build_dir)
            # 物联网证书文件带入
            if app in config.get(arg.env).CERTS:
                shutil.move("../cert", ".")

            # 加入字体库
            if app in config.get(arg.env).FONTS:
                shutil.copytree("../fonts", "fonts")

            # bin脚本带入
            if app in config.get(arg.env).HUAYUN_BIN:
                shutil.move("../spring-cloud-huayun-labs/{a}/target/bin".format(a=app), ".")
            elif app in config.get(arg.env).AI_BIN:
                shutil.move("../spring-cloud-ai-labs/{a}/target/bin".format(a=app), ".")
            elif app in config.get(arg.env).ARCH_BIN:
                shutil.move("../{a}/target/classes/bin".format(a=app), ".")
            else:
                pass

            # 生成docker-entrypoint.sh启动文件
            with open('docker-entrypoint.sh','w') as fp:
                dapp = app.replace("-", "_")
                port = config.get(arg.env).__dict__.get(dapp)
                template = Jinja2Render('docker-entrypoint.j2')
                fp.write(template.render(PROJECT=arg.project, VERSION=arg.version, APP=app, PORT=port))

            # 生成Dockerfile
            with open('Dockerfile', 'w') as fp:
                template = Jinja2Render('Dockerfile.j2')
                fp.write(template.render(PROJECT=arg.project, VERSION=arg.version, APP=app)) 
            
            # 生成进程对象
            p1 = multiprocessing.Process(target=DockerBuild, args=(arg.project, app, arg.time, build_dir, arg.env))
            # 加入进程池
            process_pool.append(p1)
            os.chdir(basedir)
        
        # 多进程并发构建
        for p in process_pool:
            p.start()
            
            
    else:
        # 前端设计
        if not os.path.exists("k8s"): os.mkdir("k8s")
        os.chdir("k8s")
        with open('Dockerfile', "w") as fp:
            template = Jinja2Render('Dockerfile2.j2')
            fp.write(template.render(PROJECT=arg.project, VERSION=arg.version, APP=arg.appname))
        shutil.move("../nginx/{}.conf".format(arg.appname), ".")
        shutil.move("../dist", ".")
        DockerBuild(arg.project, arg.appname, arg.time, ".", arg.env)

    # 读取错误队列，检测是否有构建失败的
    while not fin.qsize() == len(arg.appname.split(',')):
        if not err.empty():
            for _ in range(err.qsize()):
                logging.error('****** Build Docker {} ERROR !******'.format(err.get()))
            sys.exit(2)



    

