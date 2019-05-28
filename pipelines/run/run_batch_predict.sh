#!/bin/bash

python3 run_pipeline.py \
--port 8082 \
--experiment CLV_BATCH_PREDICT \
--run-name TESTING_RUN \
--pipeline_file ../compiled/clv_batch_predict.tar.gz \
--arguments '{\
"project_id": "sandbox-235500", \
"model_id": "TBL403503175207747584", \
"datasource": "gs://clv-testing/transactions", \
"destination": "bq://sandbox-235500", \
"dataproc_gcs_output": "gs://clv-testing/features", \
"pyspark_script_path": "gs://clv-testing/scripts/create_features_and_label.py" \
}'
