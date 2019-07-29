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
"""Command line wrapper around kfp.Client().

This a temporary workaround for the lack of full feature CLI for KFP.
This module will be deprecated when a standard CLI is released.
"""

import fire
import kfp
import kfp_server_api


class KFPClient(object):
  """CLI wrapper around kfp.Client() API."""

  def __init__(self, host=None):
    """Creates a new instance of KFPClient.

    Args:
      host: the host to talk to Kubeflow Pipelines.
    """

    self._client = kfp.Client(host)

  def _get_pipeline_id(self, pipeline_name):
    """Gets a pipeline ID from the pipeline's name."""
    page_token = ""
    while True:
      response = self._client.list_pipelines(page_token, page_size=10)
      pipeline_ids = [
          pipeline.id
          for pipeline in response.pipelines
          if pipeline.name == pipeline_name
      ]
      page_token = response.next_page_token
      if page_token is None or pipeline_ids:
        break

    pipeline_id = pipeline_ids[0] if pipeline_ids else None

    return pipeline_id

  def run_pipeline(self,
                   experiment_name,
                   run_name,
                   pipeline_package_path=None,
                   params={},
                   pipeline_name=None):
    """Submits a pipeline run."""
    assert pipeline_package_path or pipeline_name

    pipeline_id = None if pipeline_package_path else self._get_pipeline_id(
        pipeline_name)

    experiment_ref = None
    try:
      experiment_ref = self._client.get_experiment(
          experiment_name=experiment_name)
    except ValueError:
      experiment_ref = self._client.create_experiment(experiment_name)

    run_ref = self._client.run_pipeline(
        experiment_ref.id,
        run_name,
        pipeline_package_path=pipeline_package_path,
        params=params,
        pipeline_id=pipeline_id)

    print("Run submitted:")
    print("    Run ID: ", run_ref.id)
    print("    Run status: ", run_ref.status)

  def upload_pipeline(self, pipeline_package_path, pipeline_name):
    """Uploads a pipeline package to KFP."""
    try:
      pipeline_ref = self._client.upload_pipeline(pipeline_package_path,
                                                  pipeline_name)
      print("Pipeline ID: {}".format(pipeline_ref.id))
    except kfp_server_api.rest.ApiException:
      print("Pipeline already exists")

  def create_experiment(self, name):
    """Creates a KFP experiment."""
    self._client.create_experiment(name)


if __name__ == "__main__":
  fire.Fire(KFPClient)
