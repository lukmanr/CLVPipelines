This folder contains source code for two KFP Pipelines:
- Train and deploy
- Batch predict

Folder content

- `train_pipeline.oy` - The training and deployment pipeline DSL
- `batch_predict.py` - The batch predict pipeline DSL
- `helper_components` - Utility components used by the pipelines. Implemented as KFP Lightweight Python components
- `artificats/query_template.sql.jinja` - The template for BigQuery SQL query used for data preprocessing
- `settings.yaml` - Default values for the pipelines parameters and compiler pragmas
