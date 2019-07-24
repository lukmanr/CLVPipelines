#!/bin/bash

SUBSTITUTIONS=\
_CLV_REPO=jarokaz/CLVPipelines

gcloud builds submit --no-source --config cloudbuild.yaml \
--substitutions $SUBSTITUTIONS




