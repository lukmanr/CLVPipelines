#!/bin/bash

python3 ../src/batch_predict.py \
--project-id=sandbox-235500 \
--region=us-central1 \
--model-id=TBL403503175207747584 \
--datasource=gs://clv-testing/features/part-00000-eaa03287-5d54-45e3-b547-e1488db2d42b-c000.csv,gs://clv-testing/features/part-00001-eaa03287-5d54-45e3-b547-e1488db2d42b-c000.csv,gs://clv-testing/features/part-00002-eaa03287-5d54-45e3-b547-e1488db2d42b-c000.csv \
--destination=bq://sandbox-235500 \
--output=outputs/metadata.txt \
--key_file=key.json 

#python3 ../src/batch_predict.py \
#--project-id=sandbox-235500 \
#--region=us-central1 \
#--model-id=TBL403503175207747584 \
#--datasource=gs://clv-testing/test-features/features.csv \
#--output=gs://clv-testing/predictions 
#--key_file=key.json \