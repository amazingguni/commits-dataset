import sys
from pathlib import Path
import random

def is_dataset(s):
    target_ends_with = ['train.index', 'train.source', 'train.target',
    'eval.index', 'eval.source', 'eval.target',
    'test.index', 'test.source', 'test.target']
    for w in target_ends_with:
        if s.endswith(w):
            return True
    return False

def main(path):
    dataset_dir = Path(path)
    lowercase_dir = dataset_dir.parent / f'{dataset_dir.name}_lower'
    lowercase_dir.mkdir(parents=True, exist_ok=True)
    
    for path in dataset_dir.glob('*'):
        if path.is_dir():
            continue
        name = path.name
        if not is_dataset(name):
            continue
        lower_path = lowercase_dir / name
        with open(path) as f, open(lower_path, 'w') as f_out:
            f_out.write(f.read().lower())
        print(lower_path)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Create lowercase dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains all dataset')
    args = parser.parse_args()
    main(args.path)
