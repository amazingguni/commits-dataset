import re
from nltk import WordPunctTokenizer, data, pos_tag, download
from nltk.corpus import wordnet

no_english_pattern = re.compile(r'[^\sa-zA-Z0-9.!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]')
download('averaged_perceptron_tagger')
download('wordnet')

def has_no_english(s):
    return bool(no_english_pattern.search(s))
        
def remove_no_english_str(s):
    # TODO If lines which contain no english charactor has no context meaning, consider to remove this line or commit from dataset
    except_no_english = r'[^\sa-zA-Z0-9.!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~]'
    processed = re.sub(except_no_english, '', s)
    return processed

def remove_redundant_white_space(s):
    return re.sub(r'\s+', ' ', s)

def remove_tag_issue_number(s):
    return re.sub(r'(\w+ \d+:)|([Ff]ix(es)? #?\d+)|([Bb]ug: ?\d+)|(\([Bb]ug \d+\))|(\([Ii]ssue #?\d+\))|(\([Cc]loses? #\d+\))|(#\d+-)|(\(#\d+\))|(\[#\d+\])|([Ii]ssues? #\d+:?)|({#\d+})|(^\[.+\])|(^\S{1,10}:)|(^\S+-\d+:? ?:?)|(\(cherry picked from commit \S+\))|([Cc]loses? gh-\d+)', '', s)

def remove_first_special_charactor(s):
    return re.sub(r'\s*[.:\-,\/\*]\s+', '', s)



def remove_http_urls(s):
    return re.sub(r'(\(.*https?:\/\/.*\))|(https?:\/\/\S+$)', '', s)
    
def remove_last_special_char(s):
    return re.sub(r'\s*[\.,;:]+\s*$', '', s)

def tokenize(s):
    tokens = WordPunctTokenizer().tokenize(s)
    return ' '.join(tokens)

def split_sentence(paragraph):
    tokenizer = data.load('tokenizers/punkt/english.pickle')
    sentences = tokenizer.tokenize(paragraph)
    return sentences

def overlap_two_seq(a, b):
    return bool(set(a) & set(b))

def starts_with_verb(word_list):
    if not word_list:
        return False
    # word_list = ['He'] + word_list
    pos_tags = pos_tag(['He'] + word_list)
    is_verb = pos_tags[1][1].startswith('V')
    if is_verb:
        return True
    pos_tags = pos_tag(['You'] + word_list)
    is_verb = pos_tags[1][1].startswith('V')
    if is_verb:
        return True
    return False
    
def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    if treebank_tag.startswith('V'):
        return wordnet.VERB
    if treebank_tag.startswith('N'):
        return wordnet.NOUN
    if treebank_tag.startswith('R'):
        return wordnet.ADV
    return wordnet.NOUN



def starts_with_verb2(word_list):
    if len(word_list) <= 0:
        return False
    word_list = ['He'] + word_list
    count = 0
    for word, pos in pos_tag(word_list):
        treebank_tag = get_wordnet_pos(pos)
        if count == 1:
            return treebank_tag.startswith('V') or treebank_tag.startswith('v')
        count += 1