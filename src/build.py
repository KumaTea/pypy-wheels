import os
import sys
import argparse
import subprocess
from config import *
from tqdm import tqdm


arg = argparse.ArgumentParser()
arg.add_argument('-V', '--ver', help='pypy version')
arg.add_argument('-s', '--since', help='start from this package')
arg.add_argument('-u', '--until', help='end at this package')
arg.add_argument('-O', '--only', help='only build this package')
args = arg.parse_args()


def build(ver: str, py_path: str, plat: str = 'win', since: str = None, until: str = None, only: str = None):
    if ver not in build_versions:
        print(f'pypy {ver} not found')
        exit(1)
    # if 'win' in plat:
    #     check_pypy(ver)

    print(f'Building wheels for pypy {ver}...')
    # packages = []
    success = []
    failed = []

    if only:
        print(f'Building {only}...')
        packages = [only]
        until_index = 1
    else:
        with open('../packages.txt', 'r') as f:
            packages = f.read().splitlines()

        if 'win' in plat:
            with open('../pkgs_win.txt', 'r') as f:
                packages = packages + f.read().splitlines()
        elif 'linux' in plat:
            with open('../pkgs_linux.txt', 'r') as f:
                packages = packages + f.read().splitlines()

        with open('../pkgs_in.txt', 'r') as f:
            packages = packages + f.read().splitlines()

        # packages = list(set(packages))
        if since:
            index = packages.index(since)
            if index > 0:
                packages = ['NotARealPackage'] * index + packages[index:]

        if until:
            if until.isdigit():
                until_index = int(until)
            else:
                until_index = packages.index(until)
        else:
            until_index = len(packages)

    pbar = tqdm(packages)
    count = 0
    for pkg in pbar:
        if pkg == 'NotARealPackage':
            continue
        pbar.set_description(f'S: {len(success)}, F: {len(failed)}, C: {pkg}')
        flags = ''
        if only:
            flags = '--force-reinstall'
        command = (f'{py_path} -m '
                   f'pip install -U {flags} '
                   f'{pkg} '
                   f'--extra-index-url https://pypy.kmtea.eu/simple')
        try:
            result = subprocess.run(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if ('error' not in result.stderr.decode('utf-8').lower()) or (f'Successfully installed {pkg}'.lower() in result.stdout.decode('utf-8').lower()):
                success.append(pkg)
                count += 1
            else:
                failed.append(pkg)
                print('######### FAILURE #########')
                print(f'{pkg=}')
                print(result.stdout.decode('utf-8'))
                print('########## ERROR ##########')
                print(result.stderr.decode('utf-8'))
                print('##########  END  ##########')

            current_index = packages.index(pkg)
            if current_index >= until_index:
                raise KeyboardInterrupt

            if count >= 100:
                print('Built 100 packages. Uninstall all.')
                uninst_all(ver, py_path, plat)
        except KeyboardInterrupt:
            print('Exiting...')
            print(f'{success=}')
            print(f'{failed=}')
            print(f'{pkg=}')
            sys.exit(1)
        except Exception as e:
            failed.append(pkg)
            print(e)
        finally:
            print('Cleanup...')
            uninst_all(ver, py_path, plat)

    print(f'Success: {len(success)}, Failed: {len(failed)}')
    return success, failed


def uninst_all(ver: str, py_path: str, plat: str = 'win'):
    # uninstall all packages
    if plat == 'win':
        freeze_cmd = f'{py_path} -m pip freeze'
        r = subprocess.run(freeze_cmd.split(), stdout=subprocess.PIPE)
        pkgs = r.stdout.decode('utf-8').splitlines()
        uninst_cmd = f'{py_path} -m pip uninstall -y'

        for pkg in tqdm(pkgs):
            p = subprocess.run(f'{uninst_cmd} {pkg}'.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if p.returncode != 0:
                print(p.stdout.decode('utf-8'))
                print(p.stderr.decode('utf-8'))
    else:
        uninst_cmd = f'{py_path} -m pip freeze | xargz {py_path} -m pip uninstall -y'

        p = subprocess.Popen(uninst_cmd.split(), stdout=subprocess.PIPE)
        for line in iter(p.stdout.readline, b''):
            print(line.decode('utf-8').strip())
        p.stdout.close()
        p.wait()

    if os.path.exists(f'freeze.{ver}.txt'):
        os.remove(f'freeze.{ver}.txt')
