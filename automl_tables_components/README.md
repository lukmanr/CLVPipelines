This folder contains source code for a group of Kubeflow Pipeline components that wrap selected **AutoML Tables APIs**.

There are five components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys an AutoML model for online predictions
- Batch Predict - runs a batch inference using a trained AutoML model
- Log Evaluation Metrics - retrieves and logs (as an KFP Markdown artifact) the  evaluation metrics for an AutoML model

All components are packaged into a single Docker image described by `Dockerfile`

The folder structure:
- `src` - Source code for the components
- `specs` - YAML specifications of the components
- `tests` - Scripts to help with testing.



