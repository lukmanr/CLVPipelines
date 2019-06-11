This folder contains source code for the tutorial's pipelines.

- `src/train_pipeline.py` - The training and deployment pipeline DSL
- `src/batch_predict_pipeline.py` - The batch predict pipeline DSL
- `src/helper_components.py` - Helper Lightweight Python components
- `src/query_template.sql.jinja` - The template for BigQuery SQL query used for data preprocessing
- `settings.yaml` - Default values for the pipelines parameters and compiler pragmas
- `update_pipeline_settings.py` - a utility script used by Cloud Build to dynamically update `settings.yaml`

