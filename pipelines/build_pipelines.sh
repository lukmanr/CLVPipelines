#!/bin/bash


# Currently KFP compiler does not support relative paths for load_component_from_path function
# As a workaround we will copy the latest YAML files to the same directory as pipeline at every
# build.
#
# Eventually YAML specs will be moved to a public repo and referenced using load_component_from_url
#
cp ../components/automl_tables/specs/*.yaml .

# Compile the pipelines
dsl-compile --py src/train-bigquery/train_bq.py --output compiled/clv_train_bq.tar.gz
dsl-compile --py src/train-dataproc/train_dataproc.py --output compiled/clv_train.tar.gz
dsl-compile --py src/batch-predict/batch_predict.py --output compiled/clv_batch_predict.tar.gz

rm *.yaml