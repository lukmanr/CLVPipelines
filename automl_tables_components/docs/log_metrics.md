## Log Evaluation Metrics
### Intended use
Use the componet to retrieve and log (as a KFP markdown artifact) the latest evaluation metrics of a trained AutoML model.
### Runtime arguments

|Name|Description|Type|Optional|Default|
|----|-----------|----|--------|-------|
|model_full_id|The full ID of a trained AutoML Tables model|String|No||



### Output
The component does not return any outputs.

### Description
The component retrieves *the latest* performance evaluation for a given trained AutoML tables model and writes it as a KFP Markdown artificat. The artifact can be inspected in the KFP UI. Currently, only the regression evaluation metrics are supported. 
