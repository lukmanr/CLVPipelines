#Copyright 2019 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import kfp
import argparse
import logging

BASE_IMAGE = 'gcr.io/sandbox-235500/automltablesbase:dev'

@kfp.dsl.python_component(name='Create features', base_image=BASE_IMAGE)
def prepare_features(
    project_id: str,
    data_source_id: str,
    threshold_date: str,
    predict_end: str,
    max_monetary: str,
    dest_dataset_id: str,
    dest_table_id: str,
    query_template_uri: str) -> str:
    """Creates training features from sales transactions BQ table"""

    import logging
    import re
    import uuid
    from google.cloud import bigquery
    from google.cloud import storage

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    def load_query_template(project_id, query_template_uri):
        """Loads a query template from a GCS bucket""" 

        _, bucket, blob_name = re.split("gs://|/", query_template_uri, 2)
        blob = storage.Client(project_id).get_bucket(bucket).blob(blob_name)
        query_template = blob.download_as_string().decode('utf-8')

        return query_template

    # Load the query template and finalize the query
    query_template = str(load_query_template(project_id, query_template_uri))
    query = query_template.format(
        data_source_id=data_source_id,
        threshold_date=threshold_date,
        predict_end=predict_end,
        max_monetary=max_monetary
    )

    # Configure query job
    client = bigquery.Client(project=project_id)
    # If destination table not passed create a unique table id 
    if not dest_table_id:
        dest_table_id = 'output_{}'.format(uuid.uuid4().hex)
    # Configure BQ to write an output to a destination table
    job_config = bigquery.QueryJobConfig(
        destination=client.dataset(dest_dataset_id).table(dest_table_id),
        create_disposition=bigquery.job.CreateDisposition.CREATE_IF_NEEDED,
        write_disposition=bigquery.job.WriteDisposition.WRITE_TRUNCATE)
        
    # Execute the query and wait for the query to finish
    logging.info("Starting feature processing using {} as source".format(data_source_id))
    client.query(query, job_config).result()
    dest_uri = "bq://{}.{}.{}".format(project_id, dest_dataset_id, dest_table_id)
    logging.info("Feature processing completed. Features stored in: {}".format(dest_uri))
    
    # Return the URI of the destination table
    return dest_uri


def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--container-registry',
        type=str,
        #required=True,
        default='sandbox-235500',
        help='The GCP container registry for the target image.')
    parser.add_argument(
        '--gcs-staging-path',
        type=str,
        #required=True,
        default='gs://sandbox-235500/staging',
        help='The GCS path for the staging area used by Kaniko')
 
    return parser.parse_args()


def main():
    """Build KFP BigQuery components"""

    args = _parse_arguments()

    kfp.compiler.build_python_component(
        component_func=prepare_features,
        staging_gcs_path=args.gcs_staging_path,
        target_component_file='clv-prepare-features.yaml',
        target_image='gcr.io/{}/clv-prepare-features:latest'.format(args.container_registry))


if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
    