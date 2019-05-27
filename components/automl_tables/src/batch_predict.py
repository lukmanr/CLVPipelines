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
import json
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def batch_predict(client, project_id, region, model_id, datasource, destination_prefix):
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

  if destination_prefix.startswith("bq"):
    output_config = {"bigquery_destination": {"output_uri": destination_prefix}}
  else:
    output_config = {"gcs_destination": {"output_uri_prefix": destination_prefix}}

  # Run the prediction query
  response = client.batch_predict(
      model_full_id, input_config, output_config)

  # Wait for completion
  # WORKAROUND to catch exception thrown by response.result()
  try:
    response.result()
  except:
    pass

  return response.metadata
  
def prediction_metadata_to_markdown_metadata(response_metadata):
    """Converts batch predict response metadat to markdown"""

    markdown_template = (
        "**Batch predict results:**  \n"
        "&nbsp;&nbsp;&nbsp;&nbsp;**Input datasource:**&nbsp{input}  \n"
        "&nbsp;&nbsp;&nbsp;&nbsp;**Output destination:**&nbsp{output}  \n"
    )
    markdown = markdown_template.format(
        input=response_metadata.batch_predict_details.input_config,
        output=response_metadata.batch_predict_details.output_info
    )

    return markdown


def write_metadata_for_output_viewers(*argv):
    """Writes items to be rendered by KFP UI as artificats"""

    metadata = {
        "version": 1,
        "outputs": argv 
    }
    with open('/mlpipeline-ui-metadata.json', 'w') as f:
            json.dump(metadata, f)


    ### Debug code ###
    print("Debug: Wrote to /mlpipeline-ui-metadata.json")
    with open('/mlpipeline-ui-metadata.json', 'r') as f:
      print(f.read())

def _parse_arguments():
  """Parse command line arguments."""

  parser = argparse.ArgumentParser()
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
      "--destination-prefix",
      type=str,
      required=True,
      help="Destination sink for predictions")
  parser.add_argument(
      "--output-destination",
      type=str,
      required=True,
      help="Output")
  return parser.parse_args()


if __name__ == "__main__":
  logging.basicConfig(level=logging.INFO)
  args = _parse_arguments()
  client = automl.PredictionServiceClient()

  # Run scoring
  logging.info("Starting batch scoring using: {}".format(args.datasource))
  result = batch_predict(
      client,
      args.project_id,
      args.region,
      args.model_id,
      args.datasource,
      args.destination_prefix)
  logging.info("Batch scoring completed: {}".format(str(result)))
  write_metadata_for_output_viewers(prediction_metadata_to_markdown_metadata(result))

  # Save results
  if args.destination_prefix.startswith("bq"):
    output = result.batch_predict_details.output_info.bigquery_output_dataset
  else:
    output = "bbb"

  Path(args.output_destination).parent.mkdir(parents=True, exist_ok=True)
  Path(args.output_destination).write_text(output)
