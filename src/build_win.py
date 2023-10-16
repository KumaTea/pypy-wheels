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


def copy_wheels():
    print(f'Copying wheels for pypy...')
    pip_cache_dir = get_pip_cache_dir()
    if not os.path.exists(pip_cache_dir):
        return None

    for ver in build_versions:
        os.makedirs(f'{WIN_WHEEL_DIR}\\{ver}', exist_ok=True)
    os.makedirs(f'{WIN_WHEEL_DIR}\\none', exist_ok=True)

    # find whl file in pip cache
    whl_files = []
    for root, dirs, files in os.walk(pip_cache_dir):
        for file in files:
            if file.endswith('.whl'):
                whl_files.append((root, file))

    # copy whl file to wheel dir
    pbar = tqdm(whl_files)
    copied_files = []
    for root, file in pbar:
        if file in copied_files:
            continue
        else:
            pbar.set_description(f'Coping {file}')
            for ver in build_versions:
                if f'pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}' in file:
                    shutil.copy(f'{root}\\{file}', f'{WIN_WHEEL_DIR}\\{ver}\\{file}')
                    copied_files.append(file)
                    break
            else:
                shutil.copy(f'{root}\\{file}', f'{WIN_WHEEL_DIR}\\none\\{file}')
                copied_files.append(file)

    print(f'Copied {len(copied_files)} wheels')
    return copied_files


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
