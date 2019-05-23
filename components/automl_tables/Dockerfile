FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl grpcio 

RUN mkdir /ml

WORKDIR /ml

COPY src/import_dataset.py /ml
COPY src/train_model.py /ml
COPY src/deploy_model.py /ml
COPY src/batch_predict.py /ml
COPY src/retrieve_regression_metrics.py /ml

ENTRYPOINT ["bash"]