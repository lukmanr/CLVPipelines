FROM python:3.6-slim-jessie

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && \
    curl https://packages.cloud.google.com/apt/doc/apt-key.gpg |  apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - && \
    update -y && apt-get install google-cloud-sdk

RUN pip3 install \ 
    Jinja2 \
    fire \
    https://storage.googleapis.com/ml-pipeline/release/0.1.24.tar.gz 

RUN /builder/google-cloud-sdk/bin/gcloud -q components install kubectl

ENTRYPOINT ["/bin/bash"]
