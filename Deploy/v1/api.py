#!/usr/bin/env python
# -*- coding=utf-8 -*-

from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
import os
import yaml
import logging

app = Flask(__name__)
api = Api(app)

basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO, filename='/'.join([basedir,'api.log']), format="%(asctime)s - API - %(levelname)s: %(message)s")

def manifest(app, env):
    with open('/'.join([basedir,'manifest', env ,'deploy.yaml'])) as fp:
        config = yaml.load(fp)
    return config[app]


class Deploy(Resource):
    def get(self):
        try:
            env = request.args.get("env")
            app = request.args.get("app")
        except KeyError as e:
            abort(400)
        ho = list()
        try:
            data = manifest(app, env)
        except IOError as e:
            abort(400)
        try:
            jmx = data["jmx"]
        except KeyError as e:
            jmx = None
        hosts = data["hosts"]
        for host in hosts:
            ho.append(host["ip"])
        result = {
              "app": app,
              "env": env,
              "hosts": ho,
              "jmx": jmx
        }
        logging.info(result)
        return jsonify(result)

api.add_resource(Deploy, "/deploy")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
