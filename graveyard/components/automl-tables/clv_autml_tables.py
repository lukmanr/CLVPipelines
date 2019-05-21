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

BASE_IMAGE = 'gcr.io/sandbox-235500/automltablesbase:dev'

@kfp.dsl.python_component(name='Import features', base_image=BASE_IMAGE)
def import_dataset(
    project_id: str,
    location: str,
    dataset_name: str,
    source_data: str) -> str:
    """Imports clv features into an AutoML dataset"""

    import logging
    from google.cloud import automl_v1beta1 as automl

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

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


@kfp.dsl.python_component(name='Train model', base_image=BASE_IMAGE)
def train_model(
    project_id: str,
    location: str,
    dataset_id: str,
    model_name: str,
    train_budget: int,
    optimization_objective: str,
    target_name: str,
    features_to_exclude: str) -> str:
    """Train an AutoML Tables model"""

    import logging
    import re
    from google.cloud import automl_v1beta1 as automl

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    client = automl.AutoMlClient()

    # Retrieve a table spec for the primary table
    dataset_path = client.dataset_path(project_id, location, dataset_id)
    dataset_ref = client.get_dataset(dataset_path)
    primary_table_spec_id = dataset_ref.tables_dataset_metadata.primary_table_spec_id
    # Filtering does not seem to work so scan through all table_specs
    table_specs = client.list_table_specs(parent=dataset_path)
    primary_table_spec = [table_spec for table_spec in table_specs if 
        re.fullmatch('.*%s' % primary_table_spec_id, table_spec.name)][0]

    # Retrieve column specs for the primary table
    column_specs = client.list_column_specs(primary_table_spec.name)
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
    logging.info( "Starting training model: {}".format(model_name))
    response = client.create_model(
        parent=location_path,
        model={
            "display_name": model_name,
            "dataset_id": dataset_id,
            "tables_model_metadata": tables_model_metadata
        }
    )
    # Wait for completion
    result = response.result()
    logging.info("Training completed")
    return result.name


def main():
    """Build KFP components"""

    args = _parse_arguments()
    # Build prepare_features components

    kfp.compiler.build_python_component(
        component_func=import_dataset,
        staging_gcs_path=args.gcs_staging_path,
        target_component_file='clv-import-dataset.yaml',
        target_image='gcr.io/{}/clv-import-dataset:latest'.format(args.container_registry))

    kfp.compiler.build_python_component(
        component_func=train_model,
        staging_gcs_path=args.gcs_staging_path,
        target_component_file='clv-train-model.yaml',
        target_image='gcr.io/{}/clv-train-model:latest'.format(args.container_registry))

def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--container-registry',
        type=str,
        #required=True,
        default='sandbox-235500',
        help='The GCP container registry for the target image.')
    parser.add_argument(
        '--gcs-staging-path',
        type=str,
        #required=True,
        default='gs://sandbox-235500/staging',
        help='The GCS path for the staging area used by Kaniko')
 
    return parser.parse_args()

if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
    
