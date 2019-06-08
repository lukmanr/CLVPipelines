FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl grpcio fire

RUN pip install https://storage.googleapis.com/ml-pipeline/release/0.1.21/kfp.tar.gz --upgrade

ENTRYPOINT ["/bin/bash"]
