#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=jarokaz/CLVPipelines,\
_CLUSTER=jkk8s-3,\
_ZONE=us-central1-a

gcloud builds submit --no-source --config cloudbuild.yaml \
--substitutions $SUBSTITUTIONS




