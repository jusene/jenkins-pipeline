#!/usr/bin/env python
# -*- coding=utf-8 -*-

from consul import Consul
from consul import Check


class ConsulClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.consul = Consul(host, port)
    def register(self, name, service_id=None, address=None, port=None, tags=None, interval="5s", timeout="15s"):
        try:
            r = self.consul.agent.service.register(name, service_id=service_id, address=address, port=int(port), check=Check.tcp(host=address, port=int(port), interval=interval, timeout=timeout))
            return r
        except Exception as e:
            return e
    def deregister(self, service_id):
        try:
            r = self.consul.agent.service.deregister(service_id)
            return r
        except Exception as e:
            return e
