## Log Evaluation Metrics
### Intended use
Use the componet to retrieve and log the latest evaluation metrics of a trained AutoML model.
### Runtime arguments

|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|model_full_id|The full ID of a trained AutoML Tables model|String|No|
|primary_metric|The name of the primary metric to log as a pipeline metric|String|No|



### Output
The component returns the value of `primary_metric`.

### Description
The component retrieves *the latest* performance evaluation for a given trained AutoML tables model and writes it as a KFP Markdown artifact. The artifact can be inspected in the KFP UI. Currently, only the regression evaluation metrics are supported. 

The component also retrieves the value of a metric which name is passed in the `primary_metric` argument and logs it a a pipeline metric.
