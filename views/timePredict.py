from flask import Flask, jsonify, request
import h2o
from h2o.automl import H2OAutoML
import pandas as pd

app = Flask(__name__)

# Initialize the H2O cluster
h2o.init()


# Function to prepare and train the model
def train_model():
    # Correct dataset with consistent lengths
    data = {
        "@timestamp per day": [
            "2024-05-11", "2024-05-11", "2024-05-12", "2024-05-12", "2024-05-13", "2024-05-13",
            "2024-05-14", "2024-05-14", "2024-05-15", "2024-05-15", "2024-05-16", "2024-05-16",
            "2024-05-17", "2024-05-17", "2024-05-18", "2024-05-18", "2024-05-19", "2024-05-19",
            "2024-05-20", "2024-05-20", "2024-05-21", "2024-05-21", "2024-05-22", "2024-05-22",
            "2024-05-23", "2024-05-23", "2024-05-24", "2024-05-24", "2024-05-25", "2024-05-25",
            "2024-05-26", "2024-05-26", "2024-05-27", "2024-05-27", "2024-05-28", "2024-05-28",
            "2024-05-29", "2024-05-29",
        ],
        "Top 8 unusual terms in loglevel.keyword": [
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR", "WARN", "ERR", "WARN", "ERR",
            "WARN", "ERR"
        ],
        "Count": [
            838883, 120657, 847947, 131419, 1034517, 132758,
            1037594, 138390, 1095740, 188132, 1252447, 199917,
            943302, 140777, 864344, 128762, 1042209, 138272,
            922828, 135289, 956096, 130638, 1112480, 149398,
            982640, 146320, 965195, 128745, 1141922, 234476,
            915702, 132765, 1280953, 151469, 1469002, 186118,
            1020298, 131483,
        ]
    }

    df = pd.DataFrame(data)
    df['@timestamp per day'] = pd.to_datetime(df['@timestamp per day'])
    df.set_index('@timestamp per day', inplace=True)

    warn_series = df[df['Top 8 unusual terms in loglevel.keyword'] == 'WARN'][['Count']]
    err_series = df[df['Top 8 unusual terms in loglevel.keyword'] == 'ERR'][['Count']]

    def train_automl(series):
        series['@timestamp per day'] = series.index.strftime('%Y-%m-%d')

        h2o_df = h2o.H2OFrame(series)
        target = 'Count'
        features = ['@timestamp per day']

        aml = H2OAutoML(max_models=20, seed=1)
        aml.train(x=features, y=target, training_frame=h2o_df)
        return aml.leader

    warn_model = train_automl(warn_series)
    err_model = train_automl(err_series)

    return warn_model, err_model


warn_model, err_model = train_model()


@app.route('/predict', methods=['GET'])
def predict():
    log_level = request.args.get('log_level', 'WARN')
    steps = int(request.args.get('steps', 1))

    future_dates = pd.date_range(start=pd.Timestamp.now(), periods=steps + 1, freq='D')[1:]
    future_df = pd.DataFrame({'@timestamp per day': future_dates.strftime('%Y-%m-%d')})
    future_h2o_df = h2o.H2OFrame(future_df)

    if log_level.upper() == 'WARN':
        predictions = warn_model.predict(future_h2o_df)
    elif log_level.upper() == 'ERR':
        predictions = err_model.predict(future_h2o_df)
    else:
        return jsonify({'error': 'Invalid log_level'}), 400

    predicted_counts = predictions.as_data_frame().to_dict(orient='records')

    return jsonify(predicted_counts)


# Run the Flask app
if __name__ == '__main__':
    app.run()
