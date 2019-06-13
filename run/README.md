This folder contains sample code demonstrating how to use `kfp.Client()` API to configure experiments and submit pipeline runs programmatically.


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



