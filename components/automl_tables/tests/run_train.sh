#!/bin/bash

python3 -m launcher train_model train \
--project-id=sandbox-235500 \
--region=us-central1 \
--dataset-id=TBL4552901728759971840 \
--model-name="test model" \
--train-budget=1000 \
--optimization-objective=MIMINIZE_MAE \
--primary-metric=mean_absolute_error \
--target-name=target_monetary \
--features-to-exclude='["customer_id"]' \
--output-model-full-id='outputs/model_full_id.txt' \
--output-primary-metric-value='outputs/primary-metric-value.txt' \
