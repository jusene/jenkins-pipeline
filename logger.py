#!/usr/bin/env python
#!-*- coding=utf-8 -*-

import logging


def log():
    logger = logging.getLogger('SaltStack')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    return logger