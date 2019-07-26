#!/bin/bash

python kfp-cli.py \
run_pipeline \
--experiment_name "CLV Training" \
--run-name "Training run" \
--pipeline_name train_pipeline \
--params '{\
"project_id": "jktest5", \
"source_gcs_path": "gs://jkclv-bucket2/dataset/transactions.csv", \
"source_bq_table": "", \
"bq_dataset_name": "", \
"transactions_table_name": "transactions", \
"features_table_name": "features", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
}'
