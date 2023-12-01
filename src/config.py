# project
import os

AUTHOR = 'KumaTea'
PROJ = 'pypy-wheels'
whl_dir = '../whl'
whl_file = 'wheels.html'
sha_file = 'sha256sums.json'
gh_rl_api = 'https://api.github.com/repos/{author}/{project}/releases'


# build

build_versions = ['3.7', '3.8', '3.9', '3.10']

# win

WIN_WORK_DIR = 'E:\\Cache\\pypy'
WIN_DL_DIR = 'E:\\Cache\\pypy\\dl'
WIN_WHEEL_DIR = 'E:\\Cache\\pypy\\whl'

# linux
# docker, so root

if os.name == 'nt':
    LINUX_WORK_DIR = 'E:\\Cache\\linux'
else:
    LINUX_WORK_DIR = '/home/kuma/pypy'
LINUX_WHEEL_DIR = f'{LINUX_WORK_DIR}/whl'
LINUX_MANY_DIR = f'{LINUX_WORK_DIR}/whl/many'

LOCAL_WHL_LINK = 'http://localhost:10300'

LINUX_MAX_LOAD = 4
WIN_MAX_LOAD = 16
