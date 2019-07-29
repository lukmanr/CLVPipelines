#!/bin/bash

python kfp-cli.py \
run_pipeline \
--experiment "CLV Predict" \
--run-name "Batch predict run" \
--pipeline_name predict_pipeline \
--arguments '{\
"project_id": "jktest6", \
"source_gcs_path": "gs://jkclv-bucket2/dataset/test_transactions.csv", \
"source_bq_table": "", \
"bq_dataset_name": "", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
"aml_model_id": "TBL9153944474630488064", \
"destination_prefix": "bq://clv-dev", \
}'
