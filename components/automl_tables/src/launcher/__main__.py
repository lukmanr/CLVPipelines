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
"""Launcher model default entry."""

import argparse
import logging

import launcher


def main():
  """Parses a module name and launches a corresponding module."""
  logging.basicConfig(level=logging.INFO)
  parser = argparse.ArgumentParser(
      prog='launcher', description='Launch a python module or file.')
  parser.add_argument(
      'module', type=str, help='Either a python file path or a module name.')
  parser.add_argument('args', nargs=argparse.REMAINDER)
  args = parser.parse_args()

  launcher.launch(args.module, args.args)


if __name__ == '__main__':
  main()
