## Train Model
### Intended use
Use the component to trigger training of an AutoML Tables model.
### Runtime arguments
|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|project_id|GCP Project ID|GCPProjectID|No||
|region|AutoML Tables region. Currently, the only supported region is us=central1|String|No|us-central1|
|description|AutoML Tables Dataset description|String|No||
|dataset_id|The ID of an AutoML Tables dataset to use for training|String|No||
|model_name|The name of an AutoML Tables model|String|No||
|train_budget|AutoML Training [training budget](https://cloud.google.com/automl-tables/docs/models) in millihours|Integer|No||
|optimization_objective|AutoML Tables [optimization objective](https://cloud.google.com/automl-tables/docs/models).|String|Yes||
|primary_metric|The name of the primary performance metric to retrieve after the training completes and to return as an output|String|No|
|target_name|The name of the column to be used as the training label. If set it overwrites the value set during dataset import|Yes||
|features_to_exclude|The list of features to exclude from this training run. Should be passed as a list literal. E.g. `"[feature1, feature2]"`|Yes|No|


### Output

|Name|Description|Type|
|----|-----------|----|
|output_model_full_id|The full ID of the created AutoML Tables Model|String|
|output_primary_metric_value|The value of the primary performance metric.|Float|

### Description
The component is a wrapper around `AutoMlClient.create_dataset()` API. Currently, the component does not allow you to configure the schema of the target AutoML Tables Dataset. The component uses schema auto-detection.
