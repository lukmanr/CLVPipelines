This folder contains Dockerfile that defines a base image used by Lightweight Python components used in some of the tutorial's pipelines. 

To build the image use `build_image.sh`. The script builds and pushes the image to `gcr.io/clv-pipelines`  as `gcr.io/clv-pipelines/base-image:latest`.

`gcr.io/clv-pipelines` is a container registry with public visibilty - created to manage pre-build images for the tutorial.

If you want to push the image to a different registry pass the new full image name as a parameter to the script.

