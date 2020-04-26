import sys
from pathlib import Path
from utils import tokenize, overlap_two_seq, starts_with_verb, remove_tag_issue_number,\
 remove_http_urls, remove_redundant_white_space, remove_last_special_char
import random

def main(path):
    preprocessed_dir = Path(path)
    f_all_index = open(preprocessed_dir / 'all.index')
    f_all_target = open(preprocessed_dir / 'all.target')
    f_all_line_diff = open(preprocessed_dir / 'all.line.source')
    f_all_word_diff = open(preprocessed_dir / 'all.word.source')

    f_filtered_index = open(preprocessed_dir / 'all.verbfilter.index', 'w')
    f_filtered_target = open(preprocessed_dir / 'all.verbfilter.target', 'w')
    f_filtered_line_diff = open(preprocessed_dir / 'all.verbfilter.line.source', 'w')
    f_filtered_word_diff = open(preprocessed_dir / 'all.verbfilter.word.source', 'w')
    
    total_cnt = 0
    filtered_cnt = 0    
    for index, target, line_diff, word_diff in zip(f_all_index, f_all_target, f_all_line_diff, f_all_word_diff):
        total_cnt += 1
        target = target.strip()
        if not target:
            continue
        line_diff = line_diff.strip()
        word_diff = word_diff.strip()
        if 'revert' in target.lower():
            continue
        target_words = target.split()
        if not starts_with_verb(target_words):
            continue
        f_filtered_index.write(f'{index.strip()}\n')
        f_filtered_target.write(f'{target}\n')
        f_filtered_line_diff.write(f'{line_diff}\n')
        f_filtered_word_diff.write(f'{word_diff}\n')
        filtered_cnt += 1
    print(f'Filtered {filtered_cnt} data generated(total: {total_cnt})')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Verb filter commit message dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains all dataset')
    args = parser.parse_args()
    main(args.path)
