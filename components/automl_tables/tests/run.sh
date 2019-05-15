#!/bin/bash

python prep.py --project-id=sandbox-235500 --dataset-id=CLVDataset --transactions-table-id='sandbox-235500.CLVDataset.transactions'  --features-table-name=features  --threshold-date='2011-08-08' --predict-end='2011-12-12' --max-monetary=15000 --output-table-id='outputs/features.txt' 

