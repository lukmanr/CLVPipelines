#!/bin/bash

#python3 run_pipeline.py \
#--port 8082 \
#--experiment CLV_BATCH_PREDICT \
#--run-name TESTING_RUN \
#--pipeline_file ../compiled/clv_batch_predict.tar.gz \
#--arguments '{\
#"project_id": "sandbox-235500", \
#"source_gcs_path": "gs://clv-testing/transactions/transactions.csv", \
#"source_bq_table": "",
#"bq_dataset_name": "clv_dataset", \
#"transactions_table_name": "transactions", \
#"features_table_name": "features", \
#"predict_end": "2011-12-12", \
#"threshold_date": "2011-08-08", \
#"max_monetary": 15000, \
#"aml_model_id": "TBL1359603302349668352", \
#"destination_prefix": "bq://sandbox-235500"}'


python3 run_pipeline.py \
--port 8082 \
--experiment CLV_BATCH_PREDICT \
--run-name TESTING_RUN \
--pipeline_file ../compiled/clv_batch_predict.tar.gz \
--arguments '{\
"project_id": "sandbox-235500", \
"source_gcs_path": "", \
"source_bq_table": "sandbox-235500.source.transactions", \
"bq_dataset_name": "clv_dataset", \
"transactions_table_name": "transactions", \
"features_table_name": "features", \
"predict_end": "2011-12-12", \
"threshold_date": "2011-08-08", \
"max_monetary": 15000, \
"aml_model_id": "TBL1359603302349668352", \
"destination_prefix": "bq://sandbox-235500"}'
