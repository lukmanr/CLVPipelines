This folder contains source code and a definition of a hosting base image for two helper components:
- **Load transactions** - Loads input sales transactions data to a staging table in BigQuery
- **Prepare query** - Prepares a data preprocessing and feature engineering query by substituting placeholders in a Jinja2 query template with the values passed as the component's arguments.

