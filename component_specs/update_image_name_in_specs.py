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
"""This module is a command line utility to generate component specs from jinja templates"""

import pathlib
import fire
import yaml


def update_image_name(folder, image):
  """Updates component specifications with a container image name."""

  for spec_path in pathlib.Path(folder).glob('*'):
    spec = pathlib.Path(spec_path).joinpath('component.yaml').read_text()
    spec = yaml.safe_load(spec)
    spec['implementation']['container']['image'] = image
    pathlib.Path(spec_path).joinpath('component.yaml').write_text(yaml.dump(spec))

if __name__ == '__main__':
  fire.Fire(update_image_name)