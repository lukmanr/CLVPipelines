#!/bin/bash

python3 run_pipeline.py \
--port 8082 \
--experiment CLV_TRAIN_DATAPROC \
--run-name TESTING_RUN \
--pipeline_file ../compiled/clv_train_dataproc.tar.gz \
--arguments '{\
"project_id": "sandbox-235500", \
"source_gcs_path: "gs://clv-testing/transactions", \
"output_gcs_path": "gs://clv-testing/features", \
"aml_dataset_name": "clv_features", \
"model_name": "clv_regression", \
"pyspark_script_path": "gs://clv-testing/scripts/create_features_and_label.py" \
}'
