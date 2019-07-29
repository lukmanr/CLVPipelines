## Train Model
### Intended use
Use the component to trigger training of an AutoML Tables model.
### Runtime arguments
|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|project_id|GCP Project ID|GCPProjectID|No||
|region|AutoML Tables region. Currently, the only supported region is us=central1|String|No|us-central1|
|dataset_id|The ID of an AutoML Tables dataset to use for training|String|No||
|model_name|The name of an AutoML Tables model|String|No||
|train_budget|AutoML Training [training budget](https://cloud.google.com/automl-tables/docs/models) in millihours|Integer|No||
|optimization_objective|AutoML Tables [optimization objective](https://cloud.google.com/automl-tables/docs/models).|String|Yes||
|target_name|The name of the column to be used as the training label. If set it overwrites the value set during dataset import|Yes||
|features_to_exclude|The list of features to exclude from this training run. Should be passed as a list literal string. E.g. `"[feature1, feature2]"`|Yes|No|


### Output

|Name|Description|Type|
|----|-----------|----|
|output_model_full_id|The full ID of the created AutoML Tables Model|String|
|output_primary_metric_value|The value of the primary performance metric.|Float|

### Description
The component is a wrapper around `AutoMlClient.create_model()` API. If the target colummn's type is Categorical, AutoML Tables trains a classification model. If the target column's type is Numeric, AutoML Tables trains a regression model. Make sure to set `optimization_objective` and `primary_metric` parameters to match [the machine learning problem](https://cloud.google.com/automl-tables/docs/problem-types).
