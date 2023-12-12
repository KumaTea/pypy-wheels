import os
import shutil
import logging
from tqdm import tqdm
from check_sha import get_saved_hash
from tools import get_pip_cache_dir, is_good_whl
from config import LINUX_WHEEL_DIR, LINUX_MANY_DIR, WIN_WHEEL_DIR, build_versions


saved_hash = get_saved_hash()


def copy_wheels(dst: str):
    logging.info(f'Copying wheels for pypy...')
    pip_cache_dir = get_pip_cache_dir()
    if not os.path.exists(pip_cache_dir):
        return None

    os.makedirs(dst, exist_ok=True)
    for ver in build_versions:
        os.makedirs(f'{dst}/{ver}', exist_ok=True)
    os.makedirs(f'{dst}/none', exist_ok=True)

    logging.info('find whl file in pip cache')
    whl_files = []
    for root, dirs, files in os.walk(pip_cache_dir):
        for file in files:
            if is_good_whl(file):
                whl_files.append((root, file))

    with open('../whl/wheels.html', 'r', encoding='utf-8') as f:
        whl_html = f.read()

    logging.info('get new wheels')
    new_whl = []
    for root, file in whl_files:
        if file not in whl_html:
            new_whl.append((root, file))
        else:
            if file in saved_hash:
                logging.warning(f'Skip: \t{file} already exists in saved_sha256sums')
            else:
                new_whl.append((root, file))
                logging.warning(f'NEW: \t{file} exists in wheels.html but not in saved_sha256sums')
                logging.warning(f'\tYou MUST remove old file from releases!!!')

    logging.info('select files to copy')
    pbar = tqdm(new_whl)
    copied_files = []
    for root, file in pbar:
        if file in copied_files:
            continue
        else:
            pbar.set_description(f'Coping {file}')
            matched = False
            for ver in build_versions:
                if f'pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}' in file:
                    if not (os.path.isfile(f'{dst}/{ver}/{file}') or os.path.isfile(f'{LINUX_MANY_DIR}/done/{file}')):
                        shutil.copy(f'{root}/{file}', f'{dst}/{ver}/{file}')
                        copied_files.append(file)
                        matched = True
                        break
            if 'none' in file:
                if not (os.path.isfile(f'{dst}/none/{file}') or os.path.isfile(f'{LINUX_MANY_DIR}/done/{file}')):
                    shutil.copy(f'{root}/{file}', f'{dst}/none/{file}')
                    copied_files.append(file)
                    matched = True
            if not matched:
                logging.error(f'Unmatched: {file}')

    logging.info(f'Copied {len(copied_files)} wheels')
    return copied_files


if __name__ == '__main__':
    if os.name == 'nt':
        copy_wheels(WIN_WHEEL_DIR)
    else:
        copy_wheels(LINUX_WHEEL_DIR)
