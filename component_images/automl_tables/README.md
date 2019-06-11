This folder contains source code for Kubeflow Pipeline components that wrap selected **AutoML Tables APIs**.

There are five components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys an AutoML model
- Batch Predict - runs batch inference
- Log Evaluation Metrics - retrieves and logs (as an KFP Markdown artifact) the latest evaluation metrics for an AutoML model

All components are packaged into a single Docker image described by `Dockerfile`

The folder structure:
- `src` - Source code for the components
- `tests` - TBD. Currently some helper scripts.



