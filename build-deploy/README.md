This folder contains Cloud Build artifacts:
- `cloudbuild.yaml` - a Cloud Build config file
- `build.sh` - a bash script template that uses `gcloud builds submit` to configure and start the build
- `kfp-compiler-builder/Dockerfile` - Dockerfile for an image used by the builds custom steps.
- `helpers` - a folder with utility scripts used during the build
  - `update_image_name_in_specs.py` - updating the `image` node in the component specs. 
  - `helpers/update_settings_file.py` - updating the pipelines setting file


## Building and deploying the pipelines
Before the tutorial's pipelines can be run, they have to be configured, compiled, and deployed in your project.

The building and deploying of the pipelines have been automated using [GCP Cloud Build](https://cloud.google.com/cloud-build/docs/).  The build process goes through the following steps:
1. Copy the solution's github repo into the Cloud Build runtime environment
1. Create a docker image to support custom build steps
1. Build a base image for the pipeline's helper components (refer to the later sections to understand the pipeline's design). The name of the image is provided as a build parameter.
1. Build an image that hosts components wrapping AutoML Tables API. The name of the image is provided as a build parameter.
1. Update the YAML specifications of the AutoML Tables components with the name of the image created in the previous step
1. Update the settings that control the pipelines' compilation. The values for these settings are provided as build parameters.
1. Compile the pipelines. 
1. Deploy the compiled pipelines to a GCS folder in your project. The path to the folder is provided as a build parameter.
1. Deploy the artifacts used by the pipelines at runtime to a GCS folder in your project. The path to the folder is provided as a build parameter.
1. Deploy the component images to the Container Registry of your project. 
1. Copy the sample dataset to a GCS folder in your project. The path to the folder is provided as a build parameter.

You can start the build using the `gcloud builds submit` command. The build config file containg the above instructions is in the `cloud-build` folder of this repo. The build execution is controlled by a set of parameters that are set when the build is submitted for execution. The following arguments are required:




Parameter | Description 
-----------|-------------
_CLV_REPO  | The name of the github repository with the solution's source components. 
_BASE_IMAGE | The name of a base image for Lightweight Python compoments. Specify the image name only. The image will be pushed to `gcr.io/[YOUR_PROJECT_ID]/[_BASE_IMAGE]`
_AUTOML_TABLES_IMAGE | The name of an image that hosts AutoML Tables components
_TRAIN_PIPELINE | The name for the compiled training pipeline. The compiled pipeline will be saved as `[_TRAIN_PIPELINE].tar.gz`
_PREDICT_PIPELINE | The name for the compiled training pipeline. The compiled pipeline will be saved as `[_PREDICT_PIPELINE].tar.gz` |
_BUCKET_NAME | The name of a GCP bucket in your project to store compiled pipelines and other artifacts used by the pipelines. If the bucket does not exist, it will be created by the build 
_PIPELINES_FOLDER | The name of the folder in _BUCKET_NAME to store the compiled pipelines
_ARTIFACTS_FOLDER | The name of the folder in _BUCKET_NAME to store artificats used by the pipelines at running time. 
_SAMPLE_DATASET_FOLDER | The name of the folder in _BUCKET_NAME to store the sample dataset used by the pipelines.


The `/cloud-build/build.sh` demonstrates how to use `gcloud builds submit` to start the build process. 


To build and deploy the pipelines:
1. Open [Cloud Shell](https://cloud.google.com/shell/docs/) in your project.
2. Create a working directory and download build configuration
```
cd
mkdir [DIRECTORY_NAME]
cd [DIRECTORY_NAME]
wget https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/cloud-build/cloudbuild.yaml
wget https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/cloud-build/build.sh
```
3. Update `build.sh` with your argument values
4. Start the build
```
chmod 755 build.sh
./build.sh
```


