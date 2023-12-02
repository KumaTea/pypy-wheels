import hashlib
import logging
import requests
from tqdm import tqdm
from tools import get_whl_list
from gen_whl import saved_sha256sums, save_sha256sums


def get_sha_pkgs():
    pkgs = []
    whl_list = get_whl_list()

    for pair in whl_list:
        file, url = pair
        if '#sha256=' in url:
            pkgs.append(pair)

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
    whl_list = get_whl_list()
    all_filenames = [pair[0] for pair in whl_list]
    for filename in saved_sha256sums.copy():
        if filename not in all_filenames:
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
