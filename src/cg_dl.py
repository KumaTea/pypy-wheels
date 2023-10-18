import os
import sys
import zipfile
from tqdm import tqdm

MODULE_DIR = r'E:\Downloads\gohlkegrabber'
if MODULE_DIR not in sys.path:
    sys.path.append(MODULE_DIR)

from gohlkegrabber import GohlkeGrabber  # noqa


def whl_valid(file: str) -> bool:
    # whl is a zip file
    # check if a folder ends in dist-info in it
    with zipfile.ZipFile(file, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.endswith('dist-info/'):
                return True
    return False


DL_DST = r'E:\Downloads\gohlkegrabber\output'

if __name__ == '__main__':
    gg = GohlkeGrabber()
    gg.reload()

    pbar = tqdm(list(gg.packages.keys()))
    path, meta = '', ''
    for package in pbar:
        skip = False
        for whl_name in gg.packages[package]:
            if 'pypy' in whl_name:
                if whl_name in os.listdir('output'):
                    if whl_valid(os.path.join('output', whl_name)):
                        path = os.path.join('output', whl_name)
                        skip = True
                    else:
                        os.remove(os.path.join('output', whl_name))
                if not skip:
                    pbar.set_description(f'Now: {whl_name} Last: {str(path)}')
                    path, meta = gg.retrieve(
                        DL_DST, package,
                        python=gg.packages[package][whl_name]['python'],
                        platform=gg.packages[package][whl_name]['platform'],
                        version=gg.packages[package][whl_name]['version']
                    )
