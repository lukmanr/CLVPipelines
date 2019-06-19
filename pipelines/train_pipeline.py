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

from helper_components import load_sales_transactions
from helper_components import prepare_feature_engineering_query

import kfp
from kfp import gcp

import pathlib
import yaml

# Load pipeline settings
compiler_settings = yaml.safe_load(
    pathlib.Path('settings.yaml').read_text())['compiler_settings']
argument_defaults = yaml.safe_load(
    pathlib.Path('settings.yaml').read_text())['argument_defaults']

# Initialize component store
component_store = kfp.components.ComponentStore(
    compiler_settings['local_search_paths'],
    compiler_settings['url_search_prefixes'])

# Create component factories
load_sales_transactions_op = kfp.components.func_to_container_op(
    load_sales_transactions,
    base_image=compiler_settings['lightweight_components_base_image'])
prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
    prepare_feature_engineering_query,
    base_image=compiler_settings['lightweight_components_base_image'])
engineer_features_op = component_store.load_component('bigquery/query')
import_dataset_op = component_store.load_component('aml-import-dataset')
train_model_op = component_store.load_component('aml-train-model')
deploy_model_op = component_store.load_component('aml-deploy-model')
log_metrics_op = component_store.load_component('aml-log-metrics')


# Pipeline definition
@kfp.dsl.pipeline(
    name='CLV Training',
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
    features_table_name=argument_defaults['features_table_name'],
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
    query_template_uri=argument_defaults['query_template_uri']):
  """Trains and optionally deploys a CLV Model."""


  


  train_model = train_model_op(
      project_id=project_id,
      region=aml_compute_region,
      dataset_id="model_id",
      model_name=aml_model_name,
      train_budget=train_budget,
      optimization_objective=optimization_objective,
      target_name=target_column_name,
      features_to_exclude=features_to_exclude)

  # Log evaluation metrics
  log_metrics = log_metrics_op(
      model_full_id=train_model.outputs['output_model_full_id'],
      primary_metric=primary_metric)

  
  if compiler_settings['use_sa_secret']:
    steps = [
        train_model, log_metrics
    ]
    for step in steps:
      step.apply(gcp.use_gcp_secret('user-gcp-sa'))
 
