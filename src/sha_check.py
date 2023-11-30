import hashlib
import logging
import requests
from tqdm import tqdm
from gen_whl import saved_sha256sums, save_sha256sums


whl_path = '../whl/wheels.html'
with open(whl_path, 'r', encoding='utf-8') as f:
    whl_html = f.read()


def get_sha_pkgs():
    pkgs = []

    for line in whl_html.split('\n'):
        if '<a' in line:
            a_tag_open_start = line.find('<a href="')
            a_tag_open_end = line.find('">')
            a_tag_close = line.find('</a>')
            pkg_filename = line[a_tag_open_end + len('">'):a_tag_close]
            pkg_url = line[a_tag_open_start + len('<a href="'):a_tag_open_end]

            if '#sha256=' in pkg_url:
                pkgs.append((pkg_filename, pkg_url))
    return pkgs


def sha_check(filename: str, url: str, pbar: tqdm):
    if saved_sha256sums[filename]['verify']:
        return True
    local_sha = saved_sha256sums[filename]['sha']
    remote_sha = url.split('#sha256=')[1]
    assert local_sha == remote_sha, f'{filename} sha256sum not match! local: {local_sha}, remote: {remote_sha}'

    cdn_url = f'https://gh.kmtea.eu/{url}'
    r = requests.get(cdn_url)
    assert r.status_code == 200, f'{filename} cdn url: {cdn_url} not found!'
    cdn_sha = hashlib.sha256(r.content).hexdigest()
    if cdn_sha != local_sha:
        pbar.write(
            f'\n{filename} cdn sha256sum not match!\n'
            f'  local: {local_sha}\n'
            f'  cdn: {cdn_sha}\n'
        )
    else:
        saved_sha256sums[filename]['verify'] = True


def remove_obsolete():
    for filename in saved_sha256sums.copy():
        if filename not in whl_html:
            logging.warning(f'{filename} not found in wheels.html!')
            saved_sha256sums.pop(filename)


def main():
    pkgs = get_sha_pkgs()
    pbar = tqdm(pkgs)
    for pkg in pbar:
        sha_check(pkg[0], pkg[1], pbar)
    remove_obsolete()
    save_sha256sums()


if __name__ == '__main__':
    main()
