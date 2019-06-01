#!/bin/bash

python3 ../src/train_model.py \
--project-id=sandbox-235500 \
--location=us-central1 \
--dataset-id=TBL88 \
--model-name="test model" \
--train-budget=1000 \
--optimization-objective=MIMINIZE_MAE \
--target-name=target_monetary \
--features-to-exclude=customer_id \
--output-model-full-id='outputs/model_full_id.txt' \
