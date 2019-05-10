FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl google-cloud-bigquery

RUN mkdir /ml

WORKDIR /ml

COPY prep_data/src/prep.py /ml
COPY prep_data/src/preprocess.sql /ml
COPY prep_data/src/create_features.sql /ml

ENTRYPOINT ["bash"]