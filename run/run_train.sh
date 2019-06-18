#!/bin/bash

python run_pipeline.py \
--host http://localhost:8082 \
--experiment "CLV Training" \
--run-name "Training run" \
--pipeline_file clv_train.tar.gz \
--arguments '{\
"project_id": "clv-prod", \
"source_gcs_path": "gs://clv-accelerator/sample-dataset/transactions.csv", \
"source_bq_table": "", \
"bq_dataset_name": "", \
"transactions_table_name": "transactions", \
"features_table_name": "features", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
}'
