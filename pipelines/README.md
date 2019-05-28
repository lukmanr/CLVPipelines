This folder contains source code for the tutorial's pipelines.

- `src/train_bigquery_pipeline` - The pipeline using Biguery for data pre-processing and AutoML Tables for training 
- `src/train_dataproc_pipeline` - The pipeline using Dataproc (Spark) for data pre-processing and AutoML Tables for training
- `src/batch_predict_pipeline` - The pipeline using Dataproc (Spark) for data pre-processing and AutoML Tables for predictions
- `src/scripts` - The SQL query template used by `train_bigquery` and the PySpark script used by `train_dataproc` and `batch_predict` pipelines.
- `run` - The utility Python and Bash scripts to submit pipelines for execution from a command line.

To compile the pipelines run `./build_pipelines.sh`.


