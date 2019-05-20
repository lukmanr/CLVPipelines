# Copyright 2019 Google Inc. All Rights Reserved.
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

import re
import argparse
import logging
from pathlib import Path
from google.cloud import automl_v1beta1 as automl


def main():
    project_id="sandbox-235500"
    location="us-central1"
    dataset_id="TBL2470444297938272256"

    client = automl.AutoMlClient()

    """
    # Retrieve a table spec for the primary table
    dataset_path = client.dataset_path(project_id, location, dataset_id)
    dataset_ref = client.get_dataset(dataset_path)
    primary_table_spec_id = dataset_ref.tables_dataset_metadata.primary_table_spec_id
    # Filtering does not seem to work so scan through all table_specs
    table_specs = client.list_table_specs(parent=dataset_path)
    primary_table_spec = [table_spec for table_spec in table_specs if 
        re.fullmatch('.*%s' % primary_table_spec_id, table_spec.name)][0]
 
    print(primary_table_spec.name)
    """

    name = "projects/165540728514/locations/us-central1/datasets/TBL2470444297938272256/tableSpecs/3589826299851440128"

    print(name)
 
    dataset_path = client.dataset_path(project_id, location, dataset_id)

    dataset_ref = client.get_dataset(dataset_path)
    primary_table_path = client.table_spec_path(
            project_id,
            location,
            dataset_id,
            dataset_ref.tables_dataset_metadata.primary_table_spec_id)

    print(primary_table_path)

    name = primary_table_path

    # Retrieve column specs for the primary table
    column_specs = client.list_column_specs(name)
    for spec in column_specs:
        print(spec.name)
 



if __name__ == '__main__':
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)
    main()
    
    