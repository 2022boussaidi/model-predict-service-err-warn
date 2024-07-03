from flask import Flask, request
from werkzeug.utils import secure_filename
import os
from models.models import Workspace, File
from flask_swagger_ui import get_swaggerui_blueprint
import h2o
from h2o.automl import H2OAutoML
import pandas as pd

app = Flask(__name__)

# Swagger specific setup
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Workspaces_H2O_Flask-REST-Api"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

@app.route('/train', methods=['POST'])  # train models using a file uploaded in the request
def apload():
    # Initialize H2O
    h2o.init()

    # Get JSON data and file from the request
    json_data = request.form
    a_value = json_data["a_key"]
    fd = request.files['file']

    # Save the uploaded file
    file_path = os.path.join(os.path.abspath('files'), secure_filename(fd.filename))
    fd.save(file_path)

    # Import the file to H2O
    data = h2o.import_file(path=file_path, destination_frame="train")
    train, test = data.split_frame(ratios=[0.8])
    x = train.columns
    print(x)
    y = a_value
    x.remove(y)
    train[y] = train[y].asfactor()
    test[y] = test[y].asfactor()

    # Train the models using H2O AutoML
    aml = H2OAutoML(max_models=20, seed=1)
    aml.train(x=x, y=y, training_frame=train)
    lb = aml.leaderboard

    # Save models locally
    model_ids = list(lb['model_id'].as_data_frame().iloc[:, 0])
    model_ids_df = pd.DataFrame({'model_id': model_ids})
    out_path = "ML_models"
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for m_id in model_ids:
        mdl = h2o.get_model(m_id)
        h2o.save_model(model=mdl, path=out_path, force=True)
    h2o.export_file(lb, os.path.join(out_path, secure_filename(fd.filename) + '_algorithms'), force=True)
    lbdf = lb.head(rows=10).as_data_frame()
    js = lbdf.to_json()

    # Return the leaderboard as JSON
    return js

if __name__ == "__main__":
    app.run(port=5005, debug=True)
