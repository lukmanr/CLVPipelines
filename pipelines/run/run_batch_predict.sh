#!/bin/bash

#python3 run_pip
#--host https://jkkf.endpoints.sandbox-235500.cloud.goog/pipeline \
#--client_id 165540728514-vdmfatc4jdch6bkuvsfcd0opfd5bipg6.apps.googleusercontent.com \
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
--host https://jkkf.endpoints.sandbox-235500.cloud.goog/pipeline \
--client_id 165540728514-vdmfatc4jdch6bkuvsfcd0opfd5bipg6.apps.googleusercontent.com \
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
"aml_model_id": "TBL8120491505451270144", \
"destination_prefix": "bq://sandbox-235500", \
"query_template_uri": "gs://clv-testing/scripts/create_features_template.sql" \
}'
