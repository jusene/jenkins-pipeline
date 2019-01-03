from flask import Flask, request, jsonify
from flask_restful import Api, Resource, abort
from sqlalchemy import and_
from .model import session, AppDeploy
import logging
import os

app = Flask(__name__)
api = Api(app)
basedir=os.path.dirname(os.path.abspath(__file__))
logging.basicConfig(level=logging.INFO, filename='/'.join([basedir,'access.log']), format='%(asctime)s - %(levelname)s: %(message)s')

class Deploy(Resource):
    def get(self):
        environment = request.args.get('env')
        appname = request.args.get('app')
        try:
            row = session.query(AppDeploy).filter(and_(AppDeploy.appname == appname,
                                                       AppDeploy.env == environment)).one()
            result = {
                "app": row.appname,
                "env": row.env,
                'jmx': row.jmx,
                'hosts': list(map(lambda x: x.ip, row.group.hosts))
            }
            logging.info(result)
            return jsonify(result)
        except Exception as e:
            abort(500)
        finally:
            session.close()

    def delete(self):
        environment = request.args.get("env")
        appname = request.args.get("app")
        try:
            session.query(AppDeploy).filter(and_(AppDeploy.appname == appname,
                                                 AppDeploy.env == environment)).delete()
            session.commit()
            return jsonify({"app": appname, "env": environment, "action": "delete", "msg": True})
        except Exception as e:
            session.rollback()
            return jsonify({"app": appname, "env": environment, "action": "delete", "meg": e})


api.add_resource(Deploy, '/deploy')

