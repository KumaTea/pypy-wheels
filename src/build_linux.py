import argparse
import subprocess
from config import *
from tqdm import tqdm


arg = argparse.ArgumentParser()
arg.add_argument('-V', '--ver', help='pypy version')
args = arg.parse_args()


def get_pypy(ver: str):
    return f'/opt/python/pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}_pp73/bin/python3'


def build(ver: str = None):
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

    packages = list(set(packages))

    pbar = tqdm(packages)
    for pkg in pbar:
        pbar.set_description(f'Success: {len(success)}, Failed: {len(failed)}, Current: {pkg}')
        command = (f'{pypy_path} -m '
                   f'pip install -U {pkg} '
                   f'--extra-index-url https://pypy.kmtea.eu/wheels.html')
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if f'Successfully installed {pkg}' in result.stdout.decode('utf-8').lower():
                success.append(pkg)
            elif f'Requirement already satisfied: {pkg}' in result.stdout.decode('utf-8').lower():
                success.append(pkg)
            else:
                failed.append(pkg)
                print(result.stdout.decode('utf-8'))
        except Exception as e:
            failed.append(pkg)
            print(e)

    print(f'Success: {len(success)}, Failed: {len(failed)}')


if __name__ == '__main__':
    build()
