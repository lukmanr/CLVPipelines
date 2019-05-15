#%%
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.gcp as gcp



#%%
BASE_IMAGE = 'gcr.io/sandbox-235500/automltablesbase:dev'
QUERY_TEMPLATE_URI = 'gs://sandbox-235500/sql-templates/create_features.sql'
BIGQUERY_COMPONENT_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/3b938d664de35db9401c6d198439394a9fca95fa/components/gcp/bigquery/query/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-train-model.yaml'


@dsl.pipeline(
    name='CLVTrainingPipeline',
    description='CLV Training Pipeline'
)
def clv_pipeline(
    project_id='', 
    source_data_uri='',
    dest_dataset_id='', 
    dest_table_id='',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    automl_compute_region='us-central1',
    automl_dataset_name='clv_features'
):
    import_dataset_op = kfp.components.load_component(AML_IMPORT_DATASET_SPEC_URI)
    train_model_op = kfp.components.load_component(AML_TRAIN_MODEL_SPEC_URI)

    """    
    prepare_features_task = prepare_features_op(
        project_id=project_id,
        data_source_id=data_source_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary,
        dest_dataset_id=dest_dataset_id,
        dest_table_id=dest_table_id,
        query_template_uri=QUERY_TEMPLATE_URI
        )

    """
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=automl_compute_region,
        dataset_name=automl_dataset_name,
        source_data_uri=source_data_uri
        )

  
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
    'source_data_uri': 'bq://sandbox-235500.CLVDataset.transactions',
    'dest_dataset_id': 'CLVDataset',
    'dest_table_id': 'features',
    'threshold_date': '2011-08-08',
    'predict_end': '2011-12-12'
}


HOST = 'http://localhost:8082/api/v1/namespaces/kubeflow/services/ml-pipeline:8888/proxy'
EXPERIMENT_NAME = 'TEST'

client = kfp.Client(HOST)
experiment = client.create_experiment(EXPERIMENT_NAME)

#Submit a pipeline run
run_name = pipeline_func.__name__ + ' run'
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)
print(run_result)
