import requests

def main(language, token):
    fullnames = []
    
    for i in range(10):
        page = i + 1
        print(f'download page {page}')
        query = f'topic:{language} language:{language} stars:>0'
        url = f'https://api.github.com/search/repositories?q={query}&sort=stars&per_page=100&page={page}'
        if token:
            url  += f'&access_token={token}'
        response = requests.get(url)
        fullnames += [(item['full_name'], item['stargazers_count'], item['default_branch']) for item in response.json()['items']]

    with open(f'{language}_top_1000.txt', 'w') as f:
        for name, star, branch in fullnames:
            f.write(f'{name}\t{star}\t{branch}\n')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(
        description='Get top 1000 language repository list ordered by star')
    
    parser.add_argument('--language', type=str)
    parser.add_argument('--token', type=str, required=False)
    args = parser.parse_args()
    
    main(args.language, args.token)
