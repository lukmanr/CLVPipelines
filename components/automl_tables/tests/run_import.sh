#!/bin/bash

python -m launcher import_dataset import_dataset \
--project-id=sandbox-235500 \
--region=us-central1 \
--dataset-name=clv_dataset \
--description="CLV Dataset" \
--source-data-uri='bq://sandbox-235500.clv_dataset.features' \
--target-column-name=target_monetary \
--weight-column-name= \
--ml-use-column-name= \
--output-project-id='outputs/project.txt' \
--output-dataset-id='outputs/dataset.txt' \
--output-location='outputs/location.txt' 
