#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=jarokaz/CLVPipelines,\
_BASE_IMAGE=base_image,\
_AUTOML_TABLES_IMAGE=automl_tables,\
_TAG=latest,\
_TRAIN_PIPELINE=train_pipeline,\
_PREDICT_PIPELINE=predict_pipeline,\
_BUCKET_NAME=jktest4clv,\
_PIPELINES_FOLDER=pipelines,\
_ARTIFACTS_FOLDER=artifacts,\
_SAMPLE_DATASET_FOLDER=dataset

gcloud builds submit --no-source --config cloudbuild.yaml \
--substitutions $SUBSTITUTIONS




