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

import kfp
from kfp import dsl
import os
import argparse
import json
import uuid
import helper_components 


# URIs to the specifications of the components used in the pipeline
BIGQUERY_COMPONENT_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/bigquery/query/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'aml-train-model.yaml'
AML_RETRIEVE_METRICS_SPEC_URI = 'aml-retrieve-regression-metrics.yaml'
AML_DEPLOY_MODEL_SPEC_URI = 'aml-deploy-model.yaml'


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
    transactions_table_name,
    features_table_name,
    threshold_date,
    predict_end,
    max_monetary,
    dataset_location='US',
    aml_dataset_name='clv_features',
    aml_model_name='clv_regression',
    aml_compute_region='us-central1',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id',
    optimization_objective='MINIMIZE_MAE',
    deployment_threshold=900, 
    skip_deployment=True,
    query_template_uri='gs://clv-pipelines/scripts/create_features_template.sql'
):
    # Create component factories
    load_sales_transactions_op = kfp.components.func_to_container_op(
        helper_components.load_sales_transactions)
    prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
        helper_components.prepare_feature_engineering_query)
    engineer_features_op = component_store.load_component('bigquery/query') 
    import_dataset_op = component_store.load_component('aml-import-dataset') 
    train_model_op = component_store.load_component('aml-train-model')  
    deploy_model_op = component_store.load_component('aml-deploy-model')  
    retrieve_metrics_op = component_store.load_component('aml-retrieve-metrics')

    # Define workflow

    # Load sales transactions 
    load_sales_transactions_task = load_sales_transactions_op(
        project_id=project_id,
        source_gcs_path=source_gcs_path,
        source_bq_table=source_bq_table,
        dataset_location=dataset_location,
        dataset_name=bq_dataset_name,
        table_id=transactions_table_name 
    ) 

    # Generate the feature engineering query
    prepare_feature_engineering_query_task = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=load_sales_transactions_task.output,
        destination_dataset=bq_dataset_name,
        features_table_name=features_table_name,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=query_template_uri
    )


    # Run the feature engineering query on BigQuery.
    engineer_features_task = engineer_features_op(
        query=prepare_feature_engineering_query_task.outputs['query'],
        project_id=project_id,
        dataset_id=prepare_feature_engineering_query_task.outputs['dataset_name'],
        table_id=prepare_feature_engineering_query_task.outputs['table_name'],
        output_gcs_path='',
        dataset_location=dataset_location,
        job_config=''
    )

    source_data_uri = 'bq://{}.{}.{}'.format(
        project_id,
        prepare_feature_engineering_query_task.outputs['dataset_name'],
        prepare_feature_engineering_query_task.outputs['table_name'])

    # Import BQ table with features into AML dataset
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=aml_compute_region,
        dataset_name=aml_dataset_name,
        description='',
        source_data_uri=source_data_uri,
        target_column_name=target_column_name,
        weight_column_name='',
        ml_use_column_name=''       
    )
    import_dataset_task.after(engineer_features_task)

    # Train the model
    train_model_task = train_model_op(
        project_id=project_id,
        location=aml_compute_region,
        dataset_id=import_dataset_task.outputs['output_dataset_id'],
        model_name=aml_model_name,
        train_budget=train_budget,
        optimization_objective='MINIMIZE_MAE',
        target_name=target_column_name,
        features_to_exclude=features_to_exclude
        )

    # Retrieve regression metrics for the model 
    retrieve_metrics_task = retrieve_metrics_op(
       model_full_id=train_model_task.output) 

    # If MAE is above the threshold deploy the model
    with dsl.Condition(retrieve_metrics_task.outputs['output_mae'] < deployment_threshold):
        deploy_model_tast = deploy_model_op(train_model_task.output)



def _parse_arguments():
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--output-dir',
        type=str,
        required=True,
        help='The output folder for a compiled pipeline')
    parser.add_argument(
        '--local-search-paths',
        type=str,
        required=True,
        help='Local search path for component definitions')
    parser.add_argument(
        '--url-search-prefixes',
        type=str,
        required=True,
        help='The URL prefix to look for component definitions')
    parser.add_argument(
        '--type-check',
        type=str,
        default=False,
        help='Check types during compilation if True')
     
    return parser.parse_args()
        
platform='Local'

if __name__ == '__main__':

    args = _parse_arguments()

    local_search_paths = args.local_search_paths.split(',')
    url_search_prefixes = args.url_search_prefixes.split(',')

    component_store = kfp.components.ComponentStore(local_search_paths, url_search_prefixes)

    # Compile the pipeline
    pipeline_func = clv_train
    pipeline_filename = pipeline_func.__name__ + '.tar.gz'
    pipeline_path = os.path.join(args.output_dir, pipeline_filename)

    kfp.compiler.Compiler().compile(pipeline_func, pipeline_path, type_check=args.type_check) 


