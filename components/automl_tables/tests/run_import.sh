#!/bin/bash

python3 ../src/import_dataset.py \
--project-id=sandbox-235500 \
--location=us-central1 \
--dataset-name=clv_dataset \
--description="CLV Dataset" \
--source-data-uri='gs://clv-pipelines/order-summaries/part-0.csv' \
--target-column-name=target_monetary \
--weight-column-name= \
--ml-use-column-name= \
--output-project-id='outputs/project.txt' \
--output-dataset-id='outputs/dataset.txt' \
--output-location='outputs/location.txt' 
