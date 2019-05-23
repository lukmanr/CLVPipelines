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


# URIs to the specifications of the components used in the pipeline
BIGQUERY_COMPONENT_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/bigquery/query/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'aml-train-model.yaml'
AML_RETRIEVE_METRICS_SPEC_URI = 'aml-retrieve-regression-metrics.yaml'
AML_DEPLOY_MODEL_SPEC_URI = 'aml-deploy-model.yaml'


# Helper Lightweight Python components
BASE_IMAGE = 'gcr.io/clv-pipelines/base-image:latest'

@kfp.dsl.python_component(name='Load transactions', base_image=BASE_IMAGE)
def load_sales_transactions(
    project_id: str,
    source_gcs_path: str,
    location: str,
    dataset_id: str,
    table_id: str) -> str:
    """Loads sales transactions from a CSV file on GCS to a BigQuery table"""

    from google.cloud import bigquery
    import uuid
    import logging

    client = bigquery.Client(project=project_id)

    # Create or get a dataset reference
    dataset = bigquery.Dataset("{}.{}".format(project_id, dataset_id))
    dataset.location = location
    dataset_ref = client.create_dataset(dataset, exists_ok=True) 

    # Configure Load job settings
    job_config = bigquery.LoadJobConfig()
    job_config.schema = [
        bigquery.SchemaField("customer_id", "STRING"),
        bigquery.SchemaField("order_date", "DATE"),
        bigquery.SchemaField("quantity", "INTEGER"),
        bigquery.SchemaField("unit_price", "FLOAT")
    ]
    job_config.source_format = bigquery.SourceFormat.CSV
    job_config.create_disposition = bigquery.job.CreateDisposition.CREATE_IF_NEEDED
    job_config.write_disposition = bigquery.job.WriteDisposition.WRITE_TRUNCATE
    job_config.skip_leading_rows = 1

    # Start the load job
    load_job = client.load_table_from_uri(
        source_gcs_path,
        dataset_ref.table(table_id),
        job_config=job_config
    )  

    # Wait for table load to complete
    load_job.result()

    return "{}.{}.{}".format(project_id, dataset_id, table_id)


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


# Pipeline definition
@kfp.dsl.pipeline(
    name='CLV Training BigQuery AutoML',
    description='CLV Training Pipeline using BigQuery for feature engineering and Automl Tables for model training'
)
def clv_train_bq_automl(
    project_id, 
    source_gcs_path,
    bq_location='US',
    transactions_dataset_id='clv_dataset',
    transactions_table_id='transactions',
    threshold_date='2011-08-08',
    predict_end='2011-12-12',
    features_dataset_id='clv_dataset',
    features_table_id='features',
    max_monetary=15000,
    compute_region='us-central1',
    dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id',
    mae_threshold='700'
):
    # Create component factories
    load_sales_transactions_op = kfp.components.func_to_container_op(load_sales_transactions)
    prepare_feature_engineering_query_op = kfp.components.func_to_container_op(prepare_feature_engineering_query)
    engineer_features_op = kfp.components.load_component_from_url(BIGQUERY_COMPONENT_SPEC_URI)
    import_dataset_op = kfp.components.load_component_from_file(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component_from_file(AML_TRAIN_MODEL_SPEC_URI)
    retrieve_metrics_op = kfp.components.load_component_from_file(AML_RETRIEVE_METRICS_SPEC_URI)
    deploy_model_op = kfp.components.load_component_from_file(AML_DEPLOY_MODEL_SPEC_URI)

    # Define workflow

    # Load sales transactions from GCS to Big Query
    load_sales_transactions_task = load_sales_transactions_op(
        project_id=project_id,
        source_gcs_path=source_gcs_path,
        location=bq_location,
        dataset_id=transactions_dataset_id,
        table_id=transactions_table_id 
    ) 

    # Generate the feature engineering query
    QUERY_TEMPLATE_URI = 'gs://clv-pipelines/scripts/create_features_template.sql'
    prepare_feature_engineering_query_task = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=load_sales_transactions_task.output,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=QUERY_TEMPLATE_URI
    )

    # Run the feature engineering query on BigQuery.
    engineer_features_task = engineer_features_op(
        query=prepare_feature_engineering_query_task.output,
        project_id=project_id,
        dataset_id=features_dataset_id,
        table_id=features_table_id,
        output_gcs_path='',
        dataset_location=bq_location,
        job_config=''
    )
     
    # Import BQ table with features into AML dataset
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=compute_region,
        dataset_name=dataset_name,
        description='',
        source_data_uri='bq://{}.{}.{}'.format(project_id, features_dataset_id, features_table_id),
        target_column_name=target_column_name,
        weight_column_name='',
        ml_use_column_name=''       
    )
    import_dataset_task.after(engineer_features_task)

    # Train the model
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

    # Retrieve regression metrics for the model 
    retrieve_metrics_task = retrieve_metrics_op(
       model_full_id=train_model_task.output) 

    # If MAE is above the threshold deploy the model
    with dsl.Condition(retrieve_metrics_task.outputs['output_mae'] > mae_threshold):
        deploy_model_tast = deploy_model_op(train_model_task.output)
