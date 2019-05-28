This folder contains source code for example Kubeflow Pipelines components. The components wrap **AutoML Tables API**.

There are five components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys a trained model as AutoML Tables service
- Batch Predict - runs batch scoring using a trained model - TBD
- Retrieve Regression Evaluation Metrics - retrieves and logs (as a KFP artifact) regression evaluation metrics from a trained regression model.

All components are packaged into a single Docker image. 

The folder structure:
- `src` - Source code for the components
- `tests` - TBD. Currently some helper scripts.
- `specs` - YAML specifications of the components

To build the image run `./build_image.sh`. The script builds an image and deploys it to `gcr.io/clv-pipelines/kfp-automl-tables:latest`. 

To use a different registry, pass the full image name as a command line parameter to the script.

To employ a component in a pipeline use `kfp.components.load_component_from_url` referencing a `.yaml` file from a component definition folder. 


