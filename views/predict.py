
import os, os.path

from flask_swagger_ui import get_swaggerui_blueprint
import py_eureka_client.eureka_client as eureka_client
from flask import Flask, request, jsonify

from h2o.automl import H2OAutoML
import h2o
import pandas as pd
from flask_cors import CORS
from py_zipkin.zipkin import zipkin_span, ZipkinAttrs, Encoding
from py_zipkin.transport import BaseTransportHandler
import requests

app = Flask(__name__)
CORS(app)
## swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger_predict.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Workspaces_H2O_Flask-REST-Api"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


app = Flask(__name__)

# Register the Flask application with Eureka
eureka_client.init(
    eureka_server="http://localhost:9102/",
    app_name="predict-count-service",
    instance_port=5002,
    instance_ip="127.0.0.1"
)
CORS(app)

# Initialize the H2O cluster
h2o.init()


# Define a custom transport handler for Zipkin
class ZipkinTransportHandler(BaseTransportHandler):
    def get_max_payload_bytes(self):
        return None

    def send(self, encoded_span):
        body = encoded_span
        print(body)
        # Post the span details to the Zipkin URL
        requests.post(
            "http://localhost:9411/api/v2/spans",
            data=body,
            headers={'Content-Type': 'application/json'},
        )


zipkin_transport_handler = ZipkinTransportHandler()







### end swagger specific ###
#### http://localhost:5004/predict/GBM_2_AutoML_1_20240516_212404###
@app.route('/predict/<model>', methods=['POST'])  # prediction by choosing the model key
def predict(model):
    zipkin_attrs = ZipkinAttrs(
        trace_id=request.headers.get('X-B3-TraceID'),
        span_id=request.headers.get('X-B3-SpanID'),
        parent_span_id=request.headers.get('X-B3-ParentSpanID'),
        flags=request.headers.get('X-B3-Flags'),
        is_sampled=request.headers.get('X-B3-Sampled'),
    )

    # Decorate the function with Zipkin tracing
    with zipkin_span(
            service_name="predict-count-service",
            zipkin_attrs=zipkin_attrs,
            span_name="predict",
            transport_handler=zipkin_transport_handler,
            port=5002,
            sample_rate=100,
            encoding=Encoding.V2_JSON
    ):

        item_dict = {}
        model_name = os.path.join("ML_models", model)
        uploaded_model = h2o.load_model(model_name)
        testing = request.get_json()
        test = h2o.H2OFrame(testing)
        pred_ans = uploaded_model.predict(test).as_data_frame()
        item_dict['Prediction'] = pred_ans.predict.values[0].item()  # Convert to standard Python type
        print(item_dict)
    return jsonify(item_dict)  # Return the result as a JSON response


if __name__ == "__main__":
    app.run(port=5002, debug=True)