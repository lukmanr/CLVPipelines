import argparse
import sys
import json
import logging
import uuid
from google.cloud import bigquery
from pathlib import Path


PREPROCESS_QUERY_TEMPLATE = 'preprocess.sql'

 
def run_query(query, project_id, dataset_id, table_id=None):
    """Runs a query and dumps output to BQ table"""
                
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
    query_job = client.query(query, job_config)
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
        '--transactions-table-id',
        type=str,
        required=True,
        help='The ID of the table with input transactions.')
    parser.add_argument(
        '--features-table-name',
        type=str,
        required=False,
        help='The name of the output table.')
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
        '--output-table-id',
        type=str,
        required=False,
        help='The file to write the ID of the features table. Provided by KFP.')

  
    return parser.parse_args()

def main():
    args = _parse_arguments()

    # Load a query template
    with open(PREPROCESS_QUERY_TEMPLATE, 'r') as f:
        query_template = f.read() 

    # Substitute the query template's parameters
    query = query_template.format(
        transactions_table_id=args.transactions_table_id,
        threshold_date=args.threshold_date,
        predict_end=args.predict_end,
        max_monetary=args.max_monetary)
    
    # Run the query
    features_table_id = run_query(
        query,
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        table_id=args.features_table_name)
    
    
    logging.info("Wrote features to table: {}".format(features_table_id))
    
    # Save output table FQNs to output
    Path(args.output_table_id).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_table_id).write_text(features_table_id)



if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
    
    