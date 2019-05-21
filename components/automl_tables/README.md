This folder contains source code for example Kubeflow Pipelines components. The components wrap **AutoML Tables API**.

There are four components:
- Import Dataset - creates and populates an AutoML Dataset from BigQuery or GCS source
- Train Model - trains an AutoML model
- Deploy Model - deploys a trained model as AutoML Tables service
- Batch Predict - runs batch scoring using a trained model

All components are packaged into a single Docker image. 

The folder structure:
- `./` - Dockerfile, and build script
- `./src` - Source code for the components
- `./specs` - Component specifications
- `./tests` - TBD. Currently some helper scripts.

To build the image run `./build_image.sh`. The script builds an image and deploys it to `gcr.io/clv-pipelines/kfp-automl-tables:latest`. 

To use a different registry pass the full image name as a command line parameter to the script.

