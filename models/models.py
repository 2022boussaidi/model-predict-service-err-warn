from flask import Flask, jsonify, request
from flask_mongoengine import MongoEngine
from mongoengine import *
from datetime import datetime

app = Flask(__name__)

app.config['MONGODB_SETTINGS'] = {
    'db':'db_name',
    'host':'localhost',
    'port':'27017'
}
app.config['MONGODB_SETTINGS'] = {
    'host':'mongodb://localhost:27017'}



db = MongoEngine(app)


class File(db.Document): 
    filename=db.StringField()
    path=db.StringField()
    created= DateTimeField(default=datetime.utcnow)
    content_type=db.StringField()
    def read(self):
           files = File.objects()
           return  jsonify(files), 200

    def Delete(self, id):
        files= File.objects.get_or_404(id=id)
        files.delete()
        return jsonify(str(files.id) + " " + 'deleted Successfuly'), 200

class Models(db.Document) :
    model_name=db.StringField()
    path=db.StringField()
    saved=   DateTimeField(default=datetime.utcnow) 
    def read(self):
           model= Models.objects()
           return  jsonify(model), 200

    def Delete(self, id):
        model = Models.objects.get_or_404(id=id)
        model.delete()
        return jsonify(str(model.id) + " " + 'deleted Successfuly'), 200



class Workspace(db.Document):
       
       CreationDate=   DateTimeField(default=datetime.utcnow)
       name = db.StringField()
       CreatedBy = db.StringField()
       files=db.ListField(db.ReferenceField(File))
       models=db.ListField(db.ReferenceField(Models))
       def write(self,body):
           body = request.get_json()
           workspace = Workspace(**body).save()
           return jsonify(workspace), 201
       def read(self):
           workspaces = Workspace.objects()
           return  jsonify(workspaces), 200
       def Read(self,id):
           workspace = Workspace.objects.get_or_404(id=id)
           return jsonify(workspace), 200
       def Delete(self,id):
           workspace = Workspace.objects.get_or_404(id=id)
           workspace.delete()
           return jsonify(str(workspace.id)+" "+ 'deleted Successfuly'), 200
       def Update(self,id,body):
           body = request.get_json()
           workspace = Workspace.objects.get_or_404(id=id)
           workspace.update(**body)
           return jsonify(str(workspace.id)+" "+ 'updated Successfuly'), 200