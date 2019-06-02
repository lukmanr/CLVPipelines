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
CREATE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/create_cluster/component.yaml'
DELETE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/delete_cluster/component.yaml'
SUBMIT_PYSPARK_JOB_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/submit_pyspark_job/component.yaml'
AML_BATCH_PREDICT_SPEC_URI = 'aml-batch-predict.yaml'

# Helper Lightweight Python components
BASE_IMAGE = 'gcr.io/clv-pipelines/base-image:latest'


@kfp.dsl.python_component(name='List GCS files ', base_image=BASE_IMAGE)
def list_gcs_files(source_gcs_folder: str) -> str:
  """Returns a list of full GCS paths
  This is a helper component designed to bridge an output of a Dataproc/Spark
  processing to an input of AutoML Import Dataset. The component takes as an
  input a path of to a GCS folder returns a comma-delimited list of full GCS
  paths - as required by AutoML Import Dataset.
  """

  import re
  from google.cloud import storage

  storage_client = storage.Client()

  _, bucket_name, prefix = re.split('gs://|/', source_gcs_folder, 2)
  prefix = prefix + '/' if prefix[-1] != '/' else prefix
  bucket = storage_client.get_bucket(bucket_name)
  blobs = [
      'gs://{}/{}'.format(bucket_name, blob.name)
      for blob in bucket.list_blobs(prefix=prefix, delimiter='')
      if (blob.name != prefix) and not (blob.name.endswith('_SUCCESS'))
  ]

  return ','.join(blobs)


# WORKAROUND
# Since kfp.components.load_component does not currently support exit handlers
# we explicitly define an exit handler op on dataproc delete cluster component
def dataproc_delete_cluster_exit_handler_op(project_id, region, name):
  return dsl.ContainerOp(
      name='Delete cluster exit handler',
      image='gcr.io/ml-pipeline/ml-pipeline-gcp:3b949b37aa2cefd3180398d59116f43ce965a2a6',
      arguments=[
          'kfp_component.google.dataproc', 'delete_cluster', '--project_id',
          project_id, '--region', region, '--name', name, '--wait_interval', 30
      ],
      is_exit_handler=True)


@kfp.dsl.pipeline(
    name='CLV Batch Predict AutoML',
    description='CLV predictions using Dataproc for feature engineering and BQ as a final destination'
)
def clv_batch_predict(project_id,
                      pyspark_script_path,
                      source_gcs_path,
                      output_gcs_path,
                      model_id,
                      destination,
                      region='us-central1',
                      threshold_date='2011-08-08',
                      predict_end='2011-12-12',
                      max_monetary=15000,
                      max_partitions=8):

  # Create component factories
  list_gcs_files_op = kfp.components.func_to_container_op(list_gcs_files)
  dataproc_create_cluster_op = kfp.components.load_component_from_url(
      CREATE_DATAPROC_SPEC_URI)
  dataproc_delete_cluster_op = kfp.components.load_component_from_url(
      DELETE_DATAPROC_SPEC_URI)
  dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(
      SUBMIT_PYSPARK_JOB_SPEC_URI)
  batch_predict_op = kfp.components.load_component_from_file(
      AML_BATCH_PREDICT_SPEC_URI)

  cluster_name = 'dataproc-{{workflow.name}}'

  # Define workflow
  # Define the delete Dataproc cluster exit handler
  delete_cluster_exit_handler = dataproc_delete_cluster_exit_handler_op(
      project_id=project_id, region=region, name=cluster_name)

  with dsl.ExitHandler(exit_op=delete_cluster_exit_handler):
    # Create a Dataproc cluster
    create_cluster_task = dataproc_create_cluster_op(
        project_id=project_id,
        region=region,
        name=cluster_name,
        name_prefix='',
        initialization_actions='',
        config_bucket='',
        image_version='',
        cluster='',
        wait_interval='30')

    # Run the feature engineering PySpark script.
    pyspark_script_args = ('['
                           '"--source-gcs-path={}",'
                           '"--output-gcs-path={}",'
                           '"--threshold-date={}",'
                           '"--predict-end={}",'
                           '"--max-monetary={}",'
                           '"--max-partitions={}",'
                           ']').format(source_gcs_path, output_gcs_path,
                                       threshold_date, predict_end,
                                       max_monetary, max_partitions)

    submit_pyspark_job_task = dataproc_submit_pyspark_job_op(
        project_id=project_id,
        region=region,
        cluster_name=create_cluster_task.output,
        main_python_file_uri=pyspark_script_path,
        args=pyspark_script_args,
        pyspark_job='{}',
        job='{}',
        wait_interval='30')

    delete_cluster_task = dataproc_delete_cluster_op(
        project_id=project_id, region=region, name=cluster_name)
    delete_cluster_task.after(submit_pyspark_job_task)

    # Create a list of full gcs filenames from the dataproc output folder
    list_gcs_files_task = list_gcs_files_op(output_gcs_path)
    list_gcs_files_task.after(submit_pyspark_job_task)

    batch_predict_task = batch_predict_op(
        project_id=project_id,
        region=region,
        model_id=model_id,
        datasource=list_gcs_files_task.output,
        destination_prefix=destination)

    # Run batch predict on the output of PySpark job
    batch_predict_task.after(submit_pyspark_job_task)
