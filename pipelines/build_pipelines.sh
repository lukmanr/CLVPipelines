#!/bin/bash

dsl-compile --py src/train-bigquery-aml/train_bq_aml.py --output clv_train_bq_automl.tar.gz
dsl-compile --py src/train-dataproc-aml/train_dataproc_aml.py --output clv_train_dataproc.tar.gz

if [[ $1 == "" ]]; then
    bucket="gs://clv-pipelines/scripts"
else
    bucket="$1"
fi


gsutil cp src/train-bigquery-aml/create_features_template.sql "${bucket}"
gsutil cp src/train-dataproc-aml/create_features.py "${bucket}"
