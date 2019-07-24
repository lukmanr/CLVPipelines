FROM google/cloud-sdk:slim

RUN apt-get update -y && apt-get install python3-pip 

RUN pip3 install \ 
    Jinja2 \
    fire \
    https://storage.googleapis.com/ml-pipeline/release/0.1.23.tar.gz 

RUN gcloud -q components install kubectl

ENTRYPOINT ["/bin/bash"]
