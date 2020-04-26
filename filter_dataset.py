import sys
from pathlib import Path
from utils import tokenize, overlap_two_seq, starts_with_verb, remove_tag_issue_number,\
 remove_http_urls, remove_redundant_white_space, remove_last_special_char
import random

def main(path, max_src_len, max_tgt_len):
    preprocessed_dir = Path(path)
    f_all_index = open(preprocessed_dir / 'all.index')
    f_all_target = open(preprocessed_dir / 'all.target')
    f_all_line_diff = open(preprocessed_dir / 'all.line.source')
    f_all_word_diff = open(preprocessed_dir / 'all.word.source')

    f_filtered_index = open(preprocessed_dir / 'all.filtered.index', 'w')
    f_filtered_target = open(preprocessed_dir / 'all.filtered.target', 'w')
    f_filtered_line_diff = open(preprocessed_dir / 'all.filtered.line.source', 'w')
    f_filtered_word_diff = open(preprocessed_dir / 'all.filtered.word.source', 'w')
    
    total_cnt = 0
    filtered_cnt = 0    
    for index, target, line_diff, word_diff in zip(f_all_index, f_all_target, f_all_line_diff, f_all_word_diff):
        total_cnt += 1
        #target = remove_tag_issue_number(target)
        #target = remove_http_urls(target)
        #target = remove_last_special_char(target)
        #target = remove_redundant_white_space(target.strip())
        target = tokenize(target)
        # target = target.lower().strip()
        # line_diff = line_diff.lower().strip()
        # word_diff = word_diff.lower().strip()
        target = target.strip()
        line_diff = line_diff.strip()
        word_diff = word_diff.strip()
        
        if not target:
            continue
        if not line_diff:
            continue
        if not word_diff:
            continue
        if target.startswith('revert "'):
            continue
        target_words = target.split()
        line_diff_words = line_diff.split()
        word_diff_words = word_diff.split()
        if len(target_words) > max_tgt_len:
            continue
        if len(line_diff_words) > max_src_len:
            continue
        if len(word_diff_words) > max_src_len:
            continue
        if not overlap_two_seq(target_words, line_diff_words):
            continue
        if not overlap_two_seq(target_words, word_diff_words):
            continue
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
        description='Filter commit message dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains all dataset')
    parser.add_argument('--max-src-len', type=int, default=100, help='Enter maximum length of source sentences')
    parser.add_argument('--max-tgt-len', type=int, default=30, help='Enter maximum length of target sentences')
    args = parser.parse_args()
    main(args.path, args.max_src_len, args.max_tgt_len)
