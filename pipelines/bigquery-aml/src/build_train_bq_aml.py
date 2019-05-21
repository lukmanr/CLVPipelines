
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
import os
import argparse


BASE_IMAGE = 'gcr.io/clv-pipelines/base-image:latest'
@kfp.dsl.python_component(name='Prepare query', base_image=BASE_IMAGE)
def prepare_feature_engineering_query(
    project_id: str,
    source_table_id: str,
    threshold_date: str,
    predict_end: str,
    max_monetary: str,
    query_template_uri: str) -> str:
    """Generates a feature engineering query.
    
    This a lightweight Python KFP component that generates a query
    that processes an input BQ table with sales transactions into features
    that will be used for CLV model training. The component replaces placeholders
    in a query template with values passed as parameters.
    """

    from google.cloud import storage
    import re
    
    # Read a query template from GCS
    _, bucket, blob_name = re.split("gs://|/", query_template_uri, 2)
    blob = storage.Client(project_id).get_bucket(bucket).blob(blob_name)
    query_template = blob.download_as_string().decode('utf-8')

    # Substitute placeholders in the query template
    query = query_template.format(
        data_source_id=source_table_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary
    )
    
    return query


# Set the URIs to the specifications of the components used in the pipeline
BIGQUERY_COMPONENT_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/bigquery/query/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'gs://clv-pipelines-scripts/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'gs://clv-pipelines-scripts/aml-train-model.yaml'
# Set the URI to the location of the feature engineering query template
QUERY_TEMPLATE_URI = 'gs://clv-pipelines-scripts/create_features_template.sql'

@kfp.dsl.pipeline(
    name='CLV Training Pipeline - BigQuery',
    description='CLV Training Pipeline using BigQuery for feature engineering and Automl Tables for model training'
)
def clv_train_pipeline_bq_automl(
    project_id='', 
    source_table_id='',
    features_dataset_id='', 
    features_table_id='',
    features_dataset_location='US',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    compute_region='us-central1',
    automl_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id'
):
    # Create component factories
    prepare_feature_engineering_query_op = kfp.components.func_to_container_op(prepare_feature_engineering_query)
    engineer_features_op = kfp.components.load_component_from_url(BIGQUERY_COMPONENT_SPEC_URI)
    import_dataset_op = kfp.components.load_component_from_url(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component_from_url(AML_TRAIN_MODEL_SPEC_URI)

    # Define the pipeline's tasks
    prepare_feature_engineering_query_task = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=source_table_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=QUERY_TEMPLATE_URI
    )

    engineer_features_task = engineer_features_op(
        query=prepare_feature_engineering_query_task.output,
        project_id=project_id,
        dataset_id=features_dataset_id,
        table_id=features_table_id,
        output_gcs_path='',
        dataset_location=features_dataset_location,
        job_config=''
    )

    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=compute_region,
        dataset_name=automl_dataset_name,
        description='',
        source_data_uri='bq://{}.{}.{}'.format(project_id, features_dataset_id, features_table_id),
        target_column_name=target_column_name,
        weight_column_name='',
        ml_use_column_name=''       
    )
    import_dataset_task.after(engineer_features_task)

    train_model_task = train_model_op(
        project_id=project_id,
        location=compute_region,
        dataset_id=import_dataset_task.outputs['output_dataset_id'],
        model_name=model_name,
        train_budget=train_budget,
        optimization_objective='MINIMIZE_MAE',
        target_name=target_column_name,
        features_to_exclude=features_to_exclude
        )
    

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--out-folder',
        type=str,
        required=True,
        help='The output folder for a compiled pipeline')
    
    return parser.parse_args()
        

if __name__ == '__main__':
    args = _parse_arguments()
    # Compile the pipeline
    pipeline_func = clv_train_pipeline_bq_automl
    pipeline_filename = pipeline_func.__name__ + '.tar.gz'
    pipeline_path = os.path.join(args.out_folder, pipeline_filename)

    kfp.compiler.Compiler().compile(pipeline_func, pipeline_path) 

    
