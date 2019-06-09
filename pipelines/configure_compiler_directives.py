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
from jinja2 import Template


def configure_compiler_directives(config_template, config_py, directives):
  """Generates config.py that configures KFP compilation behaviour"""

  template = Template(Path(config_template).read_text())
  compiler_directives = template.render(directives)
  Path(config_py).parent.mkdir(parents=True, exist_ok=True)
  Path(config_py).write_text(compiler_directives)

if __name__ == "__main__":
  fire.Fire(configure_compiler_directives)