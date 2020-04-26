import sys
from pathlib import Path
import random
import constants
from tqdm import tqdm

def main(preprocessed_dir, prefix):
    import os
    prefix_path = os.path.join(preprocessed_dir,prefix )
    print(f'Use prefix path: {prefix_path}')
    
    f_index = open(prefix_path + '.index')
    f_target = open(prefix_path + '.target')
    f_line_diff = open(prefix_path + '.line.source')
    f_word_diff = open(prefix_path + '.word.source')
    
    dataset = []
    for index, target, line_diff, word_diff in tqdm(zip(f_index, f_target, f_line_diff, f_word_diff)):
        dataset.append((index, target, line_diff, word_diff))
    random.shuffle(dataset)
    total_cnt = len(dataset)
    print(f'Total {total_cnt} dataset... Start split!')
    test_cnt = int(total_cnt * constants.TEST_RATE)
    eval_cnt = int(total_cnt * constants.EVAL_RATE)
    train_cnt = total_cnt - test_cnt - eval_cnt
    
    test_dataset = dataset[:test_cnt]
    eval_dataset = dataset[test_cnt:test_cnt + eval_cnt]
    train_dataset = dataset[test_cnt + eval_cnt:]
    
    print(f'total_cnt: {total_cnt}')
    print(f'train_dataset: {len(train_dataset)}')
    print(f'eval_dataset: {len(eval_dataset)}')
    print(f'test_dataset: {len(test_dataset)}')


    dataset_dir = Path(preprocessed_dir).parent / 'dataset'
    dataset_dir.mkdir(exist_ok=True)
    line_dir = dataset_dir / 'line'
    word_dir = dataset_dir / 'word'
    line_dir.mkdir(exist_ok=True)
    word_dir.mkdir(exist_ok=True)
    filename_prefix = Path(preprocessed_dir).parent.name

    write_dataset(line_dir, word_dir, filename_prefix, train_dataset, 'train')
    write_dataset(line_dir, word_dir, filename_prefix, eval_dataset, 'eval')
    write_dataset(line_dir, word_dir, filename_prefix, test_dataset, 'test')


        
def write_dataset(line_dir, word_dir, filename_prefix, dataset, dataset_type='train'):
    f_line_index = open(line_dir / f'{filename_prefix}.{dataset_type}.index', 'w')
    f_line_target = open(line_dir / f'{filename_prefix}.{dataset_type}.target', 'w')
    f_line_source = open(line_dir / f'{filename_prefix}.{dataset_type}.source', 'w')

    f_word_index = open(word_dir / f'{filename_prefix}.{dataset_type}.index', 'w')
    f_word_target = open(word_dir / f'{filename_prefix}.{dataset_type}.target', 'w')
    f_word_source = open(word_dir / f'{filename_prefix}.{dataset_type}.source', 'w')

    for index, target, line_diff, word_diff in dataset:
        f_line_index.write(index.strip() + '\n')
        f_line_target.write(target.strip() + '\n')
        f_line_source.write(line_diff.strip() + '\n')

        f_word_index.write(index.strip() + '\n')
        f_word_target.write(target.strip() + '\n')
        f_word_source.write(word_diff.strip() + '\n')


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Split commit message dataset')
    
    parser.add_argument('--path', type=str, required=True, help='Directory which contains filtered dataset')
    parser.add_argument('--prefix', type=str, default='all.verbfilter', help='Filename prefix (in case of all.index => all')
    args = parser.parse_args()
    
    main(args.path, args.prefix)