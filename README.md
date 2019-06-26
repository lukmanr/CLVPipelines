# Predicting Customer Lifetime Value with Kubeflow Pipelines

## Solution Overview

This repository maintains the source code for the **Predicting Customer Lifetime Value with Kubeflow Pipelines** solution.

The **Predicting Customer Lifetime Value** solution  delivers automation of Customer Lifetime Value (CLV) modeling techniques described in the [Predicting Customer Lifetime Value with AI Platform](https://cloud.google.com/solutions/machine-learning/clv-prediction-with-offline-training-intro) series of articles.

The primary goal of the solution is to orchestrate two Machine Learning workflows:
- The training and deployment of the Customer Lifetime Value predictive model.
- Batch inference using the deployed Customer Lifetime Value predictive model.

The below diagram depicts the high level architecture of the solution:

![KFP Runtime](./images/architecture.jpg)

In the solution, **Kubeflow Pipelines** is used solely as an orchestrator of Google Cloud  managed services: **BigQuery**, **AutoML Tables**, and **Cloud Storage**. **BigQuery** is used for data pre-processing and feature engineering. **AutoML Tables** is used for model training and inference. **Cloud Storage** is used primarly for staging input and output data.

The Kubeflow Pipelines services are hosted on **Google Kubernetes Engine** running on Google Cloud Platform. The solution's training and inference pipelines access **BigQuery**,  **AutoML Tables** services through a set of Kubeflow Pipelines components that wrap the respective **Google Cloud APIs**. The container images for the components utilized by the pipelines are managed in **Container Registry**.

Refer to [README](./pipelines/README.md) in the `/pipelines` folder of this repo for more details on the design and usage the training and deployment pipelines.

Refer to [README](./components/automl_tables/README.md) in the `/components/automl_tables` folder of this repo for more details on the design and usage of the AutoML Tables components.


## Installing Kubeflow Pipelines

The solution has been developed and tested on Kubeflow Pipelines on Google Cloud Platform Kubernetes Engine (GKE).

You can run the solution on a full **Kubeflow** installation  or on a lightweight deployment that only includes core Kubeflow Pipelines services. The full Kubeflow installation can be provisioned following [the Kubeflow on GCP guide](https://www.kubeflow.org/docs/gke/deploy/). The lightweight Kubeflow Pipelines deployment can be performed using the automation script delivered as a part of the solution.

Refer to [README](./install/README.md) in the `/install` folder of this repo for the detailed installation instructions.

## Building and deploying the solution

The building and deploying of the solution components has been automated using **Cloud Build**.

Refer to [README](./deploy/README.md) in the `/deploy` folder of this repo for the detailed deployment instructions.

## Running the solution's pipelines

There are two ways to run the solution's pipelines:
- Using Kubeflow Pipelines UI
- Using KFP SDK

Refer to [README](./run/README.md) in the `/run` folder of this repo for detailed instructions on how to trigger runs.

## Repository structure

`/pipelines`
The source code for two template KFP Pipelines:
- The pipeline that automates CLV model training and deployment
- The pipeline that automates batch inference


`/components`

The source code for the KFP components that wrap selected **AutoML Tables** APIs.

`/install`

Lightweight Kubeflow Pipelines deployment installation script

`/deploy`

Cloud Build configuration for automated building and deployment of the solution.

`/run`

Sample code demonstrating how to use the `kfp.Client()` programmatic interface to KFP services.



## Acknowledgements

The sample dataset used in the solution accelrator is based on the publicly available [Online Retail Data Set](http://archive.ics.uci.edu/ml/datasets/Online+Retail) from the UCI Machine Learning Repository.

The original dataset was preprocessed to conform to the the schema used by the solution's pipelines and uploaded to a public GCP bucket as `gs://clv-datasets/transactions/`.



