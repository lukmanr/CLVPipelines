#!/bin/bash

if [[ $1 == "" ]]; then
    full_image_name="gcr.io/clv-pipelines/automl-tables-component:latest"
else
    full_image_name="$1"
fi

docker build -t "${full_image_name}" .
docker push "${full_image_name}" 
