FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl 

RUN mkdir /ml

WORKDIR /ml

COPY src/import_dataset.py /ml

ENTRYPOINT ["bash"]