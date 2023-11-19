# project

AUTHOR = 'KumaTea'
PROJ = 'pypy-wheels'
whl_dir = '../whl'
whl_file = 'wheels.html'
gh_rl_api = 'https://api.github.com/repos/{author}/{project}/releases'


# build

build_versions = ['3.7', '3.8', '3.9', '3.10']

# win

WIN_WORK_DIR = 'E:\\Cache\\pypy'
WIN_DL_DIR = 'E:\\Cache\\pypy\\dl'
WIN_WHEEL_DIR = 'E:\\Cache\\pypy\\whl'

# linux
# docker, so root

LINUX_WORK_DIR = '/root/pypy-wheels'
LINUX_WHEEL_DIR = '/root/pypy-wheels/whl'
LINUX_MANY_DIR = '/root/pypy-wheels/whl/many'

