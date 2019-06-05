#!/bin/bash

#python3 -m launcher batch_predict predict \
#--project-id=sandbox-235500 \
#--region=us-central1 \
#--model-id=TBL1359603302349668352 \
#--datasource='gs://clv-testing/features/part-0.csv,gs://clv-testing/features/part-1.csv,gs://clv-testing/features/part-2.csv' \
#--destination_prefix=bq://sandbox-235500 \
#--output-destination=outputs/metadata.txt \

#python3 -m launcher batch_predict predict \
#--project-id=sandbox-235500 \
#--region=us-central1 \
#--model-id=TBL1359603302349668352 \
#--datasource='bq://sandbox-235500.clv_dataset.features' \
#--destination_prefix=bq://sandbox-235500 \
#--output_destination=outputs/metadata.txt  


python3 -m launcher batch_predict predict \
--project-id=sandbox-235500 \
--region=us-central1 \
--model-id=TBL1359603302349668352 \
--datasource='bq://sandbox-235500.clv_dataset.features' \
--destination_prefix='gs://clv-testing/clv-predictions' \
--output_destination=outputs/metadata.txt  