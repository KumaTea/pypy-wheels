import json
import hashlib
import logging
import requests
from config import *
from tqdm import tqdm


def get_local_whl_dict(d: list) -> dict:
    whl_dict = {}
    for i in [p for p in d if os.path.isdir(p)]:
        for root, dirs, files in os.walk(i):
            for file in files:
                if file.endswith('.whl'):
                    whl_dict[file] = os.path.join(root, file)
    return whl_dict


local_whl_dict = get_local_whl_dict([WIN_WHEEL_DIR, LINUX_WHEEL_DIR])


def get_saved_sha256sums():
    if os.path.exists(f'{whl_dir}/data/{sha_file}'):
        with open(f'{whl_dir}/data/{sha_file}', 'r', encoding='utf-8') as json_file:
            return json.load(json_file)
    return {}


saved_sha256sums = get_saved_sha256sums()


def get_whl_sha256(name: str):
    if name in saved_sha256sums:
        return saved_sha256sums[name]['sha']
    if name in local_whl_dict:
        path = local_whl_dict[name]
        with open(path, 'rb') as f:
            sha256sum = hashlib.sha256(f.read()).hexdigest()
        saved_sha256sums[name] = {'sha': sha256sum, 'verify': False}
        return sha256sum
    return None


def add_sha256_to_url(name: str, url: str):
    sha256sum = get_whl_sha256(name)
    if sha256sum:
        url += f'#sha256={sha256sum}'
    return url


def save_release(project: str, tag: str, data):
    with open(f'{whl_dir}/data/{project}-{tag}.json', 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file)


def load_release(filename: str):
    with open(f'{whl_dir}/data/{filename}', 'r', encoding='utf-8') as json_file:
        return json.load(json_file)


def get_gh_rl(author, project):
    os.makedirs(f'{whl_dir}/data', exist_ok=True)
    print('Fetching GitHub releases...')
    result_raw = requests.get(gh_rl_api.format(author=author, project=project)).json()
    for release in result_raw:
        if release['assets']:
            save_release(project, release['tag_name'], release)
    return result_raw


def check_dup(assets: list):
    assets_dict = {}
    for asset in assets:
        assets_dict[asset['name']] = assets_dict.get(asset['name'], []) + [asset['url']]
    for name, urls in assets_dict.items():
        if len(urls) > 1:
            logging.warning(f'Duplicated assets: {name}')
            for url in urls:
                logging.warning(f'\tURL: {url}')


def get_assets():
    assets = []
    releases = os.listdir(f'{whl_dir}/data')
    if 'sha256sums.json' in releases:
        releases.remove('sha256sums.json')
    for filename in tqdm(releases):
        release = load_release(filename)
        for binary in release['assets']:
            if 'whl' in binary['name']:
                assets.append({
                    'name': binary['name'],
                    'url': add_sha256_to_url(binary['name'], binary['browser_download_url'])
                })

    return assets


def gen_index():
    get_gh_rl(AUTHOR, PROJ)
    rl_list = get_assets()
    check_dup(rl_list)
    rl_html = ''

    # sort by filename
    rl_list.sort(key=lambda x: x['name'].lower())

    for file in rl_list:
        whl_index = (
                '<a href=\"' + file['url'] + '\">' +
                file['name'] +
                '</a><br>\n')
        rl_html += whl_index
    return ('<!DOCTYPE html>'
            '<html><body>\n'
            f'{rl_html}'
            '</body></html>')


def gen_html():
    index = gen_index()
    with open(f'{whl_dir}/{whl_file}', 'w', encoding='utf-8') as html_file:
        html_file.write(index)


def gen_html_cdn():
    with open(f'{whl_dir}/{whl_file}', 'r', encoding='utf-8') as html_file:
        html = html_file.read()
    with open(f'{whl_dir}/wheels-cdn.html', 'w', encoding='utf-8') as html_file:
        html_file.write(html.replace('https://github.com/', 'https://gh.kmtea.eu/https://github.com/'))


def save_sha256sums():
    with open(f'{whl_dir}/data/{sha_file}', 'w', encoding='utf-8') as json_file:
        # for better git
        json.dump(saved_sha256sums, json_file, indent=2)


if __name__ == '__main__':
    if os.name == 'nt':
        gen_html()
        save_sha256sums()
    else:
        gen_html_cdn()
