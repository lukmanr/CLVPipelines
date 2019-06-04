#!/bin/bash



local_search_paths='["/Users/jarekk/projects/CLVPipelines/components/specs"]' 
url_search_prefixes='["https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/"]'


python src/batch_predict_pipeline.py --output-dir=compiled --local-search-paths=${local_search_paths} --url-search-prefixes=${url_search_prefixes}
python src/train_pipeline.py --output-dir=compiled --local-search-paths=${local_search_paths} --url-search-prefixes=${url_search_prefixes}


