import sys
import shutil
import psutil
import logging
import selectors
import subprocess
from config import *
from tqdm import tqdm
from versions import PYTHON_TO_PYPY
from gen_whl import saved_sha256sums


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


def copy_wheels(dst: str):
    print(f'Copying wheels for pypy...')
    pip_cache_dir = get_pip_cache_dir()
    if not os.path.exists(pip_cache_dir):
        return None

    os.makedirs(dst, exist_ok=True)
    for ver in build_versions:
        os.makedirs(f'{dst}/{ver}', exist_ok=True)
    os.makedirs(f'{dst}/none', exist_ok=True)

    # find whl file in pip cache
    whl_files = []
    for root, dirs, files in os.walk(pip_cache_dir):
        for file in files:
            if file.endswith('.whl'):
                whl_files.append((root, file))
    
    with open('../whl/wheels.html', 'r', encoding='utf-8') as f:
        whl_html = f.read()

    # copy whl file to wheel dir
    new_whl = []
    for root, file in whl_files:
        if file not in whl_html:
            new_whl.append((root, file))
        else:
            if file in saved_sha256sums:
                logging.warning(f'{file} already exists in saved_sha256sums')
            else:
                new_whl.append((root, file))
                logging.warning(f'{file} already exists in wheels.html')
                logging.warning(f'You MUST remove old file from releases!!!')

    pbar = tqdm(new_whl)
    copied_files = []
    for root, file in pbar:
        if file in copied_files:
            continue
        else:
            pbar.set_description(f'Coping {file}')
            for ver in build_versions:
                if f'pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}' in file:
                    if not (os.path.isfile(f'{dst}/{ver}/{file}') or os.path.isfile(f'{LINUX_MANY_DIR}/done/{file}')):
                        shutil.copy(f'{root}/{file}', f'{dst}/{ver}/{file}')
                        copied_files.append(file)
                        break
            if 'none' in file:
                if not (os.path.isfile(f'{dst}/none/{file}') or os.path.isfile(f'{LINUX_MANY_DIR}/done/{file}')):
                    shutil.copy(f'{root}/{file}', f'{dst}/none/{file}')
                    copied_files.append(file)

    print(f'Copied {len(copied_files)} wheels')
    return copied_files


def get_linux_dup():
    whl_path = '../whl/wheels.html'
    if os.name == 'nt':
        whl_path = './whl/wheels.html'
    pkgs = {}
    with open(whl_path, 'r', encoding='utf-8') as f:
        whl_html = f.read()

    for line in whl_html.split('\n'):
        if '<a' in line:
            open_tag_end = line.find('>')
            close_tag_start = line.find('</a>')
            pkg_filename = line[open_tag_end+1:close_tag_start]

            pkg_name = pkg_filename.split('-')[0]
            pkg_ver = pkg_filename.split('-')[1]
            pkg_pyver = pkg_filename.split('-')[2]

            if f'{pkg_name}-{pkg_ver}-{pkg_pyver}' not in pkgs:
                pkgs[f'{pkg_name}-{pkg_ver}-{pkg_pyver}'] = []
            pkgs[f'{pkg_name}-{pkg_ver}-{pkg_pyver}'].append(pkg_filename)

    for pkg in pkgs:
        if len(pkgs[pkg]) > 1:
            archs = []
            for filename in pkgs[pkg]:
                arch = filename.split('_')[-1].split('.')[0]
                plat = filename.split('_')[-2].split('-')[-1]
                if 'linux' in plat:
                    archs.append(arch)
            if len(archs) > 1 and len(list(set(archs))) == 1:
                print(pkg, pkgs[pkg])


def get_name_dup():
    whl_path = '../whl/wheels.html'
    if os.name == 'nt':
        whl_path = './whl/wheels.html'
    pkgs = {}
    with open(whl_path, 'r', encoding='utf-8') as f:
        whl_html = f.read()

    for line in whl_html.split('\n'):
        if '<a' in line:
            a_tag_open_start = line.find('<a href="')
            a_tag_open_end = line.find('">')
            a_tag_close = line.find('</a>')
            pkg_filename = line[a_tag_open_end + len('">'):a_tag_close]
            pkg_url = line[a_tag_open_start + len('<a href="'):a_tag_open_end]

            pkgs[pkg_filename] = pkgs.get(pkg_filename, []) + [pkg_url]

    for name, urls in pkgs.items():
        if len(urls) > 1:
            logging.error(f'Duplicated assets: {name}')
            for url in urls:
                logging.error(f'\tURL: {url}')


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
