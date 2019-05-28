#!/bin/bash

python3 run_pipeline.py \
--port 8082 \
--experiment CLV_TRAIN_BQ \
--run-name TESTING_RUN \
--pipeline_file ../compiled/clv_train_bq.tar.gz \
--arguments '{\
"project_id": "sandbox-235500", \
"source_gcs_path": "gs://clv-testing/transactions/transactions.csv", \
"bq_dataset_name": "clv_dataset", \
"query_template_uri": "gs://clv-testing/scripts/create_features_and_label_template.sql", \
"aml_dataset_name": "clv_features", \
"model_name": "clv_regression", \
"train_budget": 1000, \
"features_to_exclude": "customer_id", \
"mae_threshold": 990 \
}'
