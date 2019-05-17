import argparse


def _parse_arguments():
    """Parse command line arguments"""
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--max-monetary',
        type=str,
        default=15000,
        help='Maximum monetary value.') 
    parser.add_argument(
        '--max-partitions',
        type=int,
        default=8,
        help='Maximum number of partitions.') 
    return parser.parse_args()

if __name__ == '__main__':
    args=_parse_arguments()

    print(args.max_monetary)
    print(args.max_partitions)