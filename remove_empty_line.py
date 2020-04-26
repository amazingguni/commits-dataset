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

    # f_index = open(preprocessed_dir / 'all.index', 'w')
    # f_target = open(preprocessed_dir / 'all.target', 'w')
    # f_origin_target = open(preprocessed_dir / 'all.origin.target', 'w')
    # f_line_diff = open(preprocessed_dir / 'all.line.source', 'w')
    # f_origin_line_diff = open(preprocessed_dir / 'all.origin.line.source', 'w')
    # f_word_diff = open(preprocessed_dir / 'all.word.source', 'w')
    # f_origin_word_diff = open(preprocessed_dir / 'all.origin.word.source', 'w')
    # failed_list = []
    for repo_dir in prog_bar:
        with open(repo_dir / 'all.index') as f:
            indexes = f.read().strip().split('\n')
            current_repo_cnt = len(indexes)

        # with open(repo_dir / 'all.target') as f:
        #     targets = '\n'.join([line.strip() for line in f.readlines() if line.strip()])
        #     f_target.write(f.read().strip() + '\n')

        with open(repo_dir / 'all.origin.target') as f:
            targets = f.read().strip().split('\n')
            current_target_cnt = len(targets)
            empty_removed_targets = [t.strip() for t in targets if t.strip()]
            removed_cnt = len(empty_removed_targets)
        if current_target_cnt != removed_cnt:
            diff_cnt = current_target_cnt - removed_cnt
            print(f'{current_repo_cnt:3d} / {current_target_cnt:3d} / {removed_cnt:3d} / diff {diff_cnt:2d}  {repo_dir}')
            print('\n'.join(empty_removed_targets))



if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Remove empty line in dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains repository dataset directory')
    args = parser.parse_args()
    main(args.path)