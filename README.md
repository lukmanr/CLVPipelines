# Solution Accelerator - Operationalizing Predictive Customer Lifetime Value (CLV) modeling  with Kubeflow Pipelines (KFP)

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

The pipelines utilize a number of KFP components including custom KFP components that wrap selected AutoML Tables APIs. The source code for the components can be found in the `components/automl_tables` folder.

Refer to `/components/automl_tables/README.md` for more information on the components' design and usage.

### Build and deployment automation

The process of customizing, compiling and deploying the pipelines and the AutoML Tables components has been automated using Google Cloud Build service. The automation script and its documentation are in the `/build-deploy` folder.

### Sample integration code

The pipelines can be run using Kubeflow Pipelines UI but they can also be integrated with other systems by using `kfp.Client()` programmatic interface. The `/run` folder contains codes samples demonstrating how to use `kfp.Client()` interface.

## Target runtime environment

The solution accelerator has been developed and tested on Kubeflow Pipelines on Google Cloud Platform Kubernetes Engine (GKE). 

The runtime environment required by the solution accelerator is depicted on the below diagram:
![KFP Runtime](/images/architecture.jpg)

The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running on Google Cloud Platform. The pipelines access **Cloud Storage**, **BigQuery**, and **AutoML Tables** services. The container images for the components utilized by the pipelines are managed in **Container Registry**.

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

### Kubeflow Pipelines installation automation

TBD

`/kfp-installation`





## Acknowledgements

The sample dataset used in the solution accelrator is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository. 

The original dataset was preprocessed to conform to the above schema and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/transactions.cv`. 

