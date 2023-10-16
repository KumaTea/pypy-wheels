import argparse
import subprocess
from config import *
from tqdm import tqdm


arg = argparse.ArgumentParser()
arg.add_argument('-V', '--ver', help='pypy version')
arg.add_argument('-s', '--since', help='start from this package')
args = arg.parse_args()


def build(ver: str, py_path: str, plat: str = 'win', since: str = None):
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)
    # if 'win' in plat:
    #     check_pypy(ver)

    print(f'Building wheels for pypy {ver}...')
    # packages = []
    success = []
    failed = []

    with open('../packages.txt', 'r') as f:
        packages = f.read().splitlines()

    if 'win' in plat:
        with open('../pkgs_win.txt', 'r') as f:
            packages = packages + f.read().splitlines()
    elif 'linux' in plat:
        with open('../pkgs_linux.txt', 'r') as f:
            packages = packages + f.read().splitlines()

    with open('../pkgs_in.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    packages = list(set(packages))
    if since:
        index = packages.index(since)
        if index > 0:
            packages = packages[index - 1:]

    pbar = tqdm(packages)
    for pkg in pbar:
        pbar.set_description(f'Success: {len(success)}, Failed: {len(failed)}, Current: {pkg}')
        command = (f'{py_path} -m '
                   f'pip install -U {pkg} '
                   f'--extra-index-url https://pypy.kmtea.eu/wheels.html')
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if f'Successfully installed {pkg}' in result.stdout.decode('utf-8'):
                success.append(pkg)
            elif f'Requirement already satisfied: {pkg}' in result.stdout.decode('utf-8'):
                success.append(pkg)
            else:
                failed.append(pkg)
                print(result.stdout.decode('utf-8'))
                print('########## ERROR ##########')
                print(result.stderr.decode('utf-8'))
                print('##########  END  ##########')
        except Exception as e:
            failed.append(pkg)
            print(e)

    print(f'Success: {len(success)}, Failed: {len(failed)}')
    return success, failed
