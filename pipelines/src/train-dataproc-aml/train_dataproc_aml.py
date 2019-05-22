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

# Set the URIs to the specifications of the components used in the pipeline
CREATE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/create_cluster/component.yaml'
DELETE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/delete_cluster/component.yaml' 
SUBMIT_PYSPARK_JOB_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/submit_pyspark_job/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'gs://clv-pipelines/specs/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'gs://clv-pipelines/specs/aml-train-model.yaml'
# Set the URI to the location of the feature engineering PySpark script
CREATE_FEATURES_FILE_URI = 'gs://clv-pipelines/scripts/create_features.py'


@kfp.dsl.pipeline(
    name='CLV Training Pipeline - Dataproc',
    description='CLV Training Pipeline using Dataproc/Spark for feature engineering and AutoML Tables for model training'
)
def clv_train_pipeline_dataproc_automl(
    project_id='', 
    source_gcs_path='',
    output_gcs_path='',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    max_partitions=2,
    compute_region='us-central1',
    automl_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id'
):
    # Create component factories
    dataproc_create_cluster_op = kfp.components.load_component_from_url(CREATE_DATAPROC_SPEC_URI)    
    dataproc_delete_cluster_op = kfp.components.load_component_from_url(DELETE_DATAPROC_SPEC_URI)    
    dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(SUBMIT_PYSPARK_JOB_SPEC_URI)    
    import_dataset_op = kfp.components.load_component_from_url(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component_from_url(AML_TRAIN_MODEL_SPEC_URI)

    # Define workflow

    # Create a Dataproc cluster
    dataproc_create_cluster_task = dataproc_create_cluster_op(
        project_id=project_id,
        region=compute_region,
        name='',
        name_prefix='',
        initialization_actions='',
        config_bucket='',
        image_version='',
        cluster='',
        wait_interval='30'
    ) 

    # Run the feature engineering PySpark script.
    pyspark_script_args = ('['
        '"--source-gcs-path={}",'
        '"--output-gcs-path={}",'
        '"--threshold-date={}",'
        '"--predict-end={}",'
        '"--max-monetary={}",'
        '"--max-partitions={}",'
        ']'
    ).format(
        source_gcs_path, 
        output_gcs_path,
        threshold_date,
        predict_end,
        max_monetary,
        max_partitions)

    dataproc_submit_pyspark_job_task = dataproc_submit_pyspark_job_op(
        project_id=project_id,
        region=compute_region,
        cluster_name=dataproc_create_cluster_task.output,
        main_python_file_uri = CREATE_FEATURES_FILE_URI,
        args=pyspark_script_args,
        pyspark_job='{}',
        job='{}',
        wait_interval='30'
    )

    # Delete the Dataproce cluster
    dataproc_delete_cluster_task = dataproc_delete_cluster_op(
        project_id=project_id,
        region=compute_region,
        name=dataproc_create_cluster_task.output
    )
    dataproc_delete_cluster_task.after(dataproc_submit_pyspark_job_task)

    """
    # Import CSV files with features into AML dataset 
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=compute_region,
        dataset_name=automl_dataset_name,
        source_data_uri='bq://{}.{}.{}'.format(project_id, features_dataset_id, features_table_id)
    )
    """
