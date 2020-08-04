import sys
from pathlib import Path
from utils import tokenize, overlap_two_seq, starts_with_verb, remove_tag_issue_number,\
 remove_http_urls, remove_redundant_white_space, remove_last_special_char
import random
from pathlib import Path
from subprocess import call, check_output, check_call
from tqdm import tqdm
from git import Repo
from utils import remove_no_english_str, tokenize, overlap_two_seq, starts_with_verb, remove_tag_issue_number,\
 remove_http_urls, remove_redundant_white_space, remove_last_special_char, has_no_english, split_sentence
from convert_utils import convert_line_diff_str, convert_word_diff_str
import shutil
import time
import constants
from multiprocessing import Pool
import concurrent.futures
import traceback
from make_language_dataset import get_line_diff, get_word_diff, clone_repository, fullname2dirname, dirname2fullname, DataWriter




def main(repo_sha_dic, repo_path, data_path):
    failed_repos = []
    total_cnt = 0
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=1) as executor:
            future_to_repo = {}
            for fullname in repo_sha_dic:
                branch = repo_sha_dic[fullname]['branch']
                sha_list = repo_sha_dic[fullname]['sha_list']
                future = executor.submit(make_each_repo_dataset, fullname, branch, sha_list, repo_path, data_path)
                future_to_repo[future] = fullname
            prog_bar = tqdm(concurrent.futures.as_completed(future_to_repo), total=len(repo_sha_dic))
            for future in prog_bar:
                fullname = future_to_repo[future]
                prog_bar.set_description(fullname)
                try:
                    total_cnt += future.result()
                    prog_bar.set_postfix(cnt=total_cnt)
                except Exception as exc:
                    
                    print(traceback.format_exc())
                    print(f' * repo: {fullname}')
                    
                    f_failed.write(fullname + '\n')
                    failed_repos.append(fullname)
    finally:
        print(f'Failed {len(failed_repos)} repos')
        print('\n'.join(failed_repos))

    
def make_each_repo_dataset(fullname, branch, sha_list, repo_path, data_path):
    repo_dir = repo_path / fullname2dirname(fullname)
    data_dir = data_path / fullname2dirname(fullname)
    data_dir.mkdir(exist_ok=True, parents=True)
    success_tag = data_dir / 'success'
    if success_tag.exists():
        with open(success_tag) as f:
            cnt = int(f.read())
            return cnt
    writer = DataWriter(data_dir, 'w')
    clone_repository(fullname, branch, repo_dir)
    cnt = generate_repo_dataset(fullname, branch, sha_list, repo_dir, writer)
    with open(success_tag, 'w') as f:
        f.write(str(cnt))
    shutil.rmtree(repo_dir)
    return cnt


def generate_repo_dataset(fullname, branch, sha_list, repo_dir, writer):
    repo = Repo(repo_dir)
    total_cnt, current_cnt, msg_skip, diff_skip, word_skip = 0, 0, 0, 0, 0
    index_list, origin_target_list, target_list, origin_line_list, line_list, origin_word_list, word_list = [],[],[],[],[],[],[]
    for sha in sha_list:
        commit = repo.commit(sha)
        total_cnt += 1
        commit_msg = commit.message
        sentences = split_sentence(commit_msg)
        if not sentences:
            continue
        commit_msg = sentences[0].strip()
        commit_msg_lower = commit_msg.lower()
        if 'revert' in commit_msg_lower or commit_msg_lower.startswith('merge '):
            msg_skip += 1
            continue
        commit_msg = remove_redundant_white_space(commit_msg.strip())
        origin_commit_msg = commit_msg
        if not commit_msg:
            msg_skip += 1
            continue
        
        commit_msg = tokenize(commit_msg)
        commit_msg = remove_last_special_char(commit_msg.strip())
        commit_msg = remove_no_english_str(commit_msg)
        commit_msg = remove_redundant_white_space(commit_msg.strip())
        commit_msg = commit_msg.strip()
        if not commit_msg:
            msg_skip += 1
            continue
        commit_words = commit_msg.split()
        # if not starts_with_verb(commit_words):
        #     msg_skip += 1
        #     continue
        if len(commit_words) > constants.TARGET_SEQ_LEN_MAX:
            msg_skip += 1
            continue
            
        line_diff = get_line_diff(repo_dir, sha)
        if not line_diff:
            diff_skip += 1
            continue
        origin_line_diff = line_diff
        line_diff = remove_no_english_str(line_diff)
        line_diff = remove_redundant_white_space(line_diff.strip())
        line_diff_words = line_diff.split()
        if not overlap_two_seq(line_diff_words, commit_words):
            diff_skip+=1
            continue

        if len(line_diff_words) > constants.SOURCE_SEQ_LEN_MAX:
            diff_skip+=1
            continue
        
        word_diff = get_word_diff(repo_dir, sha)
        if not word_diff:
            word_skip += 1
            continue
        origin_word_diff = word_diff
        word_diff = remove_no_english_str(word_diff)
        word_diff = remove_redundant_white_space(word_diff.strip())
        if not word_diff:
            word_skip += 1
            continue
        word_diff_words = word_diff.split()
        index = f'{fullname} {sha}'
        writer.write(index, origin_commit_msg, commit_msg, origin_line_diff, line_diff, origin_word_diff, word_diff)
        current_cnt+=1
    print(f'{fullname}:  {current_cnt}/{total_cnt}')
    return current_cnt

    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Filter commit message dataset')
    
    args = parser.parse_args()
    repo_path = Path(__file__).parent / 'repos' / 'java2000-origin'
    data_path = Path(__file__).parent / 'data' / 'java2000-origin' / 'preprocessed'

    repo_path.mkdir(exist_ok=True, parents=True)
    data_path.mkdir(exist_ok=True, parents=True)

    import json
    with open('old-java-2000-repo-sha.json') as f:
        repo_sha_dic = json.loads(f.read())
    main(repo_sha_dic, repo_path, data_path)
