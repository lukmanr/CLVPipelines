#%%
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.gcp as gcp

BASE_IMAGE = 'gcr.io/sandbox-235500/automltablesbase:dev'
QUERY_TEMPLATE_URI = 'gs://sandbox-235500/sql-templates/create_features_template.sql'
BIGQUERY_COMPONENT_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/bigquery/query/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-train-model.yaml'
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

@dsl.pipeline(
    name='CLVTrainingPipeline',
    description='CLV Training Pipeline'
)
def clv_pipeline(
    project_id='', 
    source_table_id='',
    features_dataset_id='', 
    features_table_id='',
    features_dataset_location='US',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    automl_compute_region='us-central1',
    automl_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    #target_name='target_monetary',
    #features_to_exclude='monetary'
):
    # Create component factories
    prepare_feature_engineering_query_op = kfp.components.func_to_container_op(
        prepare_feature_engineering_query)
    engineer_features_op = kfp.components.load_component_from_url(BIGQUERY_COMPONENT_SPEC_URI)
    import_dataset_op = kfp.components.load_component(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component(AML_TRAIN_MODEL_SPEC_URI)

    # Define the training pipeline
    prepare_feature_engineering_query_task = prepare_feature_engineering_query_op(
        project_id=project_id,
        source_table_id=source_table_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        query_template_uri=QUERY_TEMPLATE_URI
    ).apply(gcp.use_gcp_secret('user-gcp-sa'))

    engineer_features_task = engineer_features_op(
        query=prepare_feature_engineering_query_task.output,
        project_id=project_id,
        dataset_id=features_dataset_id,
        table_id=features_table_id,
        output_gcs_path='',
        dataset_location=features_dataset_location,
        job_config=''
    ).apply(gcp.use_gcp_secret('user-gcp-sa'))

    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=automl_compute_region,
        dataset_name=automl_dataset_name,
        source_data_uri='bq://{}.{}.{}'.format(project_id, features_dataset_id, features_table_id)
    ).apply(gcp.use_gcp_secret('user-gcp-sa'))
    import_dataset_task.after(engineer_features_task)

    train_model_task = train_model_op(
        project_id=project_id,
        location=automl_compute_region,
        dataset_id=import_dataset_task.outputs['output_dataset_id'],
        model_name='test_model',
        train_budget=1000,
        optimization_objective='MINIMIZE_MAE',
        target_name='target_monetary',
        features_to_exclude='customer_id'
        )   

pipeline_func = clv_pipeline
pipeline_filename = pipeline_func.__name__ + '.tar.gz'

kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename) 


#%%
#Specify pipeline argument values

arguments = {
    'project_id': 'sandbox-235500',
    'source_table_id': 'sandbox-235500.CLVDataset.transactions',
    'features_dataset_id': 'CLVDataset',
    'features_table_id': 'clv_features',
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
