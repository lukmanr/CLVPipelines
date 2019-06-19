#!/bin/bash

python -m launcher log_evaluation_metrics log_metrics \
--model-full-id "projects/928933997278/locations/us-central1/models/TBL3785741679735078912" \
--primary-metric "mean_absolute_error"