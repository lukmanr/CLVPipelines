#!/bin/bash


# Currently KFP compiler does not support relative paths for load_component_from_path function
# As a workaround we will copy the latest YAML files to the same directory as pipeline at every
# build.
#
# Eventually YAML specs will be moved to a public repo and referenced using load_component_from_url
#
#cp ../components/automl_tables/specs/*.yaml .

# Compile the pipelines
# dsl-compile --py src/train_pipeline.py --output compiled/clv_train.tar.gz --disable-type-check
# dsl-compile --py src/batch_predict_pipeline.py --output compiled/clv_batch_predict.tar.gz --disable-type-check

# Just in case remove yaml files
#rm *.yaml

# Copy script to GCS
#gsutil cp src/scripts/* gs://clv-testing/scripts



python src/batch_predict_pipeline.py --output-dir=compiled --local-search-paths='/Users/jarekk/projects/CLVPipelines/components/specs' --url-search-prefixes='https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/'
python src/train_pipeline.py --output-dir=compiled --local-search-paths='/Users/jarekk/projects/CLVPipelines/components/specs' --url-search-prefixes='https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/'


