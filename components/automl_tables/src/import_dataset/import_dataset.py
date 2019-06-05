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

"""This module wraps AutoML Tables dataset import API"""

import argparse
import logging
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def import_dataset(project_id, region, dataset_name, description,
                   source_data_uri, target_column_name, weight_column_name,
                   ml_use_column_name, output_project_id, output_dataset_id,
                   output_location):
  """Imports BQ table or GCS files into an AutoML dataset"""

  logging.basicConfig(level=logging.INFO)

  client = automl.AutoMlClient()
  location_path = client.location_path(project_id, region)

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

  logging.info('Starting import from: {}'.format(source_data_uri))
  response = client.import_data(dataset_ref.name, input_config)
  response.result() #Wait for completion
  logging.info('Import completed')

  # Update column specs
  if target_column_name or weight_column_name or ml_use_column_name:
    # Map column display names to column spec ID
    dataset_ref = client.get_dataset(dataset_ref.name)
    primary_table_path = client.table_spec_path(
        project_id, region, dataset_id,
        dataset_ref.tables_dataset_metadata.primary_table_spec_id)
    column_specs = client.list_column_specs(primary_table_path)
    column_specs_dict = {spec.display_name: spec.name for spec in column_specs}

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
    logging.info('Column specs updated')

  # Save project ID, dataset ID, and dataset location to output
  Path(output_project_id).parent.mkdir(parents=True, exist_ok=True)
  Path(output_project_id).write_text(project_id)
  Path(output_dataset_id).parent.mkdir(parents=True, exist_ok=True)
  Path(output_dataset_id).write_text(dataset_id)
  Path(output_location).parent.mkdir(parents=True, exist_ok=True)
  Path(output_location).write_text(region)




