#!/usr/bin/env python
# -*- coding=utf-8 -*-


class Config:
    CONFIG_PORT = 8084


class DevConfig(Config):
    pass


class TestConfig(Config):
    pass


class ProdConfig(Config):
    pass


config = {
    "dev": DevConfig(),
    "test": TestConfig(),
    "prod": ProdConfig()
}