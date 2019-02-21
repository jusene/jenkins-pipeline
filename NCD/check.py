#!/usr/bin/env python
# -*- coding=utf-8 -*-

import json
import urllib2
import logging
import sys
from config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - Deploy - %(levelname)s: %(message)s")

class check:
    def __init__(self, host, app, env):
        self.host = host
        self.app = app
        self.env = env

    def get_config_url(self):
        return "http://{host}:{port}/{app}/{env}".format(host=self.host,
                                                         port=config.get(self.env).CONFIG_PORT,
                                                         app=self.app,
                                                         env=self.env)

    def get_health_url(self, port):
        return "http://{host}:{port}/actuator/health".format(host=self.host,
                                                             port=port)

    def get_service_port(self):
        try:
            resp = urllib2.urlopen(self.get_config_url())
            conf = json.loads(resp.read())
            return conf['propertySources'][0]['source']['server.port']
        except Exception as e:
            if self.app == "iot-config":
                return config.get(self.env).CONFIG_PORT
            else:
                logging.info(self.get_config_url())
                logging.info("****** Get {app} service port fail, please check {app} or iot-config".format(app=self.app))

    def health_check(self):
        try:
            service_port = self.get_service_port()
            resp = urllib2.urlopen(self.get_health_url(service_port))
            health = json.loads(resp.read())
            return health['status']
        except Exception as e:
            logging.info(self.get_health_url(service_port))
            logging.info("****** Check {app} service fail, please check {app} or eureka".format(app=self.app))



