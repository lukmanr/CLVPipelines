#!/bin/bash

if [ "$1" == "" ]; then
    full_image_name="gcr.io/clv-pipelines/base-image:latest"
else
    full_image_name="$1"
fi

echo $full_image_name

docker build -t "${full_image_name}" .
docker push "${full_image_name}" 
