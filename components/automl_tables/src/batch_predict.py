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

"""Run Automl Tables Batch Predict"""

import argparse
import logging
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def batch_predict(project_id, region, model_name):
  """Runs inference on a batch of sales transactions"""

  client = automl.AutoMlClient()
  location_path = client.location_path(project_id, location)

  # Create a dataset
  dataset_ref = client.create_dataset(
      location_path, {
          'display_name': dataset_name,
          'description': description,
          'tables_dataset_metadata': {}
      })
  dataset_id = dataset_ref.name.split('/')[-1]

  # Import data
  if source_data_uri.startswith('bq'):
    input_config = {'bigquery_source': {'input_uri': source_data_uri}}
  else:
    input_uris = source_data_uri.split(',')
    input_config = {'gcs_source': {'input_uris': input_uris}}

  response = client.import_data(dataset_ref.name, input_config)
  # Wait for import to complete
  response.result()

  if target_column_name or weight_column_name or ml_use_column_name:
    # Map column display names to column spec ID
    dataset_ref = client.get_dataset(dataset_ref.name)
    primary_table_path = client.table_spec_path(
        project_id, location, dataset_id,
        dataset_ref.tables_dataset_metadata.primary_table_spec_id)
    column_specs = client.list_column_specs(primary_table_path)
    column_specs_dict = {spec.display_name: spec.name for spec in column_specs}

    # Set the dataset's metadata
    tables_dataset_metadata = {}
    if target_column_name:
      target_column_id = column_specs_dict[target_column_name].split('/')[-1]
      tables_dataset_metadata.update(
          {'target_column_spec_id': target_column_id})
    if weight_column_name:
      weight_column_id = column_specs_dict[weight_column_name].split('/')[-1]
      tables_dataset_metadata.update(
          {'weight_column_spec_id': weight_column_id})
    if ml_use_column_name:
      ml_use_column_id = column_specs_dict[ml_use_column_name].split('/')[-1]
      tables_dataset_metadata.update(
          {'ml_use_column_spec_id': ml_use_column_id})
    update_dataset_dict = {
        'name': dataset_ref.name,
        'tables_dataset_metadata': tables_dataset_metadata
    }
    client.update_dataset(update_dataset_dict)

  return dataset_id


def main():
  args = _parse_arguments()

  # Import dataset to AutoML tables
  logging.info('Starting import from: {}'.format(args.source_data_uri))
  dataset_id = import_dataset(
      project_id=args.project_id,
      location=args.location,
      dataset_name=args.dataset_name,
      description=args.description,
      source_data_uri=args.source_data_uri,
      target_column_name=args.target_column_name,
      weight_column_name=args.weight_column_name,
      ml_use_column_name=args.ml_use_column_name)
  logging.info('Import completed. AutoML dataset{}'.format(dataset_id))

  # Save project ID, dataset ID, and dataset location to output
  Path(args.output_project_id).parent.mkdir(parents=True, exist_ok=True)
  Path(args.output_project_id).write_text(args.project_id)
  Path(args.output_dataset_id).parent.mkdir(parents=True, exist_ok=True)
  Path(args.output_dataset_id).write_text(dataset_id)
  Path(args.output_location).parent.mkdir(parents=True, exist_ok=True)
  Path(args.output_location).write_text(args.location)


def _parse_arguments():
  """Parse command line arguments"""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--project-id',
      type=str,
      required=True,
      help='The GCP project to run processing.')
  parser.add_argument(
      '--location',
      type=str,
      required=True,
      help='A region for the AutoML Tables dataset')
  parser.add_argument(
      '--dataset-name', type=str, required=True, help='AutoML dataset name.')
  parser.add_argument('--description', type=str, help='AutoML dataset name.')
  parser.add_argument(
      '--source-data-uri',
      type=str,
      required=True,
      help='Source data URI. BigQuery or GCS')
  parser.add_argument(
      '--target-column-name',
      type=str,
      required=True,
      help='Target column name')
  parser.add_argument(
      '--weight-column-name',
      type=str,
      required=True,
      help='Wieght column name')
  parser.add_argument(
      '--ml-use-column-name',
      type=str,
      required=True,
      help='ML use columns name')
  parser.add_argument(
      '--output-project-id',
      type=str,
      required=True,
      help='The file to write the ID of the AutoML project. Provided by KFP.')
  parser.add_argument(
      '--output-dataset-id',
      type=str,
      required=True,
      help='The file to write the ID of the AutoML dataset. Provided by KFP.')
  parser.add_argument(
      '--output-location',
      type=str,
      required=True,
      help='The file to write the location the AutoML dataset. Provided by KFP.'
  )

  return parser.parse_args()


if __name__ == '__main__':
  #logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
  logging.basicConfig(level=logging.INFO)
  main()
