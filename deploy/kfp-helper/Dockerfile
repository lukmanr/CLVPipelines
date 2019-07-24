FROM google/cloud-sdk:latest

RUN apt-get -y update  && apt-get -y install python3-pip 

RUN pip3 install \ 
    Jinja2 \
    fire \
    https://storage.googleapis.com/ml-pipeline/release/0.1.23/kfp.tar.gz 

RUN apt-get install kubectl

ENTRYPOINT ["/bin/bash"]
