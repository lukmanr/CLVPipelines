import kfp
import argparse

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--port',
        type=int,
        default=8082,
        help='Forwarded port')
    parser.add_argument(
        '--experiment',
        type=str,
        default='CLV_BATCH_PREDICT',
        help='KFP experiment name.')
    parser.add_argument(
        '--pipeline_file',
        type=str,
        default='../compiled/clv_batch_predict.tar.gz',
        help='Pipeline file name.')
    parser.add_argument(
        '--project-id',
        type=str,
        default='sandbox-235500',
        help='The GCP project to run processing.')
    parser.add_argument(
        '--model-id',
        type=str,
        default='TBL403503175207747584',
        help='The ID of the model to use for predictions')
    parser.add_argument(
        '--datasource',
        type=str,
        default='gs://clv-testing/transactions',
        help='GCS location of the file with sales transactions.')
    parser.add_argument(
        '--bq_destination',
        type=str,
        default='bq://sandbox-235500',
        help='The Project ID for the prediction table')
    parser.add_argument(
        '--dataproc_gcs_output',
        type=str,
        default='gs://clv-testing/features',
        help='GCS location for CLV feature')
    parser.add_argument(
        '--pyspark_script_path',
        type=str,
        default='gs://clv-testing/scripts/create_features_and_label.py',
        help='GCS path to the PySpark preprocessing script')
     
    return parser.parse_args()


args = _parse_arguments()


host = 'http://localhost:{}'.format(args.port)
client = kfp.Client(host)
experiment = client.create_experiment(args.experiment)
run_name = 'CLV batch predict'

# Prepare pipeline arguments
arguments = {
    'project_id': args.project_id,
    'model_id': args.model_id,
    'datasource': args.datasource,
    'bq_destination': args.bq_destination,
    'dataproc_gcs_output': args.dataproc_gcs_output,
    'pyspark_script_path': args.pyspark_script_path
}

# Submit the pipeline
run = client.run_pipeline(experiment.id, run_name, args.pipeline_file, arguments)
print(run.id)

# Wait for completion
result = client.wait_for_run_completion(run.id, timeout=6000)
    
    