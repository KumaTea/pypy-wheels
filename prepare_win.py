import os
import shutil
import zipfile
import requests
import subprocess
from tools import *
from config import *
from tqdm import tqdm


def get_pip_cache_dir() -> str:
    command = 'pip cache dir'
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    return result.stdout.decode().strip()


def prepare(ver: str):
    # clear cache
    # print('Clearing cache...')
    # pip_cache_dir = get_pip_cache_dir()
    # if os.path.exists(pip_cache_dir):
    #     shutil.rmtree(pip_cache_dir)

    # download pypy
    print('Preparing pypy...')
    if not os.path.exists(WIN_DL_DIR):
        os.makedirs(WIN_DL_DIR)

    pypy_link = get_pypy_link(ver)
    pypy_file = os.path.basename(pypy_link)
    pypy_path = os.path.join(WIN_DL_DIR, pypy_file)
    if not os.path.exists(pypy_path):
        print('Downloading pypy...')
        chunk_size = 1024 * 1024
        with requests.get(pypy_link, stream=True) as r:
            total_size = int(r.headers.get('content-length', 0))
            with open(pypy_path, 'wb') as f:
                for chunk in tqdm(r.iter_content(chunk_size=chunk_size), total=total_size // chunk_size, unit='MB'):
                    f.write(chunk)

    # extract pypy
    pypy_dir = os.path.join(WIN_WORK_DIR, ver)
    if os.path.exists(pypy_dir):
        shutil.rmtree(pypy_dir)

    print('Extracting pypy...')
    folder_name = pypy_file[:-4]
    with zipfile.ZipFile(pypy_path, 'r') as f:
        # f.extractall(dl_dir)
        files = f.namelist()
        pbar = tqdm(files)
        for file in pbar:
            pbar.set_description(file.replace(folder_name, ''))
            f.extract(file, WIN_DL_DIR)
    os.rename(os.path.join(WIN_DL_DIR, folder_name), pypy_dir)

    # install pip
    print('Installing pip...')
    pypy_bin = os.path.join(pypy_dir, 'python.exe')
    subprocess.run([pypy_bin, '-m', 'ensurepip'])
    subprocess.run([pypy_bin, '-m', 'pip', 'install', '-U', 'pip', 'setuptools', 'wheel'])

    return pypy_bin
