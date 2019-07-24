FROM gcr.io/cloud-builders/gcloud-slim

RUN apt-get -y update && \
    apt-get -y install python3.6

RUN pip3 install \ 
    Jinja2 \
    fire \
    https://storage.googleapis.com/ml-pipeline/release/0.1.24.tar.gz 

RUN /builder/google-cloud-sdk/bin/gcloud -q components install kubectl

ENTRYPOINT ["/bin/bash"]
