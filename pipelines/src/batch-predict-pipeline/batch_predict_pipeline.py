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


@kfp.dsl.pipeline(
    name='CLV Batch Predict AutoML',
    description='CLV predictions using Dataproc for feature engineering and BQ as a final destination'
)
def clv_batch_predict(
    project_id,
    model_id,
    datasource,
    bq_destination,
    dataproc_gcs_output,
    pyspark_script_path,
    region='us-central1',
    threshold_date='2011-08-08',
    predict_end='2011-12-12',
    max_monetary=15000,
    max_partitions=8,
    cluster_name='clv-spark-cluster'):

  # Create component factories
  dataproc_create_cluster_op = kfp.components.load_component_from_url(
      CREATE_DATAPROC_SPEC_URI)
  dataproc_delete_cluster_op = kfp.components.load_component_from_url(
      DELETE_DATAPROC_SPEC_URI)
  dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(
      SUBMIT_PYSPARK_JOB_SPEC_URI)
  batch_predict_op = kfp.components.load_component_from_file(
      AML_BATCH_PREDICT_SPEC_URI)

  # Define workflow
  # Delete a Dataproc cluster - this is an exit handler
  delete_cluster_exit_handler = dataproc_delete_cluster_op(
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
                           ']').format(datasource, dataproc_gcs_output,
                                       threshold_date, predict_end, 
                                       max_monetary, max_partitions)

    CREATE_FEATURES_SCRIPT_URI = 'gs://clv-pipelines/scripts/create_features.py'

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
