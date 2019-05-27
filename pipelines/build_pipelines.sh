#!/bin/bash


# Currently KFP compiler does not support relative paths for load_component_from_path function
# As a workaround we will copy the latest YAML files to the same directory as pipeline at every
# build.
#
# Eventually YAML specs will be moved to a public repo and referenced using load_component_from_url
#
cp ../components/automl_tables/specs/*.yaml .

# Compile the pipelines
dsl-compile --py src/train-bigquery-pipeline/train_bq_pipeline.py --output compiled/clv_train_bq.tar.gz
dsl-compile --py src/train-dataproc-pipeline/train_dataproc_pipeline.py --output compiled/clv_train_dataproc.tar.gz
dsl-compile --py src/batch-predict-pipeline/batch_predict_pipeline.py --output compiled/clv_batch_predict.tar.gz

# Just in case remove yaml files
rm *.yaml

# Copy script to GCS
gsutil cp src/scripts/* gs://clv-testing/scripts



