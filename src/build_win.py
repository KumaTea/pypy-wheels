import subprocess
from config import *
from build import build, args
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


def build_win(ver: str = None, since: str = None):
    if not ver:
        ver = args.ver
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)
    check_pypy(ver)

    py_path = f'{WIN_WORK_DIR}\\{ver}\\python.exe'
    plat = 'win'

    return build(
        ver=ver,
        py_path=py_path,
        plat=plat,
        since=since
    )


if __name__ == '__main__':
    build_win(
        ver=args.ver,
        since=args.since
    )
