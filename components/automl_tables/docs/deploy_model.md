## Deploy Model
### Intended use
Use the component to deplay a trained AutoML Tables model for online predictions.
### Runtime arguments
|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|model_full_id|The full ID of a trained AutoML Tables model|String|No||

### Output

|Name|Description|Type|
|----|-----------|----|
|output_deployment|The status of the deployment. Currently, the component returns one of two values: "New deployment created" or "Model already deployed"|String|

### Description
The component is a wrapper around `AutoMlClient.deploy_model()` API. 
