#!/bin/bash

python run_pipeline.py \
--host http://localhost:8082 \
--experiment "CLV batch predit" \
--run-name "Batch predict run" \
--pipeline_file clv_predict.tar.gz \
--arguments '{\
"project_id": "clv-prod", \
"source_gcs_path": "gs://clv-accelerator/sample-dataset/transactions.csv", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
"aml_model_id": "TBL8408686697230893056", \
"destination_prefix": "bq://clv-dev", \
}'
