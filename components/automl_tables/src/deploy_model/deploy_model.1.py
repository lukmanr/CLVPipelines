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
"""AutoML Tables Deploy Model API wrapper."""

import logging

from pathlib import Path
from google.cloud import automl_v1beta1 as automl
from google.cloud.automl_v1beta1 import enums


def deploy(model_full_id, output_deployment):
  """Deploys an AutoML Tables model."""

  logging.basicConfig(level=logging.INFO)
  client = automl.AutoMlClient()

  # Check if the model is already deployed
  model = client.get_model(model_full_id)
  if model.deployment_state != enums.Model.DeploymentState.DEPLOYED:
    logging.info("Starting model deployment: {}".format(model_full_id))
    response = client.deploy_model(model_full_id)
    # Wait for operation to complete
    response.result()
    logging.info("Deployment completed")
    result = "New deployment created"
  else:
    logging.info("Model already deployed")
    result = "Model already deployed"

  # Save deployment outcome to output
  Path(output_deployment).parent.mkdir(parents=True, exist_ok=True)
  Path(output_deployment).write_text(result)
