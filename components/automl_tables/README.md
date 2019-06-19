# AutoML Tables KFP components

This folder contains source code for a group of Kubeflow Pipeline components that wrap selected **AutoML Tables APIs**.

There are five components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys an AutoML model for online predictions
- Batch Predict - runs a batch inference using a trained AutoML model
- Log Evaluation Metrics - retrieves and logs (as an KFP Markdown artifact) the  evaluation metrics for an AutoML model



## Folder content

The folder structure:
- `./Dockerfile` - All components are packaged into a single Docker image
- `src` - Source code for the components
- `specs` - YAML specifications for the components in the `kfp.ComponentStore` compatible folder structure
- `tests` - Scripts to help with testing.
- `docs` - Documentation formatted in the AI Hub convention.
