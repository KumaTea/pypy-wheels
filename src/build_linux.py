import argparse
import subprocess
from config import *
from tqdm import tqdm


arg = argparse.ArgumentParser()
arg.add_argument('-V', '--ver', help='pypy version')
args = arg.parse_args()


def get_pypy(ver: str):
    return f'/opt/python/pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}/bin/pypy3'


def build(ver: str):
    if not ver:
        ver = args.ver
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)
    pypy_path = get_pypy(ver)

    print(f'Building wheels for pypy {ver}...')
    # packages = []
    success = []
    failed = []

    with open('../packages.txt', 'r') as f:
        packages = f.read().splitlines()

    with open('../pkgs_linux.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    with open('../pkgs_in.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    pbar = tqdm(packages)
    for pkg in pbar:
        pbar.set_description(f'Success: {len(success)}, Failed: {len(failed)}, Current: {pkg}')
        command = f'{pypy_path} -m pip install -U {pkg}'
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result:
                success.append(pkg)
        except Exception as e:
            failed.append(pkg)
            print(e)

    print(f'Success: {len(success)}, Failed: {len(failed)}')
