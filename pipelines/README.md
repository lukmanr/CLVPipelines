This folder contains source code for two KFP Pipelines:
- Train and deploy
- Batch predict

Folder structure

- `train` - The training and deployment pipeline DSL
- `src/batch_predict_pipeline.py` - The batch predict pipeline DSL
- `src/helper_components.py` - Helper Lightweight Python components
- `src/query_template.sql.jinja` - The template for BigQuery SQL query used for data preprocessing
- `settings.yaml` - Default values for the pipelines parameters and compiler pragmas
