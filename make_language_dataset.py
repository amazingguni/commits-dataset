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

def fullname2dirname(fullname):
    return fullname.replace('/', '_TOKEN_')
def dirname2fullname(fullname):
    return fullname.replace('_TOKEN_', '/')


def clone_repository(fullname, branch, repo_dir):
    if repo_dir.exists():
        shutil.rmtree(repo_dir)
    
    # git_url = f'https://github.com/{fullname}.git'
    git_url = f'git@github.com:{fullname}.git'
    repo_dir.mkdir(exist_ok=True, parents=True)
    check_call('git init', shell=True, cwd=repo_dir)
    check_call(f'git remote add origin {git_url}', shell=True, cwd=repo_dir)
    check_call(f'git fetch origin {branch}', shell=True, cwd=repo_dir)
    check_call(f'git checkout -t origin/{branch}', shell=True, cwd=repo_dir)
    repo = Repo(repo_dir)


class DataWriter:
    def __init__(self, data_path, mode='w'):
        self.f_index = open(data_path / 'all.index', mode)
        self.f_origin_target = open(data_path / 'all.origin.target', mode)
        self.f_target = open(data_path / 'all.target', mode)
        self.f_origin_line = open(data_path / 'all.origin.line.source', mode)
        self.f_line = open(data_path / 'all.line.source', mode)
        self.f_origin_word = open(data_path / 'all.origin.word.source', mode)
        self.f_word = open(data_path / 'all.word.source', mode)
        self.cnt = 0
    
    def write(self, index, origin_target, target, origin_line, line, origin_word, word):
        self.cnt += 1
        self.f_index.write(f'{index}\n')
        self.f_origin_target.write(f'{origin_target}\n')
        self.f_target.write(f'{target}\n')
        self.f_origin_line.write(f'{origin_line}\n')
        self.f_line.write(f'{line}\n')
        self.f_origin_word.write(f'{origin_word}\n')
        self.f_word.write(f'{word}\n')
    
    def write_list(self, index_list, origin_target_list, target_list, origin_line_list, line_list, origin_word_list, word_list):
        self.cnt += len(index_list)
        self.f_index.write('\n'.join(index_list))
        self.f_origin_target.write('\n'.join(origin_target_list))
        self.f_target.write('\n'.join(target_list))
        self.f_origin_line.write('\n'.join(origin_line_list))
        self.f_line.write('\n'.join(line_list))
        self.f_origin_word.write('\n'.join(origin_word_list))
        self.f_word.write('\n'.join(word_list))

def main(repo_file, from_index, repo_path, data_path):
    fullnames = []
    with open(repo_file) as f:
        for line in f:
            if not line:
                continue
            fullname, star, branch = line.strip().split('\t')
            fullnames.append((fullname, branch))
    print(f'Start from {from_index}')
    failed_repos = []
    total_cnt = 0
    f_failed = open(f'failed_{repo_file}', 'w') 
    try:
        with concurrent.futures.ProcessPoolExecutor(max_workers=64) as executor:
            fullnames = fullnames[from_index:]
            future_to_repo = {executor.submit(make_each_repo_dataset, fullname, branch, repo_path, data_path): fullname for fullname, branch in fullnames}
            prog_bar = tqdm(concurrent.futures.as_completed(future_to_repo), total=len(fullnames))
            for future in prog_bar:
                fullname = future_to_repo[future]
                prog_bar.set_description(fullname)
                try:
                    total_cnt += future.result()
                    # if not is_ok:
                    #     f_failed.write(fullname + '\n')
                    #     failed_repos.append(fullname)
                    #     continue
                    prog_bar.set_postfix(cnt=total_cnt)
                except Exception as exc:
                    
                    print(traceback.format_exc())
                    print(f' * repo: {fullname}')
                    
                    f_failed.write(fullname + '\n')
                    failed_repos.append(fullname)
    finally:
        print(f'Failed {len(failed_repos)} repos')
        print('\n'.join(failed_repos))

    
def make_each_repo_dataset(fullname, branch, repo_path, data_path):
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
    cnt = generate_repo_dataset(fullname, branch, repo_dir, writer)
    with open(success_tag, 'w') as f:
        f.write(str(cnt))
    shutil.rmtree(repo_dir)
    return cnt


def generate_repo_dataset(fullname, branch, repo_dir, writer):
    repo = Repo(repo_dir)
    total_cnt, current_cnt, msg_skip, diff_skip, word_skip = 0, 0, 0, 0, 0
    index_list, origin_target_list, target_list, origin_line_list, line_list, origin_word_list, word_list = [],[],[],[],[],[],[]
    for commit in repo.iter_commits(branch):
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
            
        sha = str(commit.hexsha)
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

def get_line_diff(repo_dir, sha):
    try:
        line_diff = check_output(f'git show {sha}', shell=True, cwd=repo_dir, encoding='utf-8')
        return convert_line_diff_str(line_diff)
    except UnicodeDecodeError:
        pass

def get_word_diff(repo_dir, sha):
    try:
        word_diff = check_output(f'git show --word-diff {sha}', shell=True, cwd=repo_dir, encoding='utf-8')
        return convert_word_diff_str(word_diff)
    except UnicodeDecodeError:
        pass
    
if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Filter commit message dataset')
    
    parser.add_argument('--from-index', type=int, default=0, help='from index')
    parser.add_argument('--repo-file', type=str, default='java_top_1000.txt')
    parser.add_argument('--language', type=str, default='java')
    args = parser.parse_args()
    language = args.language
    repo_path = Path(__file__).parent / 'repos' / f'{language}1000'
    data_path = Path(__file__).parent / 'data' / f'{language}1000' / 'preprocessed'

    repo_path.mkdir(exist_ok=True, parents=True)
    data_path.mkdir(exist_ok=True, parents=True)

    main(args.repo_file, args.from_index, repo_path, data_path)
