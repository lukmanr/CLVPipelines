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

import argparse
import logging
from pathlib import Path
from google.cloud import automl_v1beta1 as automl
from google.cloud.automl_v1beta1 import enums


def deploy_model(model_full_id):
    """Deploys a trained AutoML model"""

    client = automl.AutoMlClient()

    # Check if the model is already deployed
    model = client.get_model(model_full_id)
    result = "Model already deployed"
    if model.deployment_state != enums.Model.DeploymentState.DEPLOYED:
        response = client.deploy_model(model_full_id)
        # Wait for operation to complete
        response.result()
        result = "New deployment created"

    return result
 

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-full-id',
        type=str,
        required=True,
        help='The full id of a model to deploy')
    parser.add_argument(
        '--output-deployment',
        type=str,
        required=True,
        help='AutoML model deployment status.')
 
    return parser.parse_args()

    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = _parse_arguments()

    # Import dataset to AutoML tables
    logging.info("Starting model deployment: {}".format(args.model_full_id))
    result = deploy_model( model_full_id=args.model_full_id)

    # Save project ID, dataset ID, and dataset location to output
    Path(args.output_deployment).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_deployment).write_text(result)

    """

    
    