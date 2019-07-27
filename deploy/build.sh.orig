#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=jarokaz/CLVPipelines,\
_AUTOML_TABLES_IMAGE=automl_tables,\
_BASE_IMAGE=base_image,\
_TAG=latest,\
_TRAIN_PIPELINE=train_pipeline,\
_PREDICT_PIPELINE=predict_pipeline,\
_ARTIFACTS_FOLDER=artifacts,\
_PIPELINES_FOLDER=pipelines,\
_SAMPLE_DATASET_FOLDER=dataset,\
_BUCKET_NAME=jkclv-bucket2,\
_CLUSTER_NAME=jkk8s-3,\
_ZONE=us-central1-a

gcloud builds submit --no-source --config cloudbuild.yaml \
--substitutions $SUBSTITUTIONS




