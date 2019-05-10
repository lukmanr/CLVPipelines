import argparse
import sys
import json
import logging
import uuid
from google.cloud import bigquery
from pathlib import Path


PREPROCESS_QUERY_TEMPLATE = 'preprocess.sql'
CREATE_FEATURES_QUERY_TEMPLATE = 'create_features.sql'
 
def run_query(query_template, project_id, dataset_id, table_id=None, **kwargs):
    """Runs a query and dumps output to BQ table"""
    
    # Generate a query from a query template
    for key, value in kwargs.items():
        query_template = query_template.replace('{{{{{}}}}}'.format(key), str(value))
            
    client = bigquery.Client(project=project_id)
    
    # If table_id not passed create a unique table name
    if not table_id:
        guid = uuid.uuid4()
        table_id = 'output_{}'.format(guid.hex)
        
    # Configure BQ to write output to a table
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.QueryJobConfig(
        destination=table_ref,
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE)
        
    # Execute the query
    query_job = client.query(query_template, job_config)
    query_job.result() # Wait for the query to finish
    
    return "{}.{}.{}".format(
        project_id, 
        dataset_id, 
        table_id)


def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project-id',
        type=str,
        required=True,
        help='The GCP project to run BQ processing.')
    parser.add_argument(
        '--dataset-id',
        type=str,
        required=True,
        help='BQ dataset of the output tables.')
    parser.add_argument(
        '--transactions-table-fqn',
        type=str,
        required=True,
        help='The input table - transactions.')
    parser.add_argument(
        '--features-table-name',
        type=str,
        required=False,
        help='The output table - features.')
    parser.add_argument(
        '--summaries-table-name',
        required=False,
        type=str,
        help='The output table - summaries.')
    parser.add_argument(
        '--threshold-date',
        type=str,
        required=True,
        help='Begining date for target value calculations.')
    parser.add_argument(
        '--predict-end',
        type=str,
        required=True,
        help='End date for target value calculations.')
    parser.add_argument(
        '--max-monetary',
        type=str,
        default=15000,
        help='Maximum monetary value.')
    parser.add_argument(
        '--output-features-table-fqn',
        type=str,
        required=False,
        help='The file to write the FQN of the order summaries table. Provided by KFP.')
    parser.add_argument(
        '--output-summaries-table-fqn',
        type=str,
        required=False,
        help='The file to write the FQN of the features table. Provided by KFP.')
 
  
    return parser.parse_args()

def main():
    logging.getLogger().setLevel(logging.INFO)
    args = _parse_arguments()

    with open(PREPROCESS_QUERY_TEMPLATE, 'r') as f:
        query = f.read() 

    summaries_table_fqn = run_query(
        query,
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        table_id=args.summaries_table_name,
        transactions_table_fqn=args.transactions_table_fqn,
        threshold_date=args.threshold_date,
        predict_end=args.predict_end)
    
    with open(CREATE_FEATURES_QUERY_TEMPLATE, 'r') as f:
        query = f.read()
        
    features_table_fqn = run_query(
        query,
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        table_id=args.features_table_name,
        summaries_table_fqn=summaries_table_fqn,
        threshold_date=args.threshold_date,
        max_monetary=args.max_monetary)
    
    # Save output table FQNs to output
    Path(args.output_summaries_table_fqn).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_summaries_table_fqn).write_text(summaries_table_fqn)
    Path(args.output_features_table_fqn).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_features_table_fqn).write_text(features_table_fqn)



if __name__ == '__main__':
    main()
    
    