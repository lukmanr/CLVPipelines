# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fire
import importlib
import sys
import logging


def launch(module_path, args):
    """Launches a python file or module as a command entrypoint.
    Args:
        module: A module path.
        args: The function to invoke and its args.
    Returns:
        The return value from the launched function.
    """

    try:
        module = importlib.import_module(module_path)
    except Exception:
      logging.error('Failed to find the module: {}'.format(module_path))
      sys.exit(1)

    return fire.Fire(module, command=args, name=module.__name__)


