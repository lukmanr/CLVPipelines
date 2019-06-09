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


def generate_specs(image_name, templates_folder='templates', specs_folder='specs'):
  """Generates component specs from jinja templates."""

  loader = FileSystemLoader(templates_folder)
  env = Environment(loader=loader)

  for template_path in Path(templates_folder).glob('*'):
    spec = env.get_template(str(template_path.name)).render(image_name=image_name)
    Path(specs_folder).joinpath(template_path.stem).mkdir(parents=True, exist_ok=True)
    Path(specs_folder).joinpath(template_path.stem, 'component.yaml').write_text(spec)

    

if __name__ == "__main__":
  fire.Fire(generate_specs)