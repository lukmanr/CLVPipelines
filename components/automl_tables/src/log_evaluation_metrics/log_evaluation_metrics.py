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

from common import get_latest_evaluation_metrics, write_metadata_for_output_viewers
from google.cloud import automl_v1beta1 as automl


def log_metrics(model_full_id):
  """Retrieves and logs the latest evaluation metrics for an AutoML Tables  model."""

  metrics = get_latest_evaluation_metrics(model_full_id)

  markdown_metadata = None
  if isinstance(metrics, automl.types.RegressionEvaluationMetrics):
    markdown_metadata = regression_evaluation_metrics_to_markdown_metadata(
        metrics)
  elif isinstance(metrics, automl.types.ClassificationEvaluationMetrics):
    markdown_metadata = classification_evaluation_metrics_to_markdown_metadata(
        metrics)

  write_metadata_for_output_viewers(markdown_metadata)


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


def classification_evaluation_metrics_to_markdown_metadata(metrics):
  """Converts classification evaluation metrics to KFP Viewer markdown metadata."""

  markdown = "TBD"

  markdown_metadata = {
      "type": "markdown",
      "storage": "inline",
      "source": markdown
  }

  return markdown_metadata
