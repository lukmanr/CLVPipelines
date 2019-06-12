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
"""This module is a command line utility to update the pipeline settings file"""

import pathlib
import fire
import yaml


def update_pipeline_settings(settings_file, **new_settings):
  """Updates pipeline settings file."""

  settings = yaml.safe_load(pathlib.Path(settings_file).read_text())
  for key, value in new_settings.items():
    settings['settings'][key] = value
  pathlib.Path(settings_file).write_text(yaml.dump(settings))

if __name__ == '__main__':
  fire.Fire(update_pipeline_settings)