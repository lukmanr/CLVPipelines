#!/bin/bash

python3 ../src/retrieve_regression_metrics.py \
--model-full-id "projects/165540728514/locations/us-central1/models/TBL5243746874724188160" \
--output-rmse "outputs/rmse.txt" \
--output-mae "outputs/mae.txt" \
--output-rsquared "outputs/rsquared.txt"  