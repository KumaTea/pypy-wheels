import sys
import time
import argparse
import requests
import selectors
import subprocess
from config import *
from tqdm import tqdm
from tools import popen_reader, get_load


arg = argparse.ArgumentParser()
arg.add_argument('-V', '--ver', help='pypy version')
arg.add_argument('-s', '--since', help='start from this package')
arg.add_argument('-u', '--until', help='end at this package')
arg.add_argument('-O', '--only', help='only build this package')
arg.add_argument('-R', '--retry', help='retry failed packages')
args = arg.parse_args()

PYPI_MIRROR = 'mirrors.sustech.edu.cn'
PROJ_URL = 'github.com/KumaTea/pypy-wheels'
PROJ_URL_LOWER = PROJ_URL.lower()
EXTRA_INDEX_URL = 'https://pypy.kmtea.eu/simple'
EXTRA_CDN = 'https://pypy.kmtea.eu/cdn'

load_limit = WIN_MAX_LOAD if os.name == 'nt' else LINUX_MAX_LOAD


def is_success_build(pkg_name: str, output: str, error: str = None):
    pkg_name = pkg_name.lower()
    output = output.lower()
    if error:
        error = error.lower()
    for line in output.splitlines():
        if any([
            error is not None and 'error' not in error,
            'successfully installed' in line and f' {pkg_name}' in line,
            all([
                'requirement already satisfied' in line,
                f' {pkg_name}' in line,
                'from {pkg_name}' not in line,
            ]),
        ]):
            return True
    return False


def is_downloading_whl(output: str, pkg_name: str):
    """
    Downloading whl from this project's release
    means that the package has been built successfully, no need to continue.

    Why not official mirror?
    Consider oldest-supported-numpy.
    """
    output = output.lower()
    pkg_name = pkg_name.lower().replace('-', '_')
    for line in output.splitlines():
        if all([
            # downloading or cached
            PROJ_URL_LOWER in line,
            f'/{pkg_name}-' in line,
            '.whl' in line,
        ]):
            return line
    return False


def building_reader(pkg_name: str, p: subprocess.Popen, pbar: tqdm = None) -> tuple:
    if os.name == 'nt':
        return popen_reader(p, pbar)

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

            if dl_line := is_downloading_whl(result, pkg_name):
                print_func(f'🎉🎉🎉 Package {pkg_name} skipped 🎉🎉🎉\n')
                print_func('Because I found this:\n')
                print_func(dl_line)
                # kill the process
                p.terminate()
                return result, error

    p.wait()
    return result, error


def gen_packages(
        plat: str = 'win',
        since: str = None,
        only: str = None,
        retry: bool = False,
        ver: str = None
):
    if only:
        print(f'Building {only}...')
        packages = [only]
    elif retry:
        failed_logs = os.listdir(f'log/{ver}')
        packages = [i[:-4] for i in failed_logs]
    else:
        with open(f'{pkg_dir}/packages.txt', 'r') as f:
            packages = f.read().splitlines()

        if 'win' in plat:
            with open(f'{pkg_dir}/pkgs_win.txt', 'r') as f:
                packages = packages + f.read().splitlines()
        elif 'linux' in plat:
            with open(f'{pkg_dir}/pkgs_linux.txt', 'r') as f:
                packages = packages + f.read().splitlines()

        with open(f'{pkg_dir}/pkgs_in.txt', 'r') as f:
            packages = packages + f.read().splitlines()

        # packages = list(set(packages))
        if since:
            if since.isdigit():
                index = int(since)
            else:
                index = packages.index(since)
            if index > 0:
                packages = packages[index:]

    return packages


def gen_until_index(packages: list, until: str = None, since_index: int = 0):
    """
    from all index to index of generated packages
    """
    if until:
        if until.isdigit():
            until_index = int(until) - since_index
        else:
            until_index = packages.index(until)
    else:
        until_index = len(packages)
    return until_index


