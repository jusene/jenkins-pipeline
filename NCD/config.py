#!/usr/bin/env python
# -*- coding=utf-8 -*-


class Config:
    CONFIG_PORT = 8084
    RESOURCE_PORT = 8808
    REGISTE_PORT = 8081
    TURBINE_PORT = 8080
    QUEUE = ['iot-registe', 'iot-config', 'huayun-common-eureka', 'huayun-common-config', 'config', 'registe', "ai-common-eureka", "ai-common-config"]
    STATS = ["ai-lab-stat", "huayun-lab-stat"]



class DevConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProdConfig(Config):
    pass


config = {
    "local": DevConfig(),
    "dev": DevConfig(),
    "test": TestConfig(),
    "pre": ProdConfig(),
    "prod": ProdConfig()
}