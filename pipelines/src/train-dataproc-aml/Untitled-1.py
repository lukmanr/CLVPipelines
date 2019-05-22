#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'pipelines/dataproc-aml'))
	print(os.getcwd())
except:
	pass
#%% [markdown]
# # Orchestrating BigQuery and AutoML Tables using Kubeflow Pipelines.
# This notebook demonstrates how to implement and execute a Kubeflow pipline that uses Dataproc/Spark for data pre-processing/feature engineering and AutoML Tables for model training. 
#%% [markdown]
# ## Defining and compiling the pipeline

#%%
import kfp

CREATE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/create_cluster/component.yaml'
DELETE_DATAPROC_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/delete_cluster/component.yaml' 
SUBMIT_PYSPARK_JOB_SPEC_URI = 'https://raw.githubusercontent.com/kubeflow/pipelines/d2f5cc92a46012b9927209e2aaccab70961582dc/components/gcp/dataproc/submit_pyspark_job/component.yaml'
AML_IMPORT_DATASET_SPEC_URI = 'https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/components/automl_tables/aml-import-dataset.yaml'
AML_TRAIN_MODEL_SPEC_URI = 'https://raw.githubusercontent.com/jarokaz/CLVPipelines/master/components/automl_tables/aml-train-model.yaml'
CREATE_FEATURES_FILE_URI = 'gs://clv-pipelines-scripts/create_features.py'

@dsl.pipeline(
    name='CLV Training Pipeline - Dataproc',
    description='CLV Training Pipeline using Dataproc/Spark for data preparation'
)
def clv_pipeline_dataproc_automl(
    project_id='', 
    source_gcs_path='',
    output_gcs_path='',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    max_partitions=2,
    compute_region='us-central1',
    automl_dataset_name='clv_features',
    model_name='clv_regression',
    train_budget='1000',
    target_column_name='target_monetary',
    features_to_exclude='customer_id'
):

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
    )

    dataproc_delete_cluster_task = dataproc_delete_cluster_op(
        project_id=project_id,
        region=region,
        name=dataproc_create_cluster_task.output
    )

    dataproc_delete_cluster_task.after(dataproc_submit_pyspark_job_task)
    
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        location=region,
        dataset_name=automl_dataset_name,
        source_data_uri='bq://{}.{}.{}'.format(project_id, features_dataset_id, features_table_id)
    )
    
   


pipeline_func = clv_dataproc_pipeline
pipeline_filename = pipeline_func.__name__ + '.tar.gz'

kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename) 


#%% [markdown]
# ## Submit the pipeline for execution

#%%
arguments = {
    'project_id': 'sandbox-235500',
    'source_gcs_path': 'gs://sandbox-235500/clv_sales_transactions',
    'output_gcs_path': 'gs://sandbox-235500/clv_training_dataset',
    'threshold_date': '2011-08-08',
    'predict_end': '2011-12-12' 
}

HOST = 'http://localhost:8082'
EXPERIMENT_NAME = 'CLV_TRAINING'

client = kfp.Client(HOST)
experiment = client.create_experiment(EXPERIMENT_NAME)

run_name = pipeline_func.__name__ + ' run'
run_result = client.run_pipeline(experiment.id, run_name, pipeline_filename, arguments)


#%%



#%%



