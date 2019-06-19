# Copyright 2019 Google Inc. All Rights Reserved.
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
"""Implementation of the KFP component that retrieves and outputs to the KFP artifact viewer the latest evaluation metrics.

Currently only regression evaluation metrics are supported
"""

import logging
import json
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def log_metrics(model_full_id, primary_metric, output_primary_metric_value):
  """Retrieves and logs the latest evaluation metrics for an AutoML Tables  model.
  
  A full set of metrics is written out as a Markdown output artifact.
  The primary metric is written out as a pipeline metric and returned as an output
  """

  metrics = get_latest_evaluation_metrics(model_full_id)

  if isinstance(metrics, automl.types.RegressionEvaluationMetrics):
    markdown_metadata = regression_evaluation_metrics_to_markdown_metadata(
        metrics)
  elif isinstance(metrics, automl.types.ClassificationEvaluationMetrics):
    markdown_metadata = classification_evaluation_metrics_to_markdown_metadata(
        metrics) 

  write_metadata_for_output_viewers(markdown_metadata)

  output_primary_metric_value = str(getattr(metrics, primary_metric)) if hasattr(
    metrics, primary_metric) else None 
  
  print(primary_metric)
  print(primary_metric_value)


  """
  if primary_metric_value:
    metric_metadata = {
      'name': primary_metric,
      'numberValue': primary_metric_value
    }
    print(metric_metadata)
    write_metrics(primary_metric_value)
  """

  accuracy = 0.9
  metrics = {
    'metrics': [{
      'name': 'accuracy-score',
      'numberValue':  accuracy,
      'format': "PERCENTAGE",
    }]
  }
  with open('/mlpipeline-metrics.json', 'w') as f:
    json.dump(metrics, f)

  Path(output_primary_metric_value).parent.mkdir(parents=True, exist_ok=True)
  Path(output_primary_metric_value).write_text(output_primary_metric_value)
 

def classification_evaluation_metrics_to_markdown_metadata(metrics):
  """Converts classification evaluation metrics to KFP Viewer markdown metadata."""

  markdown = "TBD"

  markdown_metadata = {
      "type": "markdown",
      "storage": "inline",
      "source": markdown
  }

  return markdown_metadata

def regression_evaluation_metrics_to_markdown_metadata(metrics):
  """Converts regression evaluation metrics to KFP Viewer markdown metadata."""

  regression_markdown_template = (
      "**Evaluation Metrics:**  \n"
      "&nbsp;&nbsp;&nbsp;&nbsp;**RMSE:**            {rmse}  \n"
      "&nbsp;&nbsp;&nbsp;&nbsp;**MAE:**             {mae}  \n"
      "&nbsp;&nbsp;&nbsp;&nbsp;**R-squared:**       {rsquared}  \n")

  markdown = regression_markdown_template.format(
      rmse=round(metrics.root_mean_squared_error, 2),
      mae=round(metrics.mean_absolute_error, 2),
      rsquared=round(metrics.r_squared, 2))

  markdown_metadata = {
      "type": "markdown",
      "storage": "inline",
      "source": markdown
  }

  return markdown_metadata

def get_latest_evaluation_metrics(model_full_id):
  """Retrieves the latest evaluation metrics for an AutoML Tables model."""

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


def write_metadata_for_output_viewers(*argv):
  """Writes items to be rendered by KFP UI as artificats."""

  output_metadata = {'version': 1, 'outputs': argv}
  with open('/mlpipeline-ui-metadata.json', 'w') as f:
    json.dump(output_metadata, f)

def write_metrics(*metrics):
  """Writes pipeline metrics."""

  metrics_metadata = {'metrics': metrics}
  with open('/mlpipeline-metrics.json', 'w') as f:
    json.dump(metrics_metadata, f)
