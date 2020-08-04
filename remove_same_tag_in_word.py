from pathlib import Path
import shutil

def remove_same(line):
    # s = "<file> src . org . zaproxy . zap . extension . httppanel . view . largeresponse . ExtensionHttpPanelLargeResponseView . java </file> import org . zaproxy . zap . view . HttpPanelManager . HttpPanelViewFactory ; public class ExtensionHttpPanelLargeResponseView extends ExtensionAdaptor { public static final String NAME = \" ExtensionHttpPanelLargeResponseView \"; public static final int MIN_CONTENT_LENGTH = <delete> 10000 ; </delete> <add> 100000 ; </add> public ExtensionHttpPanelLargeResponseView () { super ( NAME ); <file> src . org . zaproxy . zap . extension . httppanel . view . largeresponse . ExtensionHttpPanelLargeResponseView . java </file> import org . zaproxy . zap . view . HttpPanelManager . HttpPanelViewFactory ; public class ExtensionHttpPanelLargeResponseView extends ExtensionAdaptor { public static final String NAME = \" ExtensionHttpPanelLargeResponseView \"; public static final int MIN_CONTENT_LENGTH = <delete> 10000 ; </delete> <add> 100000 ; </add> public ExtensionHttpPanelLargeResponseView () { super ( NAME );"
    # start_file = False
    # start_add = False
    # start_delete = False
    result = []
    cache = []
    is_start = False
    start_tokens = ['<file>', '<add>', '<delete>']
    end_tokens = ['</file>', '</add>', '</delete>']
    special_tokens = start_tokens + end_tokens
    for word in line.strip().split():
        if word in start_tokens:
            is_start = True
            result.append(word)
            continue
        if word in end_tokens:
            is_start = False
            result.append(word)
            continue
        if is_start:
            result.append(word)
            continue
    return ' '.join(result)


def main(path):
    dataset_path = Path(path)
    out_dataset_path = dataset_path.parent / f'{dataset_path.name}_same_removed'
    out_dataset_path.mkdir(exist_ok=True)
    
    for each in dataset_path.glob('*.*.*'):
        out_path = out_dataset_path / each.name
        if '.source' not in each.name:
            shutil.copy(each, out_path)
            continue
        with open(each) as f, open(out_path, 'w') as f_out:
            for line in f:
                line = remove_same(line)
                f_out.write(line + '\n')
                

        

    # with open(dataset_path) as f, open(out_dataset_path, 'w') as f_out:
    #     for line in f:
    #         line = line.strip()
    #         print(line)
    #         exit()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Remove same words')
    
    parser.add_argument('--path', type=str, required=True)
    args = parser.parse_args()
    main(args.path)
