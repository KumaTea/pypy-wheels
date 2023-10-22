import os
import shutil
from tqdm import tqdm


LINUX_WHEELS_DIR = r'E:\Cache\linux\whl'
LINUX_WHEELS_NONE_DIR = r'E:\Cache\linux\whl\none'
LINUX_WHEELS_MANY_DIR = r'E:\Cache\linux\whl\many'
LINUX_WHEELS_MANY_ORIGIN_DIR = r'E:\Cache\linux\whl\many\done'

CURRENT_INDEX = r'D:\GitHub\pypy-wheels\whl\wheels.html'

TO_UPLOAD = r'E:\Cache\linux\whl\upload'

VERS = ['3.7', '3.8', '3.9', '3.10']

if __name__ == '__main__':
    os.makedirs(TO_UPLOAD, exist_ok=True)
    os.makedirs(os.path.join(TO_UPLOAD, 'nomany'), exist_ok=True)
    for ver in VERS:
        os.makedirs(os.path.join(TO_UPLOAD, ver), exist_ok=True)

    with open(CURRENT_INDEX, 'r', encoding='utf-8') as f:
        current_index = f.read()

    none_wheels = os.listdir(LINUX_WHEELS_NONE_DIR)
    for wheel in tqdm(none_wheels):
        if wheel not in current_index:
            shutil.move(
                os.path.join(LINUX_WHEELS_NONE_DIR, wheel),
                os.path.join(TO_UPLOAD, wheel)
            )

    origin_wheels = os.listdir(LINUX_WHEELS_MANY_ORIGIN_DIR)
    for wheel in tqdm(origin_wheels):
        done = False
        pkg_name = wheel.split('-')[0]
        pkg_ver = wheel.split('-')[1]
        pkg_python = wheel.split('-')[2]
        for ver in VERS:
            ver_wheels = os.listdir(os.path.join(LINUX_WHEELS_MANY_DIR, ver))
            for ver_wheel in ver_wheels:
                if pkg_name in ver_wheel and pkg_ver in ver_wheel and pkg_python in ver_wheel:
                    if ver_wheel not in current_index:
                        done = True
                        shutil.move(
                            os.path.join(LINUX_WHEELS_MANY_ORIGIN_DIR, wheel),
                            os.path.join(TO_UPLOAD, ver, wheel)
                        )
                        break
        if not done:
            shutil.move(
                os.path.join(LINUX_WHEELS_MANY_ORIGIN_DIR, wheel),
                os.path.join(TO_UPLOAD, 'nomany', wheel)
            )

    for wheel in tqdm(os.listdir(os.path.join(TO_UPLOAD, 'nomany'))):
        for ver in VERS:
            if f'pp{ver.replace(".", "")}-pypy{ver.replace(".", "")}' in wheel:
                shutil.move(
                    os.path.join(TO_UPLOAD, 'nomany', wheel),
                    os.path.join(TO_UPLOAD, ver, wheel)
                )
                break
