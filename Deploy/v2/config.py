#!/usr/bin/env python
# -*- coding=utf-8 -*-


class Config(object):
    DATABASE_URL = "mysql+pymysql://root:@127.0.0.1:3306/deploy?charset=utf8mb4"
    DATABASE_DEBUG = None
    DATABASE_POOL = 5
    DATABASE_POOL_OVERFLOW = -1
    DATABASE_POOL_TIMEOUT = 30
    DATABASE_POOL_RECYCLE = 300


class DevConfig(Config):
    def __init__(self):
        self.ENV = 'DEV'
        self.DATABASE_DEBUG = True


class TestConfig(Config):
    def __init__(self):
        self.ENV = 'TEST'
        self.DATABASE_DEBUG = True


class ProConfig(Config):
    def __init__(self):
        self.ENV = 'PRO'
        self.DATABASE_DEBUG = False


config = ProConfig()
