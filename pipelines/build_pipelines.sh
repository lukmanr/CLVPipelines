#!/bin/bash


# Currently KFP compiler does not support relative paths for load_component_from_path function
# As a workaround we will copy the latest YAML files to the same directory as pipeline at every
# build.
#
# Eventually YAML specs will be moved to a public repo and referenced using load_component_from_url
#
cp ../components/automl_tables/import_dataset/aml-import-dataset.yaml .
cp ../components/automl_tables/train_model/aml-train-model.yaml .
cp ../components/automl_tables/retrieve_regression_metrics/aml-retrieve-regression-metrics.yaml .
cp ../components/automl_tables/deploy_model/aml-deploy-model.yaml .

# Compile the pipelines
dsl-compile --py src/train-bigquery-aml/train_bq_aml.py --output clv_train_bq_automl.tar.gz
dsl-compile --py src/train-dataproc-aml/train_dataproc_aml.py --output clv_train_dataproc.tar.gz

rm aml-import-dataset.yaml 
rm aml-train-model.yaml 
rm aml-retrieve-regression-metrics.yaml 
rm aml-deploy-model.yaml 