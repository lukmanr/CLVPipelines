#%%
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.gcp as gcp

PROJECT_ID = 'sandbox-235500'
REGION = 'us-west2'
CLUSTER_NAME = 'jkspark'
EXPERIMENT_NAME = 'CLV_DATAPROC'
CREATE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/create_cluster/component.yaml'
DELETE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/delete_cluster/component.yaml' 
SUBMIT_PYSPARK_JOB_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/submit_pyspark_job/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = '/home/jupyter/projects/clv_kfp/components/automl_tables/aml-train-model.yaml'
CREATE_FEATURES_FILE_URI = 'gs://sandbox-235500/pyspark-scripts/create_features.py'

SOURCE_GCS_PATH = 'gs://sandbox-235500/clv_sales_transactions'
OUTPUT_GCS_PATH = 'gs://sandbox-235500/clv_training_dataset'

@dsl.pipeline(
    name='CLVTrainingPipelineDataproc',
    description='CLV Training Pipeline using Dataproc/Spark for data preparation'
)
def clv_dataproc_pipeline(
    project_id='', 
    region='',
    source_gcs_path='',
    output_gcs_path='',
    threshold_date='2011-08-08',
    predict_end='2011-12-12',
    max_monetary=15000,
    max_partitions=2):

    dataproc_create_cluster_op = kfp.components.load_component_from_url(CREATE_DATAPROC_SPEC_URI)    
    dataproc_delete_cluster_op = kfp.components.load_component_from_url(DELETE_DATAPROC_SPEC_URI)    
    dataproc_submit_pyspark_job_op = kfp.components.load_component_from_url(SUBMIT_PYSPARK_JOB_SPEC_URI)    

    args = ('['
        '"--source-gcs-path={}",'
        '"--output-gcs-path={}",'
        '"--threshold-date={}",'
        '"--predict-end={}",'
        '"--max-monetary={}",'
        '"--max-partitions={}",'
        ']'
    ).format(
        source_gcs_path, 
        output_gcs_path,
        threshold_date,
        predict_end,
        max_monetary,
        max_partitions)

    dataproc_create_cluster_task = dataproc_create_cluster_op(
        project_id=project_id,
        region=region,
        name='',
        name_prefix='',
        initialization_actions='',
        config_bucket='',
        image_version='',
        cluster='',
        wait_interval='30'
    ) 

    dataproc_submit_pyspark_job_task = dataproc_submit_pyspark_job_op(
        project_id=project_id,
        region=region,
        cluster_name=dataproc_create_cluster_task.output,
        main_python_file_uri = CREATE_FEATURES_FILE_URI,
        args=args,
        pyspark_job='{}',
        job='{}',
        wait_interval='30'
    ).apply(gcp.use_gcp_secret('user-gcp-sa'))

    dataproc_delete_cluster_task = dataproc_delete_cluster_op(
        project_id=project_id,
        region=region,
        name=dataproc_create_cluster_task.output
    )

    dataproc_delete_cluster_task.after(dataproc_submit_pyspark_job_task)

pipeline_func = clv_dataproc_pipeline
pipeline_filename = pipeline_func.__name__ + '.tar.gz'

kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename) 


#Specify pipeline argument values

arguments = {
    'project_id': PROJECT_ID,
    'region': REGION,
    'source_gcs_path': SOURCE_GCS_PATH,
    'output_gcs_path': OUTPUT_GCS_PATH,
    'threshold_date': '2011-08-08'
}

HOST = 'http://localhost:8082/api/v1/namespaces/kubeflow/services/ml-pipeline:8888/proxy'

client = kfp.Client(HOST)
experiment = client.create_experiment(EXPERIMENT_NAME)

#Submit a pipeline run
run_name = pipeline_func.__name__ + ' run'
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)
print(run_result)
