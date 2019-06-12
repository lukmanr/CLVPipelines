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
"""This module is a command line utility to update image name in automl component specs"""

import pathlib
import fire
import yaml


def update_image_name(spec_folder, image_name):
  """Updates component specifications with a new container image name."""

  for spec_path in pathlib.Path(spec_folder).glob('*/component.yaml'):
    spec = yaml.safe_load(pathlib.Path(spec_path).read_text())
    spec['implementation']['container']['image'] = image_name
    pathlib.Path(spec_path).write_text(yaml.dump(spec))


if __name__ == '__main__':
  fire.Fire(update_image_name)
