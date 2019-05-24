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
import kfp.dsl as dsl
import os
import argparse


# URIs to the specifications of the components used in the pipeline
CREATE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/create_cluster/component.yaml'
DELETE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/delete_cluster/component.yaml' 
SUBMIT_PYSPARK_JOB_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/submit_pyspark_job/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'aml-train-model.yaml'
AML_DEPLOY_MODEL_SPEC_URI = 'aml-deploy-model.yaml'
AML_RETRIEVE_METRICS_SPEC_URI = 'aml-retrieve-regression-metrics.yaml'


# Helper Lightweight Python components
BASE_IMAGE = 'gcr.io/clv-pipelines/base-image:latest'

@kfp.dsl.python_component(name='List GCS files ', base_image=BASE_IMAGE)
def list_gcs_files(source_gcs_folder: str) -> str:
    """Returns a list of full GCS paths

    This is a helper component designed to bridge an output of a Dataproc/Spark
    processing to an input of AutoML Import Dataset. The component takes as an 
    input a path of to a GCS folder returns a comma-delimited list of full GCS 
    paths - as required by AutoML Import Dataset.""" 

    import re
    from google.cloud import storage

    storage_client = storage.Client()

    _, bucket_name, prefix = re.split("gs://|/", source_gcs_folder, 2)
    prefix = prefix + '/' if prefix[-1] != '/' else prefix
    bucket = storage_client.get_bucket(bucket_name)
    blobs = ['gs://{}/{}'.format(bucket_name, blob.name) 
        for blob in bucket.list_blobs(prefix=prefix, delimiter='') 
        if (blob.name != prefix) and not (blob.name.endswith('_SUCCESS'))]

    return ','.join(blobs) 


# Pipeline definition
@kfp.dsl.pipeline(
    name='CLV Training Pipeline - Dataproc',
    description='CLV Training Pipeline using Dataproc/Spark for feature engineering and AutoML Tables for model training'
)
def clv_train_pipeline_dataproc_automl(
    project_id, 
    source_gcs_path,
    output_gcs_path,
    threshold_date='2011-08-08',
    predict_end='2011-12-12',
    max_monetary=15000,
    max_partitions=2,
    compute_region='us-central1',
    aml_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id',
    mae_threshold='990',
    cluster_name='clv-spark-cluster'
):
    # Create component factories
    list_gcs_files_op = kfp.components.func_to_container_op(list_gcs_files)
    dataproc_create_cluster_op = kfp.components.load_component_from_url(CREATE_DATAPROC_SPEC_URI)    
    dataproc_delete_cluster_op = kfp.components.load_component_from_url(DELETE_DATAPROC_SPEC_URI)    
    dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(SUBMIT_PYSPARK_JOB_SPEC_URI)    
    import_dataset_op = kfp.components.load_component_from_file(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component_from_file(AML_TRAIN_MODEL_SPEC_URI)
    retrieve_metrics_op = kfp.components.load_component_from_file(AML_RETRIEVE_METRICS_SPEC_URI)
    deploy_model_op = kfp.components.load_component_from_file(AML_DEPLOY_MODEL_SPEC_URI)

    # Delete a Dataproc cluster - this is an exit handler
    delete_cluster_exit_handler = dataproc_delete_cluster_op(
        project_id=project_id,
        region=compute_region,
        name=cluster_name
    )
    delete_cluster_exit_handler.is_exit_handler = True
 
    with dsl.ExitHandler(delete_cluster_exit_handler):
        # Create a Dataproc cluster
        create_cluster_task = dataproc_create_cluster_op(
            project_id=project_id,
            region=compute_region,
            name=cluster_name,
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

        CREATE_FEATURES_SCRIPT_URI = 'gs://clv-pipelines/scripts/create_features.py'

        submit_pyspark_job_task = dataproc_submit_pyspark_job_op(
            project_id=project_id,
            region=compute_region,
            cluster_name=create_cluster_task.output,
            main_python_file_uri = CREATE_FEATURES_SCRIPT_URI,
            args=pyspark_script_args,
            pyspark_job='{}',
            job='{}',
            wait_interval='30'
        )

        delete_cluster_task = dataproc_delete_cluster_op(
            project_id=project_id,
            region=compute_region,
            name=cluster_name
        )
        delete_cluster_task.after(submit_pyspark_job_task)

        # Create a list of full gcs filenames from the dataproc output folder
        list_gcs_files_task = list_gcs_files_op(output_gcs_path)
        list_gcs_files_task.after(submit_pyspark_job_task)

        # Import files with features into AML dataset
        import_dataset_task = import_dataset_op(
            project_id=project_id,
            location=compute_region,
            dataset_name=aml_dataset_name,
            description='',
            source_data_uri=list_gcs_files_task.output,
            target_column_name=target_column_name,
            weight_column_name='',
            ml_use_column_name=''       
        )

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
        with dsl.Condition(retrieve_metrics_task.outputs['output_mae'] < mae_threshold):
            deploy_model_tast = deploy_model_op(train_model_task.output)