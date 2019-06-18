#!/bin/bash

python run_pipeline.py \
--host https://jkkf.endpoints.sandbox-235500.cloud.goog/pipeline \
--experiment CLV_BATCH_PREDICT \
--run-name TESTING_RUN \
--pipeline_file clv_predict.tar.gz \
--arguments '{\
"project_id": "clv-prod", \
"source_gcs_path": "gs://clv-accelerator/sample-dataset/transactions.csv", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
"aml_model_id": "TBL8120491505451270144", \
"destination_prefix": "bq://clv-dev", \
}'
