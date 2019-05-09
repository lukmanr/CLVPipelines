#!/bin/bash

python prep.py --project-id=sandbox-235500 --input-dataset-id=CLVDataset --transactions-table-id=transactions --output-dataset-id=CLVDataset --features-table-id=features --threshold-date='2011-08-08' --predict-end='2011-12-12' --max-monetary=15000 