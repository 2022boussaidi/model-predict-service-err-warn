from flask import Flask,  request
from flask_mongoengine import MongoEngine
from werkzeug.utils import secure_filename
import os,os.path
from models.models import Workspace
from models.models import File


app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db':'db_name',
    'host':'localhost',
    'port':'27017'
}
app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb://localhost:27017'}



db = MongoEngine(app)


@app.route('/files', methods=['GET'])  
def get_files():  
        obj=File()
        return (obj.read())
@app.route('/files/<id>', methods=['DELETE'])
def delete_file(id):
    obj=File()
    return (obj.Delete(id))
@app.route('/workspaces/files/<id>', methods=['POST'])
def add_file_id(id):
    workspace = Workspace.objects.get_or_404(id=id)
    f=File()
    fd= request.files['file']
    f.filename=fd.filename
    f.content_type=fd.content_type
    f.path=os.path.join(os.path.abspath('files'),fd.filename)
    filename = secure_filename(fd.filename)
    fd.save( filename)
    f.save()
    workspace.files.append(f)
    workspace.save()
    return("file added successefully")
if __name__ == "__main__":
    app.run(port=5002, debug=True)