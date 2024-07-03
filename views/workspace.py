from flask import Flask,  request
from flask_mongoengine import MongoEngine
from flask_swagger_ui import get_swaggerui_blueprint
from models.models import Workspace

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
app.config['MONGODB_SETTINGS'] = {
    'db':'db_name',
    'host':'localhost',
    'port':'27017'
}
app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb://localhost:27017'}



db = MongoEngine(app)
@app.route('/workspaces', methods=['POST'])
def create_workspace():
        obj=Workspace() 
        body= request.get_json()
        return (obj.write(body))   

@app.route('/workspaces', methods=['GET'])  
def get_workspaces():  
        obj=Workspace()
        return (obj.read())  
@app.route('/workspaces/<id>', methods=['GET'])
def get_workspace(id): 
        obj=Workspace()
        return (obj.Read(id)) 
@app.route('/workspaces/<id>', methods=['DELETE'])
def delete_workspace(id):
    obj=Workspace()  
    return (obj.Delete(id))      
@app.route('/workspaces/<id>', methods=['PUT'])
def update_workspace(id): 
    obj=Workspace() 
    body= request.get_json()
    return (obj.Update(id,body))

if __name__ == "__main__":
    app.run(port=5000, debug=True)