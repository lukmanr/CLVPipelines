#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=jarokaz/CLVPipelines,\
_BASE_IMAGE=base_image,\
_AUTOML_TABLES_IMAGE=automl_tables,\
_TAG=latest,\
_TRAIN_PIPELINE=train_pipeline,\
_PREDICT_PIPELINE=predict_pipeline,\
_BUCKET_NAME=jktest4clv,\
_ARTIFACTS_FOLDER=artifacts

gcloud builds submit --no-source --config sandbox.yaml \
--substitutions $SUBSTITUTIONS




