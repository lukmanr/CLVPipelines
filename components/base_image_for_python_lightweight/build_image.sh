#!/bin/bash

if [ "$1" == ""]; then
    repo = "clv-pipelines"
else
    repo = "$1"

image_name=gcr.io/$repo/base-image
image_tag=latest
full_image_name=${image_name}:${image_tag}

echo $full_image_name

#docker build -t "${full_image_name}" .
#docker push "${full_image_name}" 
