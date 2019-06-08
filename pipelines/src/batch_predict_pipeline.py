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
"""Batch Predict Pipeline."""

from config import LOCAL_SEARCH_PATHS, URL_SEARCH_PREFIXES, USE_SA_SECRET

from helper_components import (load_sales_transactions,
                               prepare_feature_engineering_query)
import kfp
from kfp import gcp

# Initialize component store
component_store = kfp.components.ComponentStore(LOCAL_SEARCH_PATHS,
                                                URL_SEARCH_PREFIXES)

# Create component factories
load_sales_transactions_op = kfp.components.func_to_container_op(
    load_sales_transactions)
prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
    prepare_feature_engineering_query)
engineer_features_op = component_store.load_component('bigquery/query')
batch_predict_op = component_store.load_component('aml-batch-predict')


# Define the batch predict pipeline
@kfp.dsl.pipeline(
    name='CLV Training BigQuery AutoML',
    description='CLV Training Pipeline using BigQuery for feature engineering and Automl Tables for model training'
)
def clv_batch_predict(
    project_id,
    source_gcs_path,
    source_bq_table,
    bq_dataset_name,
    transactions_table_name,
    features_table_name,
    threshold_date,
    predict_end,
    max_monetary,
    aml_model_id,
    destination_prefix,
    dataset_location='US',
    aml_compute_region='us-central1',
    query_template_uri='gs://clv-pipelines/scripts/create_features_template.sql'
):
  """Prepares and scores sales transactions dataset."""

  # Load sales transactions
  load_transactions = load_sales_transactions_op(
      project_id=project_id,
      source_gcs_path=source_gcs_path,
      source_bq_table=source_bq_table,
      dataset_location=dataset_location,
      dataset_name=bq_dataset_name,
      table_id=transactions_table_name)

  # Generate the feature engineering query
  prepare_query = prepare_feature_engineering_query_op(
      project_id=project_id,
      source_table_id=load_transactions.output,
      destination_dataset=bq_dataset_name,
      features_table_name=features_table_name,
      threshold_date=threshold_date,
      predict_end=predict_end,
      max_monetary=max_monetary,
      query_template_uri=query_template_uri)

  # Run the feature engineering query on BigQuery.
  engineer_features = engineer_features_op(
      query=prepare_query.outputs['query'],
      project_id=project_id,
      dataset_id=prepare_query.outputs['dataset_name'],
      table_id=prepare_query.outputs['table_name'],
      output_gcs_path='',
      dataset_location=dataset_location,
      job_config='')

  # Run the batch predict task on features in Big Query
  source_data_uri = 'bq://{}.{}.{}'.format(
      project_id, prepare_query.outputs['dataset_name'],
      prepare_query.outputs['table_name'])

  predict_batch = batch_predict_op(
      project_id=project_id,
      region=aml_compute_region,
      model_id=aml_model_id,
      datasource=source_data_uri,
      destination_prefix=destination_prefix)

  predict_batch.after(engineer_features)

  # Configure the pipeline to use a service account secret
  if USE_SA_SECRET:
    steps = [load_transactions, prepare_query, engineer_features, predict_batch]
    for step in steps:
      step.apply(gcp.use_gcp_secret('user-gcp-sa'))