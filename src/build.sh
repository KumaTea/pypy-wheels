# build script for linux

set -ex

HOST_PYTHON='/opt/python/cp312-cp312/bin/python3'

BUILD_VER=$1


# install deps
$HOST_PYTHON -m pip install -r requirements.txt

# build
$HOST_PYTHON build_linux.py --ver "$BUILD_VER"
