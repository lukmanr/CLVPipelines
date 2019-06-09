#!/bin/bash

python configure_compiler_directives.py src/config.py.jinja src/config.py \
'{"local_search_paths": ["../components/automl_tables/specs"], \
  "url_search_prefixes": ["https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/"], \
  "use_sa_secret": True \
}'
