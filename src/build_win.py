import subprocess
from config import *
from build import build, args, uninst_all
from prepare_win import prepare


def check_pypy(ver: str):
    command = f'{WIN_WORK_DIR}\\{ver}\\python.exe -V'
    try:
        result = subprocess.run(command.split(), stdout=subprocess.PIPE)
        if result:
            print(f'pypy {ver} is ready')
    except FileNotFoundError:
        print(f'pypy {ver} not found, initializing...')
        prepare(ver)


def build_win(ver: str = None, since: str = None, until: str = None, only: str = None, retry: bool = False):
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
        since=since,
        until=until,
        only=only,
        retry=retry
    )


def uninst_win(ver: str = None):
    if not ver:
        ver = args.ver
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)

    py_path = f'{WIN_WORK_DIR}\\{ver}\\python.exe'
    plat = 'win'

    return uninst_all(
        ver=ver,
        py_path=py_path,
        plat=plat
    )


if __name__ == '__main__':
    build_win(
        ver=args.ver,
        since=args.since,
        until=args.until,
        only=args.only,
        retry=args.retry
    )
