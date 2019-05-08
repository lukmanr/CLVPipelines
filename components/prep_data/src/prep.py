import argparse
import sys
import json
import logging
import uuid
from google.cloud import bigquery


PREPROCESS_QUERY_TEMPLATE = 'preprocess.sql'
CREATE_FEATURES_QUERY_TEMPLATE = 'create_features.sql'
MAX_MONETARY=15000

def run_summarize_query(project_id, dataset_id, transactions_table_id, 
                        threshold_date, predict_end):
    """Clean input transactions and creater daily summaries"""
    
    # Replace the placeholders in the query template
    with open(PREPROCESS_QUERY_TEMPLATE, 'r') as f:
        query = f.read() 
    query = query.replace("<<project_id>>", project_id)
    query = query.replace("<<dataset_id>>", dataset_id)
    query = query.replace("<<threshold_date>>", threshold_date)
    query = query.replace("<<predict_end>>", predict_end)
    query = query.replace("<<transactions_table_id>>", transactions_table_id)
    
    table_id = _run_query(query, project_id, dataset_id)
    
    return table_id

def run_create_features_query(project_id, dataset_id, order_summaries_table_id, 
                              features_table_id, threshold_date, max_monetary):
    """Create features from daily summaries"""
    
    # Replace the placeholders in the query template
    with open(CREATE_FEATURES_QUERY_TEMPLATE, 'r') as f:
        query = f.read() 
   
    query = query.replace("<<project_id>>", str(project_id))
    query = query.replace("<<dataset_id>>", str(dataset_id))
    query = query.replace("<<threshold_date>>", str(threshold_date))
    query = query.replace("<<max_monetary>>", str(max_monetary))
    query = query.replace("<<order_summaries_table_id>>", str(order_summaries_table_id))
     
    table_id = _run_query(query, project_id, dataset_id, features_table_id)
    
    return table_id
    
 
def _run_query(query, project_id, dataset_id, table_id=None):
    """Runs a query and dumps output to BQ table"""
    
    client = bigquery.Client(project=project_id)
    
    # If table_id not passed create a unique table name
    if not table_id:
        guid = uuid.uuid4()
        table_id = 'clean' + guid.hex
        
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    job_config = bigquery.QueryJobConfig()
    job_config.create_disposition = bigquery.job.CreateDisposition.CREATE_IF_NEEDED
    job_config.write_dispostion = bigquery.job.WriteDisposition.WRITE_TRUNCATE
    job_config.destination = table_ref
    
       # Execute the query
    query_job = client.query(query, job_config)
    query_job.result() # Wait for the query to finish
    
    return table_id

def _delete_table(project_id, dataset_id, table_id):
    """Deletes a BQ table"""
    
    client = bigquery.Client(project=project_id)
    dataset_ref = client.dataset(dataset_id)
    table_ref = dataset_ref.table(table_id)
    client.delete_table()
    

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--project-id',
        type=str,
        required=True,
        help='The GCP project to run BQ processing')
    parser.add_argument(
        '--dataset-id',
        type=str,
        required=True,
        help='BQ dataset of the input (transactions) and output (features) tables')
    parser.add_argument(
        '--input-table-id',
        type=str,
        required=True,
        help='The input table - transactions.')
    parser.add_argument(
        '--output-table-id',
        type=str,
        required=True,
        help='The output table - features ')
    parser.add_argument(
        '--threshold-date',
        type=str,
        required=True,
        help='Begining date for target value calculations ')
    parser.add_argument(
        '--predict-end',
        type=str,
        required=True,
        help='End date for target value calculations ')
  
    
    return parser.parse_args()

def main():
    logging.getLogger().setLevel(logging.INFO)
    args = _parse_arguments()
    
    order_summaries_table_id = run_summarize_query(
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        transactions_table_id=args.input_table_id,
        threshold_date=args.threshold_date,
        predict_end=args.predict_end)
    
    run_create_features_query(
        project_id=args.project_id,
        dataset_id=args.dataset_id,
        order_summaries_table_id=order_summaries_table_id,
        features_table_id=args.output_table_id,
        threshold_date=args.threshold_date,
        max_monetary=MAX_MONETARY)
    
    _delete_table(args.project_id, args.dataset_id, order_summaries_table_id)
 
    
if __name__ == '__main__':
    main()
    
    