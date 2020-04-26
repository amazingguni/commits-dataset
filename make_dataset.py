
import re
from pathlib import Path

from tqdm import tqdm
import constants
from convert_utils import convert_commit_msg, convert_line_diff, convert_word_diff

base_path = Path(__file__).resolve().parent
data_path = base_path / 'data'


# def get_generated_sha(index_path):



def main(name):
    java_commits_path = data_path / name / 'commits'
    preprocessed_path = data_path / name / 'preprocessed'
    index_path = data_path / name / 'preprocessed' / 'all.index'
    target_path = data_path / name / 'preprocessed' / 'all.target'
    line_diff_path = data_path / name / 'preprocessed' / 'all.line.source'
    word_diff_path = data_path / name / 'preprocessed' / 'all.word.source'

    if not java_commits_path.exists():
        print(f'Directory not exist: {java_commits_path}')
    preprocessed_path.mkdir(exist_ok=True)
    sha_path_list = [path for path in java_commits_path.glob('*/*')]
    prog_bar = tqdm(sha_path_list)

    current_cnt = 0
    with open(index_path, 'w') as f_index, open(target_path, 'w') as f_target, \
        open(line_diff_path, 'w') as f_line_diff, open(word_diff_path, 'w') as f_word_diff:
        for sha_path in prog_bar:
            repo = sha_path.parent.name
            sha = sha_path.name
            prog_bar.set_description(f'cnt:{current_cnt} {repo} {sha[:7]}')
            commit_msg = convert_commit_msg(sha_path).strip()
            if not commit_msg.strip():
                continue
            if len(commit_msg.split()) > constants.TARGET_SEQ_LEN_MAX:
                continue
            line_diff_data = convert_line_diff(sha_path).strip()
            if not line_diff_data:
                continue
            if len(line_diff_data.split()) > constants.SOURCE_SEQ_LEN_MAX:
                continue
            word_diff_data = convert_word_diff(sha_path).strip()
            f_index.write(f'{repo} {sha}\n')
            f_target.write(f'{commit_msg}\n')
            f_line_diff.write(f'{line_diff_data}\n')
            f_word_diff.write(f'{word_diff_data}\n')
            current_cnt += 1
            

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Generate commit message dataset')
    parser.add_argument('--name', type=str, metavar='N', required=True, help='Data name to generate dataset(e.g, java2000)')
    args = parser.parse_args()
    main(args.name)
    
