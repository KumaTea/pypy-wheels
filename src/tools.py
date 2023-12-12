import sys
import psutil
import selectors
import subprocess
from config import *
from tqdm import tqdm
from config_ver import PYTHON_TO_PYPY


def get_pip_cache_dir() -> str:
    if os.name == 'nt':
        command = 'pip cache dir'
    else:
        command = 'python3.12 -m pip cache dir'
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    return result.stdout.decode().strip()


def get_pypy_link(ver: str, plat='win64') -> str:
    url = 'https://downloads.python.org/pypy/pypy{py_ver}-v{pypy_ver}-{plat}.{ext}'

    if plat in ['win64', 'src']:
        ext = 'zip'
    else:
        ext = 'tar.bz2'

    return url.format(py_ver=ver, pypy_ver=PYTHON_TO_PYPY[ver], plat=plat, ext=ext)


def is_good_whl(filename: str) -> bool:
    bl = ['nightly']
    for i in bl:
        if i in filename:
            return False
    return filename.endswith('.whl')


def get_whl_list() -> list:
    pkgs = []
    whl_path = f'{whl_dir}/{whl_file}'
    with open(whl_path, 'r', encoding='utf-8') as f:
        whl_html = f.read()

    for line in whl_html.split('\n'):
        if '<a' in line:
            a_tag_open_start = line.find('<a href="')
            a_tag_open_end = line.find('">')
            a_tag_close = line.find('</a>')
            pkg_filename = line[a_tag_open_end + len('">'):a_tag_close]
            pkg_url = line[a_tag_open_start + len('<a href="'):a_tag_open_end]
            pkgs.append((pkg_filename, pkg_url))

    return pkgs


def popen_reader_linux(p: subprocess.Popen, pbar: tqdm = None) -> tuple:
    sel = selectors.DefaultSelector()
    sel.register(p.stdout, selectors.EVENT_READ)
    sel.register(p.stderr, selectors.EVENT_READ)
    result = ''
    error = ''

    if pbar:
        print_func = pbar.write
    else:
        print_func = print

    done = False
    while not done:
        for key, _ in sel.select():
            data = key.fileobj.read1().decode()
            if not data:
                done = True
                break
            if key.fileobj is p.stdout:
                result += data
                print_func(data, end="")
            else:
                error += data
                print_func(data, end="", file=sys.stderr)

    p.wait()
    return result, error


def popen_reader_win(p: subprocess.Popen, pbar: tqdm = None) -> tuple:
    if pbar:
        print_func = pbar.write
    else:
        print_func = print

    result, error = p.communicate()
    result = result.decode()
    error = error.decode()
    print_func(result, end="")
    print_func(error, end="", file=sys.stderr)

    return result, error


def popen_reader(p: subprocess.Popen, pbar: tqdm = None) -> tuple:
    if os.name == 'nt':
        return popen_reader_win(p, pbar)
    else:
        return popen_reader_linux(p, pbar)


def get_load() -> float:
    return psutil.getloadavg()[0]
