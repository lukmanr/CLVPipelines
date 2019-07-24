#FROM python:3.6-slim-jessie
FROM gcr.io/cloud-builders/gcloud-slim

RUN /builder/google-cloud-sdk/bin/gcloud -q components install kubectl
RUN pip3 install Jinja2 fire
RUN pip3 install https://storage.googleapis.com/ml-pipeline/release/0.1.24.tar.gz 

ENTRYPOINT ["/bin/bash"]
