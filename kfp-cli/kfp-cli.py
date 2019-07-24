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
"""Command line wrapper around kfp.Client()."""

import fire
import kfp


#def run(host, experiment, run_name, pipeline_file, arguments):
#  """Submits a KFP pipeline for execution."""
#
#  client = kfp.Client(host)
#
#  experiment_ref = client.create_experiment(experiment)
#
#  run = client.run_pipeline(experiment_ref.id, run_name, pipeline_file,
#                            arguments)
#  print("Run submitted:")
#  print("    Run ID: {}".format(run.id))
#  print("    Experiment: {}".format(experiment))
#  print("    Pipeline: {}".format(pipeline_file))
#  print("    Arguments:")
#  for name, value in arguments.items():
#    print("      {}:  {}".format(name, value))
#  print("Waiting for completion ...")
#
#  # Wait for completion
#  result = client.wait_for_run_completion(run.id, timeout=6000)

class KFPClient(object):
  """ CLI wrapper around kfp.Client() API """

  def __init__(self, host):
    """Create a new instance of KFPClient

    Args:
      host: the host to talk to Kubeflow Pipelines
    """

    self._client = kfp.Client(host)

  def run_pipeline(self, experiment_name, run_name, pipeline_file, params={}):
    print("run_pipeline_from_package")

  def run_pipeline(self, experiment_name, run_name, pipeline_id, params={}):
    print("run_pipeline_from_id")

  def create_experiment(self, name):
    self._client.create_experiment(name)

    

if __name__ == "__main__":
  fire.Fire(KFPClient)
