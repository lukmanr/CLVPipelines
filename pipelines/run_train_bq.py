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
    
    return parser.parse_args()


args = _parse_arguments()


host = 'http://localhost:{}'.format(args.port)
client = kfp.Client(host)
experiment = client.create_experiment(args.experiment)
run_name = 'CLV train with BQ'

# Prepare pipeline arguments
arguments = {
    'project_id': args.project_id
}
# Submit the pipeline
run = client.run_pipeline(experiment.id, run_name, args.pipeline_file, arguments)
print(run.id)

result = client.wait_for_run_completion(run.id, timeout=600)
    
    