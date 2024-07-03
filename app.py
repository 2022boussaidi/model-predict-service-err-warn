from flask import Flask, jsonify, request, Response,json,render_template
from flask_mongoengine import MongoEngine
from mongoengine import *
from werkzeug.utils import secure_filename
import os,os.path
from bson.dbref import DBRef
from datetime import datetime
from h2o.automl import H2OAutoML
from flask_swagger_ui import get_swaggerui_blueprint
import h2o
from h2o.automl import H2OAutoML


app = Flask(__name__)
### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger_copy.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Workspaces_H2O_Flask-REST-Api"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###
if __name__ == "__main__":
    app.run(debug=True, port=5000) 