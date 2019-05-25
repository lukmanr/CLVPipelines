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

"""Run Automl Tables Batch Predict."""

import argparse
import logging
import time
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def batch_predict(client, project_id, region, model_id, datasource, output):
  """Runs batch predict on an AutoML tables model."""

  # Prepare prediction query config
  model_full_id = client.model_path(
      project_id, region, model_id
  )
  if datasource.startswith("bq"):
    input_config = {"bigquery_source": {"input_uri": datasource}}
  else:
    input_uris = datasource.split(",")
    input_config = {"gcs_source": {"input_uris": input_uris}}

  if output.startswith("bq"):
    output_config = {"bigquery_destination": {"output_uri": output}}
  else:
    output_config = {"gcs_destination": {"output_uri_prefix": output}}

  # Run the prediction query
  response = client.batch_predict(
      model_full_id, input_config, output_config)
    

  # Wait for completion

  # while response.done() is False:
  #  time.sleep(1)
  # result = response.result()

  response.result()

  return "result"


def _parse_arguments():
  """Parse command line arguments."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      "--key_file",
      type=str,
      help="SA key file")
  parser.add_argument(
      "--project-id",
      type=str,
      required=True,
      help="The GCP project to run processing.")
  parser.add_argument(
      "--region",
      type=str,
      required=True,
      help="A region for the AutoML Tables inference")
  parser.add_argument(
      "--model-id",
      type=str,
      required=True,
      help="An Automl model")
  parser.add_argument(
      "--datasource",
      type=str,
      required=True,
      help="Input datasource")
  parser.add_argument(
      "--output",
      type=str,
      required=True,
      help="Output")

  return parser.parse_args()


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  args = _parse_arguments()
  if args.key_file:
    client = automl.PredictionServiceClient.from_service_account_file(args.key_file)
  else:
    client = automl.PredictionServiceClient()

  # Run scoring
  logging.info("Starting batch scoring using: {}".format(args.datasource))
  result = batch_predict(
      client,
      args.project_id,
      args.region,
      args.model_id,
      args.datasource,
      args.output)
  logging.info("Batch scoring completed")

  # Save results
  # TBD ******
  Path(args.output).parent.mkdir(parents=True, exist_ok=True)
  Path(args.output).write_text(result)
