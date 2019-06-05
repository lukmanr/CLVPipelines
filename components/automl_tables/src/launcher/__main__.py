import argparse
import logging
import importlib
import sys
import fire
import launcher

def main():

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        prog='launcher',
        description='Launch a python module or file.')
    parser.add_argument('file_or_module', type=str,
        help='Either a python file path or a module name.')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    launcher.launch(args.file_or_module, args.args)

if __name__ == '__main__':
    main()