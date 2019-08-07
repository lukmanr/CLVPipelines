# Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Helper Lightweight Python components."""

import kfp
from kfp import dsl
from typing import NamedTuple


@kfp.dsl.python_component(name='Load transactions')
def load_sales_transactions(project_id: str, source_gcs_path: str,
                            source_bq_table: str, dataset_location: str,
                            dataset_name: str, table_id: str) -> str:
  """Loads historical sales transactions to BigQuery.

    If source_gcs_path is passed loads data from a CSV file in GCS.
    If source_bq_table is passed no load is executed and source table id is
    passed as
    an output. One and only one type of source must be specified.
  
  Args:
    project_id: A project ID for BigQuery.
    source_gcs_path: A URL to Cloud Storage location.
    source_bq_table: A URL to BigQuery location.
    dataset_location: The location of the destination BigQuery dataset.
    dataset_name: The name of the destination BiqQuery dataset.
    table_id: The ID of the destination table.
  """

  import uuid
  import logging
  from google.cloud import bigquery

  logging.basicConfig(level=logging.INFO)

  client = bigquery.Client(project=project_id)

  if source_gcs_path:
    # Create or get a dataset reference
    if not dataset_name:
      dataset_name = 'clv_dataset_{}'.format(uuid.uuid4().hex)
    dataset = bigquery.Dataset('{}.{}'.format(project_id, dataset_name))
    dataset.location = dataset_location
    dataset_ref = client.create_dataset(dataset, exists_ok=True)

    # Configure Load job settings
    job_config = bigquery.LoadJobConfig()
    job_config.schema = [
        bigquery.SchemaField('customer_id', 'STRING'),
        bigquery.SchemaField('order_date', 'DATE'),
        bigquery.SchemaField('quantity', 'INTEGER'),
        bigquery.SchemaField('unit_price', 'FLOAT')
    ]
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.create_disposition = bigquery.job.CreateDisposition.CREATE_IF_NEEDED
    job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE
    job_config.skip_leading_rows = 1

    if not table_id:
      table_id = 'transactions_{}'.format(uuid.uuid4().hex)

    # Start the load job
    logging.info('Importing data from {} to {}.{}'.format(
        source_gcs_path, dataset_name, table_id))
    load_job = client.load_table_from_uri(
        source_gcs_path, dataset_ref.table(table_id), job_config=job_config)

    # Wait for table load to complete
    load_job.result()

    output = '{}.{}.{}'.format(project_id, dataset_name, table_id)
  else:
    logging.info('Source data already in BigQuery: {}'.format(source_bq_table))
    output = source_bq_table

  return output


@kfp.dsl.python_component(name='Prepare query')
def prepare_feature_engineering_query(
    project_id: str, source_table_id: str, destination_dataset: str,
    features_table_name: str, threshold_date: str, predict_end: str,
    max_monetary: str,
    query_template_uri: str) -> NamedTuple('ComponentOutput', [(
        'query', str), ('dataset_name', str), ('table_name', str)]):
  """Generates a feature engineering query.

    This a lightweight Python KFP component that generates a query
    that processes an input BQ table with sales transactions into features
    that will be used for CLV model training. The component replaces
    placeholders in a query template with values passed as parameters.
  """

  import uuid
  import logging
  import re

  from jinja2 import Template
  from google.cloud import storage
  from google.cloud import bigquery

  logging.basicConfig(level=logging.INFO)
  logging.info(
      'Retrieving the query template from: {}'.format(query_template_uri))

  # Read a query template from GCS
  _, bucket, blob_name = re.split('gs://|/', query_template_uri, 2)
  blob = storage.Client(project_id).get_bucket(bucket).blob(blob_name)
  template = Template(blob.download_as_string().decode('utf-8'))

  # Substitute placeholders in the query template
  query = template.render(
      data_source_id=source_table_id,
      threshold_date=threshold_date,
      predict_end=predict_end,
      max_monetary=max_monetary)

  # Create unique destination dataset and table names if not set
  if not destination_dataset:
    destination_dataset = 'clv_dataset_{}'.format(uuid.uuid4().hex)

  if not features_table_name:
    features_table_name = 'clv_features_{}'.format(uuid.uuid4().hex)

  from collections import namedtuple
  output = namedtuple('ComponentOutput',
                      ['query', 'dataset_name', 'table_name'])

  return output(query, destination_dataset, features_table_name)
