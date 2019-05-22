#!/bin/bash

dsl-compile --py src/train-bigquery-aml/train_bq_aml.py --output clv_train_bq_automl.tar.gz
dsl-compile --py src/train-dataproc-aml/train_dataproc_aml.py --output clv_train_dataproc.tar.gz

