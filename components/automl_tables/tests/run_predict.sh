#!/bin/bash

python3 ../src/batch_predict.py \
--project-id=sandbox-235500 \
--region=us-central1 \
--model-id=TBL403503175207747584 \
--datasource=bq://sandbox-235500.clv_dataset.test_features \
--output=bq://sandbox-235500 
#--key_file=key.json \

#python3 ../src/batch_predict.py \
#--project-id=sandbox-235500 \
#--region=us-central1 \
#--model-id=TBL403503175207747584 \
#--datasource=gs://clv-testing/test-features/features.csv \
#--output=gs://clv-testing/predictions 
#--key_file=key.json \