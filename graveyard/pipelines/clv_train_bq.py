
#%%
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.gcp as gcp

BASE_IMAGE = 'gcr.io/sandbox-235500/automltablesbase:dev'

#%%
@kfp.dsl.python_component(name='Prepare feature engineering query', base_image=BASE_IMAGE,target_component_file='clean_op.yaml')
def prepare_feature_engineering_query(
    project_id: str,
    source_table_id: str,
    threshold_date: str,
    predict_end: str,
    max_monetary: str,
    query_template_uri: str) -> str:
    """Creates a featuer engineering query"""

    from google.cloud import storage
    import re
    
    # Read a query template from GCS
    _, bucket, blob_name = re.split("gs://|/", query_template_uri, 2)
    blob = storage.Client(project_id).get_bucket(bucket).blob(blob_name)
    query_template = blob.download_as_string().decode('utf-8')

    # Substitute placeholders in the query template
    query = query_template.format(
        data_source_id=source_table_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary
    )
    
    return query



#%%
QUERY_TEMPLATE_URI = 'gs://sandbox-235500/sql-templates/create_features.sql'

@dsl.pipeline(
    name='CLVTrainingPipeline',
    description='CLV Training Pipeline'
)
def clv_pipeline(
    project_id='', 
    source_table_id='',
    dest_dataset_id='', 
    dest_table_id='',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    automl_compute_region='us-central1',
    automl_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='3000',
    #target_name='target_monetary',
    #features_to_exclude='monetary'
):
    # Create component factories
    prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
        prepare_feature_engineering_query)
    import_dataset_op = kfp.components.load_component(
        '/home/jupyter/projects/clv_kfp/components/clv-import-dataset.yaml')
    train_model_op = kfp.components.load_component(
        '/home/jupyter/projects/clv_kfp/components/clv-train-model.yaml')

    prepare_feature_engineering_query_task = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=source_table_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=QUERY_TEMPLATE_URI)
    """ 
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=automl_compute_region,
        dataset_name=automl_dataset_name,
        source_data=prepare_features_task.output
        )

    train_model_task = train_model_op(
        project_id=project_id,
        location=automl_compute_region,
        dataset_id=import_dataset_task.output,
        model_name=model_name,
        train_budget=train_budget,
        optimization_objective='MINIMIZE_MAE',
        target_name='target_monetary',
        features_to_exclude='customer_id'
        ) 
    """

pipeline_func = clv_pipeline
pipeline_filename = pipeline_func.__name__ + '.tar.gz'

kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename) 


#%%
#Specify pipeline argument values

arguments = {
    'project_id': 'sandbox-235500',
    'source_table_id': 'sandbox-235500.CLVDataset.transactions',
    'dest_dataset_id': 'CLVDataset',
    'dest_table_id': 'test',
    'threshold_date': '2011-08-08',
    'predict_end': '2011-12-12',
    'max_monetary': '15000'
}

HOST = 'http://localhost:8082/api/v1/namespaces/kubeflow/services/ml-pipeline:8888/proxy'
EXPERIMENT_NAME = 'TEST_EXP'

client = kfp.Client(HOST)
experiment = client.create_experiment(EXPERIMENT_NAME)

#Submit a pipeline run
run_name = pipeline_func.__name__ + ' run'
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)
print(run_result)


#%%
11/4


