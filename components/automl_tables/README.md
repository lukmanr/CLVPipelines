This folder contains source code for example Kubeflow Pipelines components. The components wrap **AutoML Tables API**.

There are four components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys a trained model as AutoML Tables service
- Batch Predict - runs batch scoring using a trained model

All components are packaged into a single Docker image. 

The folder structure:
- `container` - Dockerfile, and build script
- `src` - Source code for the components
- `tests` - TBD. Currently some helper scripts.
- `import_dataset` - *Import Dataset* component definition file
- `train_model` - *Train Model* component definition file
- `deploy_model` - *Deploy Model* component definition file
- 'batch_predict` - *Batch Predict* component definition file

To build the image run `./container/build_image.sh`. The script builds an image and deploys it to `gcr.io/clv-pipelines/kfp-automl-tables:latest`. 

To use a different registry, pass the full image name as a command line parameter to the script.

To employ a component in a pipeline use `kfp.components.load_component_from_url` referencing a `.yaml` file from a component definition folder. 


