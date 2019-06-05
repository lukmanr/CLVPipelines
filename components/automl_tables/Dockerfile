FROM python:3.6-slim-jessie

RUN pip install  google-cloud-storage google-cloud-automl grpcio fire

RUN mkdir /ml
RUN mkdir /ml/batch_predict /ml/deploy_model /ml/import_dataset /ml/launcher /ml/train_model /ml/log_regression_metrics

WORKDIR /ml

COPY src/import_dataset/* /ml/import_dataset/
COPY src/train_model/* /ml/train_model/
COPY src/deploy_model/* /ml/deploy_model/
COPY src/batch_predict/* /ml/batch_predict/
COPY src/log_regression_metrics/* /ml/log_regression_metrics/
COPY src/launcher/* /ml/launcher/

ENTRYPOINT ["python", "-u", "-m", "launcher"]