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
import argparse
import logging
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def import_dataset(
    project_id,
    location,
    dataset_name,
    source_data_uri):
    """Imports clv features into an AutoML dataset"""

    client = automl.AutoMlClient()
    location_path = client.location_path(project_id, location)

    # Create a dataset
    dataset_ref = client.create_dataset(
        location_path,
        {
            "display_name": dataset_name,
            "tables_dataset_metadata": {}})

    # Import data
    if source_data.startswith('bq'):
        input_config = {"bigquery_source": {"input_uri": source_data}}
    else:
        input_uris = source_data.path.split(",")
        input_config = {"gcs_source": {"input_uris": input_uris}}
    response = client.import_data(dataset_ref.name, input_config)
    # Wait for import to complete
    logging.info("Starting import from {} to {}".format(source_data, dataset_ref.name))
    response.result()    
    logging.info("Import completed.")

    return dataset_ref.name.split('/')[-1]
 

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
        '--dataset_name',
        type=str,
        required=True,
        help='AutoML dataset name.')
    parser.add_argument(
        '--source_data',
        type=str,
        required=False,
        help='Source data URI. BigQuery or GCS')
    parser.add_argument(
        '--output-project-id',
        type=str,
        required=False,
        help='The file to write the ID of the AutoML project. Provided by KFP.')
    parser.add_argument(
        '--output-dataset-id',
        type=str,
        required=False,
        help='The file to write the ID of the AutoML dataset. Provided by KFP.')
    parser.add_argument(
        '--output-location',
        type=str,
        required=False,
        help='The file to write the location the AutoML dataset. Provided by KFP.')
  
    return parser.parse_args()

def main():
    args = _parse_arguments()

    # Import dataset to AutoML tables
    logging.info("Starting import from: {}".format(args.source_data_uri))
    dataset_id = import_dataset(
        project_id=args.project_id,
        location=args.location,
        dataset_name=args.dataset_name,
        source_data_uri=args.source_data_uri)
        
    # Save project ID, dataset ID, and dataset location to output
    Path(args.output_project_id).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_project_id).write_text(args.project_id)
    Path(args.output_dataset_id).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_dataset_id).write_text(dataset_id)
    Path(args.output_location).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_location).write_text(args.location)


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
    
    