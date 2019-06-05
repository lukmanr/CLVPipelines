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


def get_latest_evaluation_metrics(model_full_id):
    """Retrieves the latest evaluation metrics for an AutoML Tables model"""
    
    client = automl.AutoMlClient()
    evaluations = list(client.list_model_evaluations(model_full_id))

    create_seconds = 0
    evaluation_metrics = None
    for evaluation in evaluations:
        if evaluation.create_time.seconds > create_seconds:
          if evaluation.regression_evaluation_metrics.ListFields():
            evaluation_metrics = evaluation.regression_evaluation_metrics
            create_seconds = evaluation.create_time.seconds
          elif evaluation.classification_evaluation_metrics.ListFields():
            evaluation_metrics = evaluation.classification_evaluation_metrics
            create_seconds = evaluation.create_time.seconds

    return evaluation_metrics


def evaluation_metrics_to_markdown_metadata(metrics):
    """Converts evaluation metrics to KFP Viewer markdown metadata
    
    Currently, only regression evaluation metrics are supported..
    """

    regression_markdown_template = (
        "**Evaluation Metrics:**  \n"
        "&nbsp;&nbsp;&nbsp;&nbsp;**RMSE:**            {rmse}  \n"
        "&nbsp;&nbsp;&nbsp;&nbsp;**MAE:**             {mae}  \n"
        "&nbsp;&nbsp;&nbsp;&nbsp;**R-squared:**       {rsquared}  \n"
    )

    if isinstance(metrics, automl.types.RegressionEvaluationMetrics):
        markdown = regression_markdown_template.format(
            rmse=round(metrics.root_mean_squared_error, 2),
            mae=round(metrics.mean_absolute_error, 2),
            rsquared=round(metrics.r_squared, 2)
        )
    else:
        markdown = "TBD"

    markdown_metadata = {"type": "markdown", "storage": "inline", "source": markdown}

    return markdown_metadata


def write_metadata_for_output_viewers(*argv):
    """Writes items to be rendered by KFP UI as artificats"""

    metadata = {
        "version": 1,
        "outputs": argv 
    }

    with open('/mlpipeline-ui-metadata.json', 'w') as f:
            json.dump(metadata, f)





def _compile_pipeline(output_dir, local_search_paths, url_search_prefixes, platform='GCP', type_check=False):
    """Compile the pipeline"""

    # Set globals controlling compilation
    component_store.local_search_paths = local_search_paths 
    component_store.url_search_prefixes = url_search_prefixes
    platform=platform

    # Compile the pipeline using the name of the pipeline function as a file prefix
    pipeline_func = clv_train
    pipeline_filename = pipeline_func.__name__ + '.tar.gz'
    pipeline_path = os.path.join(output_dir, pipeline_filename)
    kfp.compiler.Compiler().compile(pipeline_func, pipeline_path, type_check=type_check) 




if __name__ == '__main__':
    fire.Fire(_compile_pipeline)


"""
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
        '--primary-metric',
        type=str,
        required=True,
        help='Primary metric to pass to output')
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
    parser.add_argument(
        '--output-primary-metric-value',
        type=str,
        required=True,
        help='The file to write the value of primary metric. Provided by KFP.')
   
    return parser.parse_args()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    args = _parse_arguments()
 
    logging.info( "Starting model training: {}".format(args.model_name))
    model_full_id = train_model(
        project_id=args.project_id,
        location=args.location,
        dsataset_id=args.dataset_id,
        model_name=args.model_name,
        train_budget=args.train_budget,
        optimization_objective=args.optimization_objective,
        target_name=args.target_name,
        features_to_exclude=args.features_to_exclude
    )
    logging.info("Training completed")

    model_full_id = "projects/165540728514/locations/us-central1/models/TBL1359603302349668352"
    print(model_full_id)

    # Write evaluation metrics to Output Viewer
    metrics = get_latest_evaluation_metrics(model_full_id)
    markdown = evaluation_metrics_to_markdown_metadata(metrics)
    #write_metadata_for_output_viewers(markdown)

    # Get the primary metric from evaluation metrics
    primary_metric_value = str(getattr(metrics, args.primary_metric)) if hasattr(metrics, args.primary_metric) else 'N/A'

    # Save model full id  to output
    Path(args.output_model_full_id).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_model_full_id).write_text(model_full_id)
    Path(args.output_primary_metric_value).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output_primary_metric_value).write_text(primary_metric_value)
  
   """

    