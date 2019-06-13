# Operationalizing Predictive Customer Lifetime Value (CLV) modeling  with Kubeflow Pipelines (KFP)

## Overview

This repository maintains the **Operationalizing Predictive Customer Lifetime Value (CLV) modeling  with Kubeflow Pipelines (KFP)** solution accelerator.

The **Operationalizing Predictive Customer Lifetime Value (CLV) modeling with Kubeflow Pipelines (KFP)** solution accelerator provides automation of CLV modeling techniques described in the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series of articles.

The solution accelerater includes the following components:
- Training and inference KFP pipelines - `/pipelines`
- AutoML Tables KFP components - `/components`
- Build and deployment automation - `/build-deploy`
- Sample integration code - `/run`

### Training and inference KFP pipelines

The solution accelerator includes two template KFP Pipelines:
- The pipeline that automates CLV model training and deployment
- The pipeline that automates batch inference using a trained CLV model

Both pipelines use BigQuery for data preprocessing and feature engineering and AutoML Tables for model training, deployment and inference.

Refer to `/pipelines/README.md` for more information on the pipelines' design and usage.

### AutoML Tables KFP components

The pipelines utilize a number of KFP components including a custom KFP component that wraps AutoML Tables API. The source code for the component can be found in the `components/automl_tables` folder.

Refer to `/components/automl_tables/README.md` for more information on the component's design and usage.

### Build and deployment automation

The process of customizing, compiling and deploying the pipelines and the AutoML Tables component has been automated using Google Cloud Build service. The automation script and its documentation are in the `/build-deploy` folder.

### Sample integration code

The pipelines can be run using Kubeflow Pipelines UI but they can also be integrated with other systems by using `kfp.Client()` programmatic interface. The `/run` folder contains codes samples demonstrating how to use `kfp.Client()` interface.

## Target runtime environment

The solution accelerator has been developed and tested on Kubeflow Pipelines on Google Cloud Platform Kubernetes Engine (GKE). 

The runtime environment required by the solution accelerator is depicted on the below diagram:
![KFP Runtime](/images/architecture.jpg)

The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running on Google Cloud Platform. The pipelines access **Cloud Storage**, **BigQuery**, and **AutoML Tables** services  The container images for the components utilized by the pipelines are managed in **Container Registry**.

### Building a runtime environment

**NOTE**. *The below installation procedure installs a full Kubeflow configuration that includes Kubeflow Pipelines and other components. When a lightweight configuration that only includes Kubeflow Pipeline components is supported this reference will be updated*

To install Kubeflow, including Kubeflow Pipelines on Google Kubernetes Engine follow the instructions on [www.kubeflow.org](https://www.kubeflow.org/docs/gke/deploy/).

**Make sure to configure Identity Aware Proxy (IAP) and Create Permanent Storage**.

The solution accelerator has been developed using Kubeflow v5.0 and Kubeflow Pipelines v0.1.20

### Updating Kubeflow service account permissions
The Kubelfow deployment process creates 3 service accounts:
`<your deployment name>-admin@<your project id>.iam.gserviceaccount.com`
`<your deployment name>-user@<your project id>.iam.gserviceaccount.com`
`<your deployment name>-vm@<your project id>.iam.gserviceaccount.com`
  
By default, the tutorial's pipelines run using `<your deployment name>-user@<your project id>.iam.gserviceaccount.com` account. This account does not have access to AutoML Tables service.
  
To grant AutoML access use GCP Console or `gcloud`.
```
gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
   --member="serviceAccount:<your deployment name>-user@<your project id>.iam.gserviceaccount.com" \
   --role="roles/automl.admin"
```



## Running the pipelines using Kubeflow Pipelines UI

To run the pipelines using Kubeflows Pipelines UI:
- Connect to Kubeflow Pipelines UI. If you deployed Kubeflow using the Deployment Manager the Kubeflow Dashboard is available at `https:[DEPLOYMENT_NAME].endpoints.[YOUR_PROJECT_ID].cloud.goog`. The Kubeflow Pipelines UI is accessible from the Kubeflow Dashboard.
- Locate the `tar.gz` file containing the compiled pipeline in the GCS location configured in the build.
- Upload the compiled pipeline, configure an experiment and start a run following the procedure described in [Kubeflow Pipelines Quickstart](https://www.kubeflow.org/docs/pipelines/pipelines-quickstart). Set the required parameters and if required change the default values.


## Running the pipelines using KFP SDK API

In the previous section of the tutorial, you run the pipelines using Kubeflow Pipelines UI. 

You can also interface with Kubeflow Pipelines programatically using  `kfp.Client()` API from the Kubeflow Pipelines SDK.

`kfp.Client()` is a programmatic interface to the Kubeflow Pipelines service. 

The scripts in `/run` folder demonstrate how to use `kfp.Client()` to connect to the Kubeflow Pipelines service, create experiments and submit runs.

`run_pipeline.py` implements a CLI wrapper around `kfp.Client()`. `run_train.sh` and `run_batch_predict.sh` are example scripts that utilize `run_pipeline.py` to submit pipeline runs.

To submit a run using `run_pipeline.py`

```
python run_pipeline.py --host [HOST_URL] 
                       --experiment [EXPERIMENT_NAME]
                       --run_name [RUN_NAME]
                       --pipeline_file [COMPILED_PIPELINE_FILE]
                       --arguments [DICTIONARY_OF_PIPELINE_ARGUMENTS]
```

**ARGUMENTS**

`--host`

The URL to use to interface with Kubeflow Pipelines. For an IAP enabled cluster set it to:
`https://[YOUR_DEPLOYMENT_NAME].endpoints.[YOUR_PROJECT_ID].[CLIENT_ID]`, where
[CLIENT_ID] is the client ID used by Identity-Aware Proxy.

`--experiment`

The name of experiment. If the experiment under this name does not exist it is created.

`--run_name`

The name of the run.

`--pipeline_file`

The path to a compiled pipeline package. The package can be in one of the formats:
`.tar.gz`, `.tgz`, `.zip`a, `.yaml`.

`--arguments`

A dictionary literal with the pipeline's runtime arguments.

### Installing Kubeflow Pipelines SDK

To use `kfp.Client()` you need a Python 3.5+ environment with KFP SDK installed. It is highly recommended to install KFP SDK into a dedicated Python or Conda environment.

The code in this tutorial was tested with KFP SDK version 0.1.20. 

```
SDK_VERSION=0.1.20
pip install https://storage.googleapis.com/ml-pipeline/release/$SDK_VERSION/kfp.tar.gz --upgrade
```

To use `run_pipeline.py` utility you also need [Python Fire package](https://google.github.io/python-fire/guide/). 
```
pip install fire
```




## Customizing the CLV pipelines
There are three primary ways you can customize the tutorial's pipelines:
- Modifying the settings that affect compilation
- Modifying or replacing data preprocessing SQL script
- Modifying orchestration
### Customizing compilation settings
### Customizing feature engineering
### Customizing orchestration



he sample dataset used in the tutorial is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. The build script copies this file to a GCS folder in your project.

