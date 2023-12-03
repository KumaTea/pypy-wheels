import sys
import shutil
import psutil
import logging
import selectors
import subprocess
from config import *
from tqdm import tqdm
from gen_whl import saved_sha256sums
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
            if file.endswith('.whl'):
                whl_files.append((root, file))
    
    with open('../whl/wheels.html', 'r', encoding='utf-8') as f:
        whl_html = f.read()

    logging.info('get new wheels')
    new_whl = []
    for root, file in whl_files:
        if file not in whl_html:
            new_whl.append((root, file))
        else:
            if file in saved_sha256sums:
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


def get_plat_dup():
    pkgs = {}
    whl_list = get_whl_list()

    for pair in whl_list:
        file, url = pair
        assert file.count('-') == 4, f'{file} has a wired name!'
        name, ver, pv_ver, abi, plat = file.split('-')

        if name not in pkgs:
            pkgs[name] = {}
        if ver not in pkgs[name]:
            pkgs[name][ver] = {}
        if pv_ver not in pkgs[name][ver]:
            pkgs[name][ver][pv_ver] = {}

        # skip abi
        if 'linux' in plat:
            os_type = 'linux'
        elif 'win' in plat:
            os_type = 'win'
        else:
            os_type = 'none'
        if os_type not in pkgs[name][ver][pv_ver]:
            pkgs[name][ver][pv_ver][os_type] = {}

        arch_list = ['x86_64', 'amd64', 'aarch64']
        for i in arch_list:
            if i in plat:
                arch = i
                break
        else:
            arch = 'any'
        if arch not in pkgs[name][ver][pv_ver][os_type]:
            pkgs[name][ver][pv_ver][os_type][arch] = []

        pkgs[name][ver][pv_ver][os_type][arch].append(file)

    for pkg in pkgs:
        for ver in pkgs[pkg]:
            for pv_ver in pkgs[pkg][ver]:
                for os_type in pkgs[pkg][ver][pv_ver]:
                    for arch in pkgs[pkg][ver][pv_ver][os_type]:
                        if len(pkgs[pkg][ver][pv_ver][os_type][arch]) > 1:
                            logging.error(f'Duplicated assets: {pkg=} {ver=} {pv_ver=} {os_type=} {arch=}')
                            for file in pkgs[pkg][ver][pv_ver][os_type][arch]:
                                logging.error(f'\tURL: {file}')

    return pkgs


def get_exact_dup():
    pkgs = {}
    whl_list = get_whl_list()

    for pair in whl_list:
        file, url = pair
        pkg_filename = file
        pkg_url = url

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
