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

import re
import argparse
import logging
import json
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def train_model(
    project_id,
    location,
    dataset_id,
    model_name,
    train_budget,
    optimization_objective,
    target_name,
    features_to_exclude):
    """Train an AutoML Tables model"""

    client = automl.AutoMlClient()

    # Retrieve column specs for the primary table
    dataset_path = client.dataset_path(project_id, location, dataset_id)
    dataset_ref = client.get_dataset(dataset_path)
    primary_table_path = client.table_spec_path(
            project_id,
            location,
            dataset_id,
            dataset_ref.tables_dataset_metadata.primary_table_spec_id)
    column_specs = client.list_column_specs(primary_table_path)
    column_specs_dict = {spec.display_name: spec for spec in column_specs}
 
    # Set model metadata
    tables_model_metadata = {}
    # Set maximum training time
    if train_budget:
        tables_model_metadata.update(
            {'train_budget_milli_node_hours': train_budget}
        )
    # Set the target column
    if target_name:
        tables_model_metadata.update(
            {'target_column_spec': column_specs_dict[target_name]}
        )
    # Set features to use for training
    if features_to_exclude:
        to_exclude = features_to_exclude.split(',')
        to_exclude.append(target_name)
        to_use = set(to_exclude).symmetric_difference(column_specs_dict.keys())
        feature_column_specs = [column_specs_dict[column_name]
            for column_name in to_use] 
        tables_model_metadata.update(
            {'input_feature_column_specs': feature_column_specs}
        )
    # Set optimization objective
    if optimization_objective:
        tables_model_metadata.update(
            {'optimization_objective': optimization_objective}
        )
    # Create a model with the model metadata in the region
    location_path = client.location_path(project_id, location)
    response = client.create_model(
        parent=location_path,
        model={
            "display_name": model_name,
            "dataset_id": dataset_id,
            "tables_model_metadata": tables_model_metadata
        }
    )
    # Wait for completion
    return response.result().name


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
        '--dataset-id',
        type=str,
        required=True,
        help='AutoML dataset id.')
    parser.add_argument(
        '--model-name',
        type=str,
        required=True,
        help='AutoML model name')
    parser.add_argument(
        '--train-budget',
        type=int,
        required=True,
        help='AutoML training budget')
    parser.add_argument(
        '--optimization-objective',
        type=str,
        required=True,
        help='AutoML optimization objective')
    parser.add_argument(
        '--target-name',
        type=str,
        required=True,
        help='Target (Label) column in AutoML dataset')
    parser.add_argument(
        '--features-to-exclude',
        type=str,
        required=True,
        help='A comma separated list of features to exclude from training')
    parser.add_argument(
        '--output-model-full-id',
        type=str,
        required=True,
        help='The file to write the ID of the trained model. Provided by KFP.')
  
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = _parse_arguments()

    logging.info( "Starting model training: {}".format(args.model_name))
    model_full_id = train_model(
        project_id=args.project_id,
        location=args.location,
        dataset_id=args.dataset_id,
        model_name=args.model_name,
        train_budget=args.train_budget,
        optimization_objective=args.optimization_objective,
        target_name=args.target_name,
        features_to_exclude=args.features_to_exclude
    )

    logging.info("Training completed")

    # Save model full id  to output
    Path(args.output_model_full_id).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_model_full_id).write_text(model_full_id)
 
    
    