#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=[CLV_REPO_NAME],\
_BASE_IMAGE=[LIGHTWEIGHT_COMPONENT_BASE_IMAGE_NAME],\
_AUTOML_TABLES_IMAGE=[AUTOML_TABLES_IMAGE_NAME],\
_TRAIN_PIPELINE=[TRAINING_PIPELINE_NAME],\
_PREDICT_PIPELINE=[BATCH_PREDICT_PIPELINE_NAME],\
_BUCKET_NAME=[DEPLOYMENT_BUCKET_NAME],\
_PIPELINES_FOLDER=[COMPILED_PIPELINES_FOLDER],\
_ARTIFACTS_FOLDER=[TEMPLATES_FOLDER],\
_SAMPLE_DATASET_FOLDER=[SAMPLE_DATASET_FOLDER]

gcloud builds submit --no-source --config ../CLVPipelines/cloud-build/cloudbuild.yaml \
--substitutions $SUBSTITUTIONS