def build(
        ver: str, py_path: str, plat: str = 'win',
        since: str = None, until: str = None,
        only: str = None,
        retry: bool = False
):
    os.makedirs(f'log/{ver}', exist_ok=True)
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)

    print(f'Building wheels for pypy {ver}...')
    packages = gen_packages(plat, since, only, retry, ver)
    all_packages = gen_packages(plat)
    success = []
    failed = []

    # init clean
    if input('Init clean? (y/n) ') == 'y':
        uninst_all(ver, py_path, plat)

    use_local_flag = ''
    try:
        r = requests.get(LOCAL_WHL_LINK)
        if r.status_code == 200:
            print('Local cache found!')
            use_local_flag = f'--find-links {LOCAL_WHL_LINK}'
    except requests.exceptions.ConnectionError:
        print('Local cache not found, nevermind.')

    force_reinstall_flag = ''
    if only:
        force_reinstall_flag = '--force-reinstall'

    extra_index_flag = ''
    if os.name == 'nt':
        pip_conf_path = os.path.join(os.environ['APPDATA'], 'pip/pip.ini')
    else:
        pip_conf_path = os.path.join(os.path.expanduser('~'), '.config/pip/pip.conf')
    if os.path.exists(pip_conf_path):
        with open(pip_conf_path, 'r') as f:
            pip_conf = f.read()
        if EXTRA_CDN not in pip_conf:
            extra_index_flag = f'--extra-index-url {EXTRA_INDEX_URL}'

    # since_index is index of all packages
    if since:
        if since.isdigit():
            since_index = int(since)
        else:
            since_index = all_packages.index(since)
    else:
        since_index = 0

    # until_index is index of generated packages
    until_index = gen_until_index(packages, until, since_index)

    env = os.environ
    pbar = tqdm(packages, initial=since_index, total=len(packages) + since_index)
    count = 0
    for pkg in pbar:
        pbar.set_description(f'S: {len(success)}  F: {len(failed)}  C: {pkg}')
        command = (
            f'{py_path} -m '
            f'pip install -U -v '
            f'{pkg} '
            f'{force_reinstall_flag} '
            f'{extra_index_flag} '
            f'{use_local_flag}'
        )
        load = get_load()
        while load > load_limit:
            pbar.write(f'Load: {load:.2f} > {load_limit}, waiting...')
            time.sleep(60)
            load = get_load()
        pbar.write(f'Load: {load:.2f} < {load_limit}, start!')
        try:
            pbar.write(f'Now running {command}')
            p = subprocess.Popen(
                command.split(),
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                env=env,  # ensure windows' Visual C++ build tools and conda env
            )
            result, error = building_reader(pkg, p, pbar)

            error_log = f'log/{ver}/{pkg}.log'
            if is_success_build(pkg, result, error):
                success.append(pkg)
                pbar.write(f'\n\n🎉 {pkg} 🎉\n\n')
                count += 1
                if os.path.isfile(error_log):
                    os.remove(error_log)
                    pbar.write(f'Removed {error_log}')
            else:
                failed.append(pkg)
                # pbar.write(result)
                pbar.write('######### FAILURE #########')
                pbar.write(f'{pkg=}')
                # if isinstance(command, list):
                #     command = ' '.join(command)
                pbar.write(f'{command=}')
                pbar.write('########## ERROR ##########')
                # pbar.write(error)
                with open(error_log, 'w', encoding='utf-8') as f:
                    f.write(result + error)
                pbar.write(f'Log saved to {error_log}')
                pbar.write('##########  END  ##########')
                pbar.write('\n')

            current_index = packages.index(pkg)
            if current_index >= until_index:
                raise KeyboardInterrupt

            if count >= 100:
                pbar.write('Built 100 packages. Uninstall all.')
                count = 0
                uninst_all(ver, py_path, plat, pbar)
            elif 'dependency conflicts' in result + error:
                pbar.write('Found dependency conflicts! Uninstall all.')
                count = 0
                uninst_all(ver, py_path, plat, pbar)
        except KeyboardInterrupt:
            pbar.write('Exiting...')
            pbar.write(f'{success=}')
            pbar.write(f'{failed=}')
            pbar.write(f'{pkg=}')
            sys.exit(1)
        except Exception as e:
            failed.append(pkg)
            pbar.write(str(e))

    pbar.write(f'Success: {len(success)}  Failed: {len(failed)}')
    return success, failed


NO_UNINST = [
    'pip', 'setuptools', 'wheel',
    'certifi', 'cffi', 'greenlet', 'hpy', 'readline', 'wrapt',
    'semantic_version',
]


def uninst_all(ver: str, py_path: str, plat: str = 'win', upper_pbar: tqdm = None):
    # uninstall all packages
    if plat == 'win':
        freeze_cmd = f'{py_path} -m pip freeze'
        r = subprocess.run(freeze_cmd.split(), stdout=subprocess.PIPE)
        pkgs = r.stdout.decode('utf-8').splitlines()
        uninst_cmd = f'{py_path} -m pip uninstall -y'

        pbar = tqdm(pkgs)
        for pkg in pbar:
            if any(pkg.startswith(f'{p}==') for p in NO_UNINST):
                continue
            p = subprocess.Popen(f'{uninst_cmd} {pkg}'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            popen_reader(p, pbar)
    else:
        uninst_cmd = f'{py_path} -m pip freeze | xargs -n 1 {py_path} -m pip uninstall -y'

        p = subprocess.Popen(uninst_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        popen_reader(p, upper_pbar)

    # ensure tools
    p = subprocess.Popen(
        f'{py_path} -m pip install'.split() + NO_UNINST,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    popen_reader(p)
