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
        default='CLV_TRAIN_BQ',
        help='KFP experiment name.')
    parser.add_argument(
        '--pipeline_file',
        type=str,
        default='clv_train_bq_automl.tar.gz',
        help='Pipeline file name.')
    parser.add_argument(
        '--project-id',
        type=str,
        default='sandbox-235500',
        help='The GCP project to run processing.')
    parser.add_argument(
        '--source_table_id',
        type=str,
        default='sandbox-235500.CLVDataset.transactions',
        help='Source table id')
    parser.add_argument(
        '--threshold_date',
        type=str,
        default='2011-08-08',
        help='Threshold date')
    parser.add_argument(
        '--predict_end',
        type=str,
        default='2011-12-12',
        help='Predict end.')
 
    return parser.parse_args()


args = _parse_arguments()


host = 'http://localhost:{}'.format(args.port)
client = kfp.Client(host)
experiment = client.create_experiment(args.experiment)
run_name = 'CLV train with BQ'

# Prepare pipeline arguments
arguments = {
    'project_id': args.project_id,
    'source_bq_table_id': args.source_table_id,
    'threshold_date': args.threshold_date,
    'predict_end': args.predict_end
}
# Submit the pipeline
run = client.run_pipeline(experiment.id, run_name, args.pipeline_file, arguments)
print(run.id)

# result = client.wait_for_run_completion(run.id, timeout=600)
    
    