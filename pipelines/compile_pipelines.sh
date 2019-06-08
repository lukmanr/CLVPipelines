#!/bin/bash

dsl-compile --py src/train_pipeline.py --output clv_train.tar.gz --disable-type-check
dsl-compile --py src/batch_predict_pipeline.py --output clv_batch_predict.tar.gz --disable-type-check

