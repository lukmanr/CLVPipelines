#!/bin/bash

if [[ $1 == "" ]]; then
    full_image_name="gcr.io/clv-pipelines/automl-tables-component:latest"
else
    full_image_name="$1"
fi

docker build -t "${full_image_name}" .
docker push "${full_image_name}" 

if [[ $1 == "" || ( $S1 != "" && $S2 == "" ) ]]; then
    bucket="gs://clv-pipelines/specs"
else
    bucket="$2"
fi


gsutil cp ../batch_predict/aml-batch-predict.yaml "${bucket}"
gsutil cp ../deploy_model/aml-deploy-model.yaml "${bucket}"
gsutil cp ../import_dataset/aml-import-dataset.yaml "${bucket}"
gsutil cp ../log_metrics/aml-log-metrics.yaml "${bucket}"

