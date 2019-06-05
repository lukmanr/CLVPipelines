import logging
import argparse
import launcher

def main():

    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        prog='launcher',
        description='Launch a python module or file.')
    parser.add_argument('module', type=str,
        help='Either a python file path or a module name.')
    parser.add_argument('args', nargs=argparse.REMAINDER)
    args = parser.parse_args()

    launcher.launch(args.module, args.args)

if __name__ == '__main__':
    main()