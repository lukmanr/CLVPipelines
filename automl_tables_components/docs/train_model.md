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


### Output

|Name|Description|Type|
|----|-----------|----|
|project_id|GCP Project ID. This is a pass-through of the input project_id|GCPProjectID|
|output_dataset_id|The ID of the created AutoML Tables Dataset|String|
|output_location|The region where the AutoML Tables Dataset was created.|String|

### Description
The component is a wrapper around `AutoMlClient.create_dataset()` API. Currently, the component does not allow you to configure the schema of the target AutoML Tables Dataset. The component uses schema auto-detection.
