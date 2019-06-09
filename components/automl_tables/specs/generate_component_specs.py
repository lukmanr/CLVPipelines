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

import fire

from pathlib import Path
from jinja2 import Environment, FileSystemLoader


def generate_specs(image_name, templates_folder='.'):
  """Generates component specs from jinja templates."""

  loader = FileSystemLoader('.')
  env = Environment(loader=loader)

  for template_path in Path(templates_folder).glob('aml-*/component.jinja'):
    spec = env.get_template(str(template_path)).render(image_name=image_name)
    Path(template_path.parent).joinpath('component.yaml').write_text(spec)
    

if __name__ == "__main__":
  fire.Fire(generate_specs)