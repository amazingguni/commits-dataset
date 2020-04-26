import sys
from pathlib import Path
import random
import constants
from tqdm import tqdm

def main(path):
    cnt = 0
    for path in  Path(path).glob('*.target'):
        print(path)
        with open(path) as f:
            single_targets = [line.strip() for line in f.readlines() if line.strip() and len(line.strip().split())==1]
            print('\n'.join(single_targets))
            cnt += len(single_targets)


    print(cnt)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Split commit message dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains filtered dataset')
    args = parser.parse_args()
    main(args.path)