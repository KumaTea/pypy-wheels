import os

# project

AUTHOR = 'KumaTea'
PROJ = 'pypy-wheels'
whl_file = 'wheels.html'
sha_file = 'sha256sums.json'
gh_rl_api = 'https://api.github.com/repos/{author}/{project}/releases'


# relative path

whl_dir = '../whl'
if not os.path.isdir(whl_dir):
    whl_dir = './whl'

pkg_dir = '../pkg'
if not os.path.isdir(pkg_dir):
    pkg_dir = './pkg'


# build

build_versions = ['3.7', '3.8', '3.9', '3.10']

LINUX_MAX_LOAD = 16
WIN_MAX_LOAD = 16


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
