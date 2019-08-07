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
"""Wrapper around AutoML Tables Create Model API."""

import logging

from pathlib import Path

from google.cloud import automl_v1beta1 as automl


def train(project_id, region, dataset_id, model_name, train_budget,
          optimization_objective, target_name, features_to_exclude,
          output_model_full_id):
  """Trains an AutoML Tables model.

  Args:
    project_id: The project ID for AutoML.
    region: The region for AutoML processing.
    dataset_id: The ID of an AutoML dataset.
    model_name: The name of an AutoML model.
    train_budget: AutoML training budget in millihours.
    optimization_objective: AutoML Tables optimization objective.
    target_name: The name of the column to be used as the training
      label.
    features_to_exclude: The list of features to exclude from a
      training run.
    output_model_full_id: KFP use.
  """

  logging.basicConfig(level=logging.INFO)

  client = automl.AutoMlClient()

  # Retrieve column specs for the primary table
  dataset_path = client.dataset_path(project_id, region, dataset_id)
  dataset_ref = client.get_dataset(dataset_path)
  primary_table_path = client.table_spec_path(
      project_id, region, dataset_id,
      dataset_ref.tables_dataset_metadata.primary_table_spec_id)
  column_specs = client.list_column_specs(primary_table_path)
  column_specs_dict = {spec.display_name: spec for spec in column_specs}

  # Set model metadata
  tables_model_metadata = {}
  # Set maximum training time
  if train_budget:
    tables_model_metadata.update(
        {'train_budget_milli_node_hours': train_budget})
  # Set the target column
  if target_name:
    tables_model_metadata.update(
        {'target_column_spec': column_specs_dict[target_name]})
  # Set features to use for training
  if features_to_exclude:
    to_exclude = features_to_exclude
    to_exclude.append(target_name)
    to_use = set(to_exclude).symmetric_difference(column_specs_dict.keys())
    feature_column_specs = [
        column_specs_dict[column_name] for column_name in to_use
    ]
    tables_model_metadata.update(
        {'input_feature_column_specs': feature_column_specs})
  # Set optimization objective
  if optimization_objective:
    tables_model_metadata.update(
        {'optimization_objective': optimization_objective})

  # Create a model with the model metadata in the region
  logging.info('Starting model training')
  location_path = client.location_path(project_id, region)
  response = client.create_model(
      parent=location_path,
      model={
          'display_name': model_name,
          'dataset_id': dataset_id,
          'tables_model_metadata': tables_model_metadata
      })
  # Wait for completion
  model_full_id = response.result().name
  logging.info('Model training completed: {}'.format(model_full_id))

  Path(output_model_full_id).parent.mkdir(parents=True, exist_ok=True)
  Path(output_model_full_id).write_text(model_full_id)
