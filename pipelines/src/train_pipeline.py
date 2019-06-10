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
"""CLV training and deployment pipeline."""

from helper_components import (load_sales_transactions,
                               prepare_feature_engineering_query)

import yaml
import pathlib 

import kfp
from kfp import gcp


# Load pipeline settings
SETTINGS_FILE = 'settings.yaml'
settings = yaml.safe_load(pathlib.Path('settings.yaml').read_text())
component_store_settings = settings['component_store']
argument_defaults = settings['argument_defaults']
compile_settings = settings['compile_settings']

# Initialize component store
component_store = kfp.components.ComponentStore(component_store_settings['local_search_paths'],
                                                component_store_settings['url_search_prefixes'])

# Create component factories
load_sales_transactions_op = kfp.components.func_to_container_op(
    load_sales_transactions)
prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
    prepare_feature_engineering_query)
engineer_features_op = component_store.load_component('bigquery/query')
import_dataset_op = component_store.load_component('aml-import-dataset')
train_model_op = component_store.load_component('aml-train-model')
deploy_model_op = component_store.load_component('aml-deploy-model')
log_metrics_op = component_store.load_component('aml-log-metrics')


# Pipeline definition
@kfp.dsl.pipeline(
    name='CLV Training BigQuery AutoML',
    description='CLV Training Pipeline using BigQuery for feature engineering and Automl Tables for model training'
)
def clv_train(
    project_id,
    source_gcs_path,
    source_bq_table,
    bq_dataset_name,
    threshold_date,
    predict_end,
    max_monetary,
    features_table_name=argument_defaults['transactions_table_name'],
    transactions_table_name=argument_defaults['transactions_table_name'],
    dataset_location=argument_defaults['dataset_location'],
    aml_dataset_name=argument_defaults['aml_dataset_name'],
    aml_model_name=argument_defaults['aml_model_name'],
    aml_compute_region=argument_defaults['aml_compute_region'],
    train_budget=argument_defaults['train_budget'],
    target_column_name=argument_defaults['target_column_name'],
    features_to_exclude=argument_defaults['features_to_exclude'],
    optimization_objective=argument_defaults['optimization_objective'],
    primary_metric=argument_defaults['primary_metric'],
    deployment_threshold=argument_defaults['deployment_threshold'],
    skip_deployment=argument_defaults['skip_deployment'],
    query_template_uri=argument_defaults['query_template_uri']
):
  """Trains and optionally deploys a CLV Model."""

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

  source_data_uri = 'bq://{}.{}.{}'.format(
      project_id, prepare_query.outputs['dataset_name'],
      prepare_query.outputs['table_name'])

  # Import BQ table with features into AML dataset
  import_dataset = import_dataset_op(
      project_id=project_id,
      region=aml_compute_region,
      dataset_name=aml_dataset_name,
      description='',
      source_data_uri=source_data_uri,
      target_column_name=target_column_name,
      weight_column_name='',
      ml_use_column_name='')
  import_dataset.after(engineer_features)

  # Train the model
  train_model = train_model_op(
      project_id=project_id,
      region=aml_compute_region,
      dataset_id=import_dataset.outputs['output_dataset_id'],
      model_name=aml_model_name,
      train_budget=train_budget,
      optimization_objective=optimization_objective,
      primary_metric=primary_metric,
      target_name=target_column_name,
      features_to_exclude=features_to_exclude)

  # Log evaluation metrics
  log_metrics = log_metrics_op(
      model_full_id=train_model.outputs['output_model_full_id'])

  # Deploy the model if configured and the primary metric below the threshold
  with kfp.dsl.Condition(skip_deployment != True):
    with kfp.dsl.Condition(train_model.outputs['output_primary_metric_value'] <
                           deployment_threshold):
      deploy_model = deploy_model_op(
          train_model.outputs['output_model_full_id'])

  # Configure the pipeline to use a service account secret
  if compile_settings['use_sa_secret']:
    steps = [
        load_transactions, prepare_query, engineer_features, import_dataset,
        train_model, log_metrics, deploy_model
    ]
    for step in steps:
      step.apply(gcp.use_gcp_secret('user-gcp-sa'))
