# get the 1,000 most-downloaded packages
# from hugovk/top-pypi-packages

import json
import time
import requests


DATA_URL = 'https://hugovk.github.io/top-pypi-packages/top-pypi-packages-30-days.min.json'

packages_file = '../pkg/packages.txt'
linux_packages_file = '../pkg/pkgs_linux.txt'
windows_packages_file = '../pkg/pkgs_win.txt'
excluded_packages_file = '../pkg/pkgs_ex.txt'
included_packages_file = '../pkg/pkgs_in.txt'


excluded_packages = [
    # ML
    'torch',
    'tensorflow',

    # GPU
    'nvidia',
    'cuda',
    'cudnn',

    # Commercial / Cloud
    'aws',
    'amazon',
    'boto',
    's3',

    'azure',

    'google',
    'gcloud',
    'gcp',

    'aliyun',
    'alibabacloud',

    # Others
    'no-manylinux',
    'nightly',
]

linux_only_packages = [

]

windows_only_packages = [
    'win32',
]

include_packages = [
    'pyrogram',
    'tgcrypto',
    'telethon',
    'cryptg',
]


def get_top_packages(url: str = DATA_URL) -> list[str]:
    packages = []
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f'Error fetching data from {url}')

    raw = json.loads(response.text)
    for package in raw['rows']:
        # yield package['project']
        packages.append(package['project'])

    return packages


# common, linux, windows, excluded
def gen_packages(packages: list = None) -> tuple[list[str], list[str], list[str], list[str]]:
    if packages is None:
        packages = get_top_packages()

    # common = []
    linux = []
    windows = []
    excluded = []

    # excluded
    for to_check in packages.copy():
        for to_exclude in excluded_packages:
            if to_exclude in to_check:
                excluded.append(to_check)
                packages.remove(to_check)
                print(f'Excluded {to_check}')
                break

    # linux and windows
    for to_check in packages.copy():
        for to_exclude in linux_only_packages:
            if to_exclude in to_check:
                linux.append(to_check)
                packages.remove(to_check)
        for to_exclude in windows_only_packages:
            if to_exclude in to_check:
                windows.append(to_check)
                packages.remove(to_check)

    # common
    common = packages

    return common, linux, windows, excluded


def write_packages(packages: list[str], file: str):
    with open(file, 'w') as f:
        for package in packages:
            f.write(f'{package}\n')


def main():
    top_packages = get_top_packages()

    start_time = time.perf_counter()
    common, linux, windows, excluded = gen_packages(top_packages)
    end_time = time.perf_counter()
    print(f'Generated packages in {end_time - start_time:.6f} seconds')

    print(f'Common:\t{len(common)}')
    print(f'Linux:\t{len(linux)}')
    print(f'Windows:\t{len(windows)}')
    print(f'Excluded:\t{len(excluded)}')
    print(f'Included:\t{len(include_packages)}')

    start_time = time.perf_counter()
    write_packages(common, packages_file)
    write_packages(linux, linux_packages_file)
    write_packages(windows, windows_packages_file)
    write_packages(excluded, excluded_packages_file)
    write_packages(include_packages, included_packages_file)
    end_time = time.perf_counter()
    print(f'Wrote packages in {end_time - start_time:.6f} seconds')


if __name__ == '__main__':
    main()
