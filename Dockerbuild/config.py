#!/usr/bin/env python
# -*- coding=utf-8 -*-

class Config:
    DOCKER_REGISTRY = 'reg.ops.com'
    PROJECT_NAME = {
        'iot': 'iot2',
        'bigdata': 'bigdata2'
    }

class DevConfig(Config):
    def __init__(self):
        self.BIN = ["huayun-lab-auth","huayun-lab-report"]

class TestConfig(Config):
    def __init__(self):
        self.BIN = ["huayun-lab-auth","huayun-lab-report"]

class ProdConfig(Config):
    def __init__(self):
        self.BIN = ["huayun-lab-auth","huayun-lab-report"]

config = {
    'dev': DevConfig(),
    'test': TestConfig(),
    'prod': ProdConfig()
}