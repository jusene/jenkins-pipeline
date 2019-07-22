#!/usr/bin/env python
# -*- coding=utf-8 -*-

import json
from models import consulclient as consul
import logging

c = consul.ConsulClient("10.192.180.33", 8500)

def register(body):
    try:
        name = body['name']
        service_id = body['id']
        address = body['address']
        port = body['port']
        tags = body.get('tags')
        logging.info("*** register {}:{}".format(name, service_id))
        ret = c.register(name, service_id, address, port, tags)
        return json.dumps({"code": 200, "message": ret})
    except Exception as e:
        return json.dumps({"code": 400, "message": e})
    
def deregister(service_id):
    try:
        ret = c.deregister(service_id)
        return json.dumps({"code": 200, "message": ret})
    except Exception as e:
        return json.dumps({"code": 400, "message": e})
