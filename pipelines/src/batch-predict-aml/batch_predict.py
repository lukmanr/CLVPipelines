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
AML_BATCH_PREDICT_URI = 'aml-batch-predict.yaml'


@kfp.dsl.pipeline(
    name='CLV Batch Predict AutoML',
    description='CLV predictions using Dataproc for feature engineering and BQ as a final destination'
)
def clv_batch_predict(
    project_id, 
    region='us-central1',
    model_id='TBL403503175207747584',
    datasource='gs://clv-testing/transactions/transactions.csv',
    destination='bq://sandbox-235500'
):
  # Create component factories
  list_gcs_files_op = kfp.components.func_to_container_op(list_gcs_files)
  dataproc_create_cluster_op = kfp.components.load_component_from_url(CREATE_DATAPROC_SPEC_URI)    
  dataproc_delete_cluster_op = kfp.components.load_component_from_url(DELETE_DATAPROC_SPEC_URI)    
  dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(SUBMIT_PYSPARK_JOB_SPEC_URI)    
  batch_predict_op = kfp.components.load_component_from_file(AML_BATCH_PREDICT_SPEC_URI)

  # Define workflow

    