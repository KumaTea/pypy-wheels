from config import *
from build import build, args


def get_pypy(ver: str):
    return f'/opt/python/pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}_pp73/bin/python3'


def build_linux(ver: str = None, since: str = None, until: str = None, only: str = None, retry: bool = False):
    if not ver:
        ver = args.ver
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)

    pypy_path = get_pypy(ver)
    plat = 'linux'

    return build(
        ver=ver,
        py_path=pypy_path,
        plat=plat,
        since=since,
        until=until,
        only=only,
        retry=retry
    )


if __name__ == '__main__':
    build_linux(
        ver=args.ver,
        since=args.since,
        until=args.until,
        only=args.only,
        retry=args.retry
    )
