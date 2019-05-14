#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'CLVPipelines/notebooks'))
	print(os.getcwd())
except:
	pass

#%%
import kfp
from kfp import compiler
import kfp.dsl as dsl
import kfp.gcp as gcp



#%%
QUERY_TEMPLATE_URI = 'gs://sandbox-235500/sql-templates/create_features.sql'

@dsl.pipeline(
    name='CLVTrainingPipeline',
    description='CLV Training Pipeline'
)
def clv_pipeline(
    project_id='', 
    data_source_id='',
    dest_dataset_id='', 
    dest_table_id='',
    threshold_date='',
    predict_end='',
    max_monetary=15000,
    automl_compute_region='us-central1',
    automl_dataset_name='clv_features'
):
    # Create component factories
    prepare_features_op = kfp.components.load_component(
        '/home/jupyter/CLVPipelines/components/clv-prepare-features.yaml')
    import_dataset_op = kfp.components.load_component(
        '/home/jupyter/CLVPipelines/components/clv-import-dataset.yaml')

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
    
    import_dataset_task = import_dataset_op(
        project_id=project_id,
        compute_region=automl_compute_region,
        dataset_name=automl_dataset_name,
        source_data=prepare_features_task.output
        )
   
pipeline_func = clv_pipeline
pipeline_filename = pipeline_func.__name__ + '.tar.gz'

kfp.compiler.Compiler().compile(pipeline_func, pipeline_filename) 


#%%
#Specify pipeline argument values

arguments = {
    'project_id': 'sandbox-235500',
    'data_source_id': 'sandbox-235500.CLVDataset.transactions',
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



