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

import os
import kfp
import fire
import helper_components 
from kfp import gcp

# Initialize component store
component_store = kfp.components.ComponentStore()
platform = "GCP"

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
    primary_metric='mean_absolute_error',
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
    load_sales_transactions = load_sales_transactions_op(
        project_id=project_id,
        source_gcs_path=source_gcs_path,
        source_bq_table=source_bq_table,
        dataset_location=dataset_location,
        dataset_name=bq_dataset_name,
        table_id=transactions_table_name 
    ) 

    # Generate the feature engineering query
    prepare_feature_engineering_query = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=load_sales_transactions.output,
        destination_dataset=bq_dataset_name,
        features_table_name=features_table_name,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=query_template_uri
    )

    # Run the feature engineering query on BigQuery.
    engineer_features = engineer_features_op(
        query=prepare_feature_engineering_query.outputs['query'],
        project_id=project_id,
        dataset_id=prepare_feature_engineering_query.outputs['dataset_name'],
        table_id=prepare_feature_engineering_query.outputs['table_name'],
        output_gcs_path='',
        dataset_location=dataset_location,
        job_config=''
    )

    source_data_uri = 'bq://{}.{}.{}'.format(
        project_id,
        prepare_feature_engineering_query.outputs['dataset_name'],
        prepare_feature_engineering_query.outputs['table_name'])

    # Import BQ table with features into AML dataset
    import_dataset = import_dataset_op(
        project_id=project_id,
        location=aml_compute_region,
        dataset_name=aml_dataset_name,
        description='',
        source_data_uri=source_data_uri,
        target_column_name=target_column_name,
        weight_column_name='',
        ml_use_column_name=''       
    )
    import_dataset.after(engineer_features)

    # Train the model
    train_model = train_model_op(
        project_id=project_id,
        location=aml_compute_region,
        dataset_id=import_dataset.outputs['output_dataset_id'],
        model_name=aml_model_name,
        train_budget=train_budget,
        optimization_objective=optimization_objective,
        primary_metric=primary_metric,
        target_name=target_column_name,
        features_to_exclude=features_to_exclude
        )

    """
    # If MAE is above the threshold deploy the model
    with kfp.dsl.Condition(retrieve_metrics.outputs['output_mae'] < deployment_threshold):
        deploy_model = deploy_model_op(train_model.output)

   # Configure the pipeline to use GCP service account secret if running on GCP
    steps = [load_sales_transactions,
             prepare_feature_engineering_query,
             engineer_features,
             import_dataset,
             train_model,
             deploy_model]
    for step in steps:
        if platform == 'GCP':
            step.apply(gcp.use_gcp_secret('user-gcp-sa'))

    """

def _compile_pipeline(output_dir, local_search_paths, url_search_prefixes, platform='GCP', type_check=False):
    """Compile the pipeline"""

    # Set globals controlling compilation
    component_store.local_search_paths = local_search_paths 
    component_store.url_search_prefixes = url_search_prefixes
    platform=platform

    # Compile the pipeline using the name of the pipeline function as a file prefix
    pipeline_func = clv_train
    pipeline_filename = pipeline_func.__name__ + '.tar.gz'
    pipeline_path = os.path.join(output_dir, pipeline_filename)
    kfp.compiler.Compiler().compile(pipeline_func, pipeline_path, type_check=type_check) 

if __name__ == '__main__':
    fire.Fire(_compile_pipeline)
