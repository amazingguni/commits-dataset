import sys
from pathlib import Path
from utils import tokenize, overlap_two_seq, starts_with_verb, remove_tag_issue_number,\
 remove_http_urls, remove_redundant_white_space, remove_last_special_char, starts_with_verb2, remove_no_english_str, remove_first_special_charactor, has_no_english
import random
import constants

def custom_preprocess(s):
    if 'Signed-off-by:' in s:
        s = s[:s.index('Signed-off-by:')]
    if 'Change-Id: ' in s:
        s = s[:s.index('Change-Id: ')]
    if 'Former-commit-id: ' in s:
        s = s[:s.index('Former-commit-id: ')]
    if 'Upstream-commit:' in s:
        s = s[:s.index('Upstream-commit:')]
    if 'Reviewed By :' in s:
        s = s[:s.index('Reviewed By :')]
    if 'Co-authored-by: ' in s:
        s = s[:s.index('Co-authored-by: ')]
    s = remove_tag_issue_number(s)
    s = remove_http_urls(s)
    s = remove_first_special_charactor(s)
    s = remove_last_special_char(s)
    s = tokenize(s)
    s = remove_no_english_str(s)
    return remove_redundant_white_space(s)

    

def main(path):
    preprocessed_dir = Path(path)
    f_all_index = open(preprocessed_dir / 'all.index')
    f_all_target = open(preprocessed_dir / 'all.target')
    f_all_origin_target = open(preprocessed_dir / 'all.origin.target')
    f_all_line_diff = open(preprocessed_dir / 'all.line.source')
    f_all_word_diff = open(preprocessed_dir / 'all.word.source')

    f_filtered_index = open(preprocessed_dir / 'all.verbfilter.index', 'w')
    f_filtered_target = open(preprocessed_dir / 'all.verbfilter.target', 'w')
    f_filtered_line_diff = open(preprocessed_dir / 'all.verbfilter.line.source', 'w')
    f_filtered_word_diff = open(preprocessed_dir / 'all.verbfilter.word.source', 'w')
    
    total_cnt = 0
    filtered_cnt = 0    
    word_not_overlap_cnt = 0
    for index, origin_target, target, line_diff, word_diff in zip(f_all_index, f_all_origin_target, f_all_target, f_all_line_diff, f_all_word_diff):
        total_cnt += 1
        # target = target.strip()
        if has_no_english(origin_target):
            continue
        if has_no_english(line_diff):
            continue
        if has_no_english(word_diff):
            continue
        origin_target = origin_target.strip()
        target = custom_preprocess(origin_target)
        if not target:
            continue
        line_diff = line_diff.strip()
        word_diff = word_diff.strip()
        
        if 'revert' in target.lower():
            continue
        target_words = target.split()
        # if not starts_with_verb(target.lower().split()):
        #     continue
        line_diff_words = line_diff.split()
        word_diff_words = word_diff.split()
        if len(target_words) == 1:
            continue
        if not overlap_two_seq(word_diff_words, target_words):
            word_not_overlap_cnt += 1
            continue
        if len(target_words) > constants.TARGET_SEQ_LEN_MAX:
            continue
        if len(line_diff_words) > constants.SOURCE_SEQ_LEN_MAX:
            continue
        if len(word_diff_words) > constants.SOURCE_SEQ_LEN_MAX:
            continue
        f_filtered_index.write(f'{index.strip()}\n')
        f_filtered_target.write(f'{target}\n')
        f_filtered_line_diff.write(f'{line_diff}\n')
        f_filtered_word_diff.write(f'{word_diff}\n')
        filtered_cnt += 1
    print(f'Filtered {filtered_cnt} data generated(total: {total_cnt})')
    print(f'word_not_overlap_cnt: {word_not_overlap_cnt}')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Verb filter commit message dataset')
    
    parser.add_argument('--path', type=str, metavar='N', required=True, help='Directory which contains all dataset')
    args = parser.parse_args()
    main(args.path)
