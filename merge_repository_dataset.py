import sys
from pathlib import Path
import random
import constants
from tqdm import tqdm

def main(path):
    preprocessed_dir = Path(path)

    repo_dir_list = [repo_dir for repo_dir in list(preprocessed_dir.glob('*')) if repo_dir.is_dir()]
    prog_bar = tqdm(repo_dir_list)
    total_cnt = 0

    f_index = open(preprocessed_dir / 'all.index', 'w')
    f_target = open(preprocessed_dir / 'all.target', 'w')
    f_origin_target = open(preprocessed_dir / 'all.origin.target', 'w')
    f_line_diff = open(preprocessed_dir / 'all.line.source', 'w')
    f_origin_line_diff = open(preprocessed_dir / 'all.origin.line.source', 'w')
    f_word_diff = open(preprocessed_dir / 'all.word.source', 'w')
    f_origin_word_diff = open(preprocessed_dir / 'all.origin.word.source', 'w')
    failed_list = []
    for repo_dir in prog_bar:
        if not (repo_dir / 'success').is_file():
            failed_list.append(repo_dir)
            continue
        with open(repo_dir / 'all.index') as f:
            indexes = f.read().strip()
            total_cnt += len(indexes.split())
            f_index.write(indexes + '\n')

        with open(repo_dir / 'all.target') as f:
            f_target.write(f.read().strip() + '\n')
        with open(repo_dir / 'all.origin.target') as f:
            f_origin_target.write(f.read().strip() + '\n')

        with open(repo_dir / 'all.line.source') as f:
            f_line_diff.write(f.read().strip() + '\n')
        with open(repo_dir / 'all.origin.line.source') as f:
            f_origin_line_diff.write(f.read().strip() + '\n')

        with open(repo_dir / 'all.word.source') as f:
            f_word_diff.write(f.read().strip() + '\n')
        with open(repo_dir / 'all.origin.word.source') as f:
            f_origin_word_diff.write(f.read().strip() + '\n')

    print(f'total_cnt: {total_cnt}')
    print(f'failed_list:')
    for repo_path in failed_list:
        print(f' * {repo_path}')



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Merge repository dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains repository dataset directory')
    args = parser.parse_args()
    main(args.path)