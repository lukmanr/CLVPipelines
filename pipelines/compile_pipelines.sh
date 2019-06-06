#!/bin/bash

dsl-compile --py src/train_pipeline.py --output compiled/train_pipeline.tar.gz --disable-type-check
dsl-compile --py src/batch_predict_pipeline.py --output compiled/batch_predict_pipeline.tar.gz --disable-type-check