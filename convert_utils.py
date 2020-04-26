import re
from utils import remove_no_english_str, remove_redundant_white_space, tokenize, split_sentence, remove_last_special_char
import constants

def convert_commit_msg(path):
    with open(path/'commit_msg', errors="ignore") as f:
        output = f.read()
    output = remove_redundant_white_space(output)
    commit_msg_sentences = split_sentence(output)
    if len(commit_msg_sentences) == 0:
        return ''

    commit_msg = commit_msg_sentences[0]
    commit_msg = remove_no_english_str(commit_msg)
    commit_msg = remove_redundant_white_space(commit_msg.strip())

    commit_msg = remove_last_special_char(commit_msg)
    return commit_msg



def convert_line_diff(path):
    with open(path/'line_diff.patch', errors="ignore") as f:
        output = f.read()
    return convert_line_diff_str(output)

def convert_line_diff_str(s):
    pattern = 'diff --git a\/(?P<path>\S+) b\/(\S+)'
    start_indices = []
    filenames = []
    for m in re.finditer(pattern, s):
        start_indices.append(m.start())
        filenames.append(m.group('path'))
    pairs = get_diff_index_pairs(start_indices, len(s))
    diff_data = ''
    for filename, p in zip(filenames, pairs):
        diff = s[p[0]:p[1]]
        file_data = convert_file_line_diff(filename, diff)
        diff_data += file_data
    
    return remove_redundant_white_space(diff_data)

def convert_file_line_diff(filename, file_diff):
    
    file_diff_data = convert_filename(filename)
    
    diff = re.sub('@@.+?@@', '@@\n', file_diff)
    blocks = []
    for each_block in diff.split('@@')[1:]:
        blocks.append(convert_block_line_diff(each_block))
    
    return file_diff_data + ' ' + f' {constants.BLOCK_START} '.join(blocks)
    

def convert_block_line_diff(block_diff):
    block_str = ''
    for line in block_diff.split('\n'):
        if re.match(r'^\s*$', line):
            continue
        line = tokenize(line)
        line = replace_diff_line_symbol(line)
        block_str += f'{line}\n'
    return block_str
        
        
def replace_diff_line_symbol(s):
    if s[0] == '+':
        return re.sub(r'^\+', constants.ADD_START + ' ', s)
    elif s[0] == '-':
        return re.sub(r'^-', constants.DELETE_START + ' ', s)
    else:
        return f'{constants.SAME_START} {s}'
    


def get_diff_index_pairs(indices, output_len):
    pairs = []
    prev_start_index = -1
    for i in indices:
        if prev_start_index > -1:
            pairs.append((prev_start_index, i))
        prev_start_index = i
    pairs.append((prev_start_index, output_len))
    return pairs

    
def convert_filename(filename):
    tokenized_filename = tokenize(filename.replace('/', '.'))
    return f'{constants.FILE_START} {tokenized_filename} {constants.FILE_END}\n'



def convert_file_word_diff(filename, file_diff):
    file_diff_data = convert_filename(filename)
    
    diff = re.sub('@@.+?@@', '@@\n', file_diff)
    blocks = []
    for each_block in diff.split('@@')[1:]:
        blocks.append(convert_block_word_diff(each_block))
    return file_diff_data + ' ' + f' {constants.BLOCK_START} '.join(blocks)

def convert_block_word_diff(block_diff):
    block_str = ''
    for line in block_diff.split('\n'):
        if re.match(r'^\s*$', line):
            continue
        line = tokenize(line)
        line = replace_word_diff_line_symbol(line)
        block_str += f'{line}\n'
    return block_str

def replace_word_diff_line_symbol(s):
    s = re.sub(r'\{\+', ' ' + constants.ADD_START + ' ', s)
    s = re.sub(r'\+\}', ' ' + constants.ADD_END + ' ', s)
    s = re.sub(r'\[\-', ' ' + constants.DELETE_START + ' ', s)
    s = re.sub(r'\-\]', ' ' + constants.DELETE_END + ' ', s)
    return s
    

def convert_word_diff(path):
    with open(path/'word_diff.patch', errors="ignore") as f:
        output = f.read()
    return convert_word_diff_str(output)

def convert_word_diff_str(s):
    pattern = 'diff --git a\/(?P<path>\S+) b\/(\S+)'
    start_indices = []
    filenames = []
    for m in re.finditer(pattern, s):
        start_indices.append(m.start())
        filenames.append(m.group('path'))
    pairs = get_diff_index_pairs(start_indices, len(s))
    diff_data = ''
    for filename, p in zip(filenames, pairs):
        diff = s[p[0]:p[1]]
        file_data = convert_file_word_diff(filename, diff)
        diff_data += file_data
    
    return remove_redundant_white_space(diff_data)