import os
from tools import copy_wheels
from config import LINUX_WHEEL_DIR, WIN_WHEEL_DIR


if __name__ == '__main__':
    if os.name == 'nt':
        copy_wheels(WIN_WHEEL_DIR)
    else:
        copy_wheels(LINUX_WHEEL_DIR)
