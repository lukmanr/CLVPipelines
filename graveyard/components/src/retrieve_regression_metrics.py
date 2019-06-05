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

import argparse
import logging
import json
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def retrieve_regression_evaluation_metrics(model_full_id):
    """Retrieves  the latest regression metrics for an AutoML Tables  model"""
    
    client = automl.AutoMlClient()

    evaluations = list(client.list_model_evaluations(model_full_id))
    create_seconds = 0
    evaluation_metrics = None
    for evaluation in evaluations:
        if evaluation.regression_evaluation_metrics.ListFields():
            if evaluation.create_time.seconds > create_seconds:
                evaluation_metrics = evaluation.regression_evaluation_metrics
                create_seconds = evaluation.create_time.seconds

    return evaluation_metrics

def retrieve_latest_evaluation_metrics(model_full_id):
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

    
def write_regression_metrics(metrics):
    """Writes metrics metadata

    This does not seem to be working with the current UI"""

    metrics = {
        'metrics': [
        {
            'name': 'RMSE',
            'numberValue': round(metrics.root_mean_squared_error, 2),
            'format': "RAW"
        },
        {
            'name': 'MAE',
            'numberValue': round(metrics.mean_absolute_error, 2),
            'format': "RAW"
        },
        {
            'name': 'R-squared',
            'numberValue': round(metrics.r_squared, 2),
            'format': "RAW"
        }]
    }

    with open('/mlpipeline-metrics.json', 'w') as f:
        json.dump(metrics, f)


def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--model-full-id',
        type=str,
        required=True,
        help='The full id of a model.')
    parser.add_argument(
        '--output-rmse',
        type=str,
        required=True,
        help='The filename of the RMSE output. Provided by KFP')
    parser.add_argument(
        '--output-mae',
        type=str,
        required=True,
        help='The filename of the MAE output. Provided by KFP')
    parser.add_argument(
        '--output-rsquared',
        type=str,
        required=True,
        help='The filename of the output metrics file. Provided by KFP')
 
    return parser.parse_args()

    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    args = _parse_arguments()
    
    logging.info("Retrieving metrics for model: {}".format(args.model_full_id))

    metrics = retrieve_latest_evaluation_metrics(args.model_full_id)

    print(evaluation_metrics_to_markdown_metadata(metrics))
    
 

    # Write metrics to the output
    #Path(args.output_rmse).parent.mkdir(parents=True, exist_ok=True)
    #Path(args.output_rmse).write_text(str(metrics.root_mean_squared_error) if metrics else 'N/A')
    #Path(args.output_mae).parent.mkdir(parents=True, exist_ok=True)
    #Path(args.output_mae).write_text(str(metrics.mean_absolute_error) if metrics else 'N/A')
    #Path(args.output_rsquared).parent.mkdir(parents=True, exist_ok=True)
    #Path(args.output_rsquared).write_text(str(metrics.r_squared) if metrics else 'N/A')
