import logging
import subprocess
from tqdm import tqdm
from typing import List
from tools import get_whl_list


whl_list = get_whl_list()


def get_py_ver_from_abi(abi: str):
    # pypy310_pp73
    assert abi.startswith('pypy')
    assert abi.endswith('_pp73')
    ver = abi[4:-5]
    return f'pp{ver}'


def get_plat_dup():
    pkgs = {}
    dup = []

    for pair in whl_list:
        file, url = pair
        assert file.count('-') == 4, f'{file} has a wired name!'

        name, ver, pv_ver, abi, plat = file.split('-')
        if pv_ver == 'pp373':  # universal tag
            pv_ver = get_py_ver_from_abi(abi)

        if name not in pkgs:
            pkgs[name] = {}
        if ver not in pkgs[name]:
            pkgs[name][ver] = {}
        if pv_ver not in pkgs[name][ver]:
            pkgs[name][ver][pv_ver] = {}

        # skip abi
        if 'linux' in plat:
            os_type = 'linux'
        elif 'win' in plat:
            os_type = 'win'
        else:
            os_type = 'none'
        if os_type not in pkgs[name][ver][pv_ver]:
            pkgs[name][ver][pv_ver][os_type] = {}

        arch_list = ['x86_64', 'amd64', 'aarch64']
        for i in arch_list:
            if i in plat:
                arch = i
                break
        else:
            arch = 'any'
        if arch not in pkgs[name][ver][pv_ver][os_type]:
            pkgs[name][ver][pv_ver][os_type][arch] = []

        pkgs[name][ver][pv_ver][os_type][arch].append(file)

    for pkg in pkgs:
        for ver in pkgs[pkg]:
            for pv_ver in pkgs[pkg][ver]:
                for os_type in pkgs[pkg][ver][pv_ver]:
                    for arch in pkgs[pkg][ver][pv_ver][os_type]:
                        if len(pkgs[pkg][ver][pv_ver][os_type][arch]) > 1:
                            logging.error(f'Duplicated assets: {pkg=} {ver=} {pv_ver=} {os_type=} {arch=}')
                            for file in pkgs[pkg][ver][pv_ver][os_type][arch]:
                                logging.error(f'\tURL: {file}')
                            dup.append(pkgs[pkg][ver][pv_ver][os_type][arch])

    return dup


def get_asset_tag(asset: str):
    for file, url in whl_list:
        if file == asset:
            return url.split('/')[-2]
    return None


def del_asset(tag: str, file: str):
    cmd = f'gh release delete-asset {tag} {file} -y'
    return subprocess.run(cmd, shell=True)


def del_all_dup(dup: List[str]):
    pbar = tqdm(dup)
    for pair in pbar:
        to_del = min(pair, key=len)
        tag = get_asset_tag(to_del)
        pbar.set_description(f'Deleting {to_del}')
        del_asset(tag, to_del)


def get_exact_dup():
    pkgs = {}

    for pair in whl_list:
        file, url = pair
        pkg_filename = file
        pkg_url = url

        pkgs[pkg_filename] = pkgs.get(pkg_filename, []) + [pkg_url]

    for name, urls in pkgs.items():
        if len(urls) > 1:
            logging.error(f'Duplicated assets: {name}')
            for url in urls:
                logging.error(f'\tURL: {url}')


if __name__ == '__main__':
    dup_list = get_plat_dup()
    if dup_list and input('Delete all duplicated assets? (y/n) ') == 'y':
        del_all_dup(dup_list)
    else:
        print('No duplicated assets found.')
    get_exact_dup()
