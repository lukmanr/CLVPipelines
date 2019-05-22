FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl grpcio 

RUN mkdir /ml

WORKDIR /ml

COPY src/import_dataset.py /ml
COPY src/train_model.py /ml

ENTRYPOINT ["bash"]