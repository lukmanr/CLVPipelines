## Running the solution's pipelines

There are two ways of triggering a KFP pipeline run:
- Using the Kubeflow Pipelines UI
- Using the KFP SDK

### Running the pipelines using Kubeflow Pipelines UI

If you provisioned the lightweight Kubeflow Pipelines deployment, the KFP UI is available at the URL printed at the end of the Kubeflow Pipelines deployment process. You can also retrieve it using the following command:

`echo "https://"$(kubectl describe configmap inverse-proxy-config -n kubeflow | grep "googleusercontent.com")`

Use the procedure described in [Pipelines Quickstart](https://www.kubeflow.org/docs/pipelines/pipelines-quickstart/) to create experiments and submit pipeline runs.

The compiled training pipeline hase been stored by Cloud Build in the following GCS location:

`gs://[_BUCKET_NAME][_PIPELINES_FOLDER]/[_TRAIN_PIPELINE].tar.gz`

The compiled batch predict pipeline in

`gs://[_BUCKET_NAME][_PIPELINES_FOLDER]/[_PREDICT_PIPELINE].tar.gz`

The runtime parameters required by the pipelines are described in detail in [`/pipelines/README.md`](/pipelines/README.md)


### Running the pipelines using KFP SDK


This folder contains code samples demonstrating how to use `kfp.Client()` API from KFP SDK to configure experiments and submit pipeline runs programmatically.

The `run_pipeline.py` Python script implements a CLI wrapper around `kfp.Client()`. The `run_train.sh` and `run_batch_predict.sh` are example bash scripts that utilize `run_pipeline.py` to submit pipeline runs.

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

The URL to use to interface with Kubeflow Pipelines. 

`--experiment`

The name of experiment. If the experiment under this name does not exist it is created.

`--run_name`

The name of the run.

`--pipeline_file`

The path to a compiled pipeline package. The package can be in one of the formats:
`.tar.gz`, `.tgz`, `.zip`a, `.yaml`.

`--arguments`

A dictionary literal with the pipeline's runtime arguments.



#### Installing Kubeflow Pipelines SDK

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



