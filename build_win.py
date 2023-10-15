import os
import shutil
import subprocess
from tools import *
from config import *
from tqdm import tqdm
from prepare_win import prepare, get_pip_cache_dir


def check_pypy(ver: str):
    command = f'{WIN_WORK_DIR}\\{ver}\\python.exe -m pip list'
    try:
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        if result:
            print(f'pypy {ver} is ready')
    except FileNotFoundError:
        print(f'pypy {ver} not found, initializing...')
        prepare(ver)


def copy_wheels(ver: str):
    print(f'Copying wheels for pypy {ver}...')
    pip_cache_dir = get_pip_cache_dir()
    if not os.path.exists(WIN_WHEEL_DIR):
        return None

    # find whl file in pip cache
    whl_files = []
    for root, dirs, files in os.walk(pip_cache_dir):
        for file in files:
            if file.endswith('.whl'):
                whl_files.append(os.path.join(root, file))

    # copy whl file to wheel dir
    pbar = tqdm(whl_files)
    for file in pbar:
        pbar.set_description(file.replace(pip_cache_dir, ''))
        shutil.copy(file, WIN_WHEEL_DIR)


def build(ver: str):
    check_pypy(ver)

    print(f'Building wheels for pypy {ver}...')
    # packages = []
    success = []
    failed = []

    with open('packages.txt', 'r') as f:
        packages = f.read().splitlines()

    with open('pkgs_win.txt', 'r') as f:
        packages = packages + f.read().splitlines()

    pbar = tqdm(packages)
    for pkg in pbar:
        pbar.set_description(f'Success: {len(success)}, Failed: {len(failed)}, Current: {pkg}')
        command = f'{WIN_WORK_DIR}\\{ver}\\python.exe -m pip install -U {pkg}'
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result:
                success.append(pkg)
        except Exception as e:
            failed.append(pkg)
            print(e)

    print(f'Success: {len(success)}, Failed: {len(failed)}')

    copy_wheels(ver)
