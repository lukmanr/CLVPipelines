if [[ $1 == "" ]]; then
    bucket="gs://clv-pipelines/specs"
else
    bucket="$1"
fi


gsutil cp batch_predict/aml-batch-predict.yaml "${bucket}"
gsutil cp deploy_model/aml-deploy-model.yaml "${bucket}"
gsutil cp import_dataset/aml-import-dataset.yaml "${bucket}"
gsutil cp log_metrics/aml-log-metrics.yaml "${bucket}"
gsutil cp train_model/aml-train-model.yaml "${bucket}"

