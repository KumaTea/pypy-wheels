import subprocess
from config import *
from tqdm import tqdm
from prepare_win import prepare


def check_pypy(ver: str):
    command = f'{WIN_WORK_DIR}\\{ver}\\python.exe -m pip list'
    try:
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        if result:
            print(f'pypy {ver} is ready')
    except FileNotFoundError:
        print(f'pypy {ver} not found, initializing...')
        prepare(ver)


def build(ver: str):
    check_pypy(ver)

    print(f'Building wheels for pypy {ver}...')
    # packages = []
    success = []
    failed = []

    with open('../packages.txt', 'r') as f:
        packages = f.read().splitlines()

    with open('../pkgs_win.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    with open('../pkgs_in.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    packages = list(set(packages))

    pbar = tqdm(packages)
    for pkg in pbar:
        pbar.set_description(f'Success: {len(success)}, Failed: {len(failed)}, Current: {pkg}')
        command = (f'{WIN_WORK_DIR}\\{ver}\\python.exe -m '
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
