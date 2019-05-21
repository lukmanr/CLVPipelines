arguments = {
    'project_id': 'sandbox-235500',
    'source_table_id': 'sandbox-235500.CLVDataset.transactions',
    'features_dataset_id': 'CLVDataset',
    'features_table_id': 'clv_features',
    'threshold_date': '2011-08-08',
    'predict_end': '2011-12-12'
}

HOST = 'http://localhost:8082'
EXPERIMENT_NAME = 'CLV_TRAINING'

client = kfp.Client(HOST)
experiment = client.create_experiment(EXPERIMENT_NAME)

run_name = pipeline_func.__name__ + ' run'
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)

