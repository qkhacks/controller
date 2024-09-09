import os
import pymongo
from dotenv import *
from flask import Flask, request, jsonify, g

from api import *
from lib.identity import *
from lib.project import *
from lib.infra import *
from web import *

app = Flask(__name__)
load_dotenv()

jwt_signing_key = os.getenv("JWT_SIGNING_KEY")
db = pymongo.MongoClient(os.getenv("DB_HOST"), int(os.getenv("DB_PORT"))).controller

organization_service = OrganizationService(db.organizations)
user_service = UserService(db.users, organization_service, jwt_signing_key)
project_access_service = ProjectAccessService(db.project_accesses)
project_service = ProjectService(db.projects, project_access_service, user_service)
data_center_service = DataCenterService(db.data_centers, project_access_service)

HealthApi(app).register()
OrganizationApi(app, organization_service).register()
UserApi(app, user_service).register()
ProjectApi(app, project_service).register()
DataCenterApi(app, data_center_service).register()

Web(app).register()

@app.before_request
def before_request():
    g.request_body = request.get_json(force=True, silent=True)
    g.db = db
    g.jwt_signing_key = jwt_signing_key


@app.errorhandler(404)
def handle_404_error(e):
    return jsonify({
        "success": False,
        "message": str(e)
    }), 404


@app.errorhandler(Exception)
def handle_all_errors(e):
    return jsonify({
        "success": False,
        "message": str(e)
    }), 500


if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=int(os.getenv("PORT")), debug=os.getenv("ENV") != "PROD")
