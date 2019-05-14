#!/bin/bash

image_name=gcr.io/sandbox-235500/clv-components
image_tag=latest
full_image_name=${image_name}:${image_tag}


docker run --entrypoint python  "${full_image_name}" prep.py --project-id=sandbox-235500 --dataset-id=CLVDataset --transactions-table-id='sandbox-235500.CLVDataset.transactions'  --features-table-name=features  --threshold-date='2011-08-08' --predict-end='2011-12-12' --max-monetary=15000 --output-table-id='outputs/features.txt' 

