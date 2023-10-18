import os
import shutil
import subprocess
from config import *
from tqdm import tqdm


def build(ver: str = None):
    try:
        os.makedirs(LINUX_MANY_DIR, exist_ok=True)
        for ver in build_versions:
            os.makedirs(f'{LINUX_MANY_DIR}/{ver}', exist_ok=True)
        os.makedirs(f'{LINUX_MANY_DIR}/done', exist_ok=True)
    except:
        pass

    # find whl file
    whl_files = []
    for root, dirs, files in os.walk(LINUX_WHEEL_DIR):
        for file in files:
            if 'linux' in file and 'manylinux' not in file and 'done' not in root:
                whl_files.append((root, file))

    print(f'Building manylinux wheels...')

    pbar = tqdm(whl_files)
    for root, file in pbar:
        this_ver = 'none'
        dst = f'{LINUX_MANY_DIR}/{this_ver}'
        for ver in build_versions:
            if f'pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}' in file:
                this_ver = ver
                dst = f'{LINUX_MANY_DIR}/{this_ver}'
                break
        pbar.set_description(f'Current: {file}')
        command = (f'/usr/local/bin/auditwheel repair '
                   f'-w {dst}/ '
                   f'{root}/{file}')
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # print(result.stdout.decode('utf-8'))
            # print(result.stderr.decode('utf-8'))
            # print(f'{root}/{file}', f'{LINUX_MANY_DIR}/done/{file}')
            shutil.move(f'{root}/{file}', f'{LINUX_MANY_DIR}/done/{file}')
        except Exception as e:
            print(e)


if __name__ == '__main__':
    build()
