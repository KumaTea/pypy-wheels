import requests
from urllib.parse import quote_plus


author = 'KumaTea'
project = 'pypy-wheels'
whl_dir = '../'
whl_file = 'wheels.html'
gh_rl_api = 'https://api.github.com/repos/{author}/{project}/releases'


def get_gh_rl(a, p):
    print('Fetching GitHub releases...')
    assets = []
    result_raw = requests.get(gh_rl_api.format(author=a, project=p)).json()
    for release in result_raw:
        if release['assets']:
            for binary in release['assets']:
                if 'whl' in binary['name']:
                    assets.append({
                        'name': binary['name'],
                        'url': binary['browser_download_url']
                    })
    return assets


def gen_index():
    rl_list = get_gh_rl(author, project)
    rl_html = ''
    for file in rl_list:
        whl_index = '<a href=\"' + file['url'] + '\">' + quote_plus(file['name']) + '</a><br>\n'
        rl_html += whl_index
    return f'<!DOCTYPE html>\n{rl_html}'


def gen_html():
    index = gen_index()
    with open(f'{whl_dir}/{whl_file}', 'w', encoding='utf-8') as html_file:
        html_file.write(index)


def gen_html_cdn():
    with open(f'{whl_dir}/{whl_file}', 'r', encoding='utf-8') as html_file:
        html = html_file.read()
    with open(f'{whl_dir}/stable-cn.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html.replace('https://github.com/', 'https://gh.kmtea.eu/https://github.com/'))


if __name__ == '__main__':
    gen_html()
    gen_html_cdn()
