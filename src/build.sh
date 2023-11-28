# build script for linux

set -ex

HOST_PYTHON='/opt/python/cp312-cp312/bin/python3'

BUILD_VER=""
BUILD_SINCE=""
BUILD_UNTIL=""
BUILD_ONLY=""

while getopts ":V:s:u:O:" opt; do
  case $opt in
    V) BUILD_VER="$OPTARG"
    ;;
    s) BUILD_SINCE="$OPTARG"
    ;;
    u) BUILD_UNTIL="$OPTARG"
    ;;
    O) BUILD_ONLY="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

while getops -l "version:,since:,until:,only:" opt; do
  case $opt in
    version) BUILD_VER="$OPTARG"
    ;;
    since) BUILD_SINCE="$OPTARG"
    ;;
    until) BUILD_UNTIL="$OPTARG"
    ;;
    only) BUILD_ONLY="$OPTARG"
    ;;
    \?) echo "Invalid option -$OPTARG" >&2
    ;;
  esac
done

# install deps
$HOST_PYTHON -m pip install -r requirements.txt

# build
$HOST_PYTHON build_linux.py --ver "$BUILD_VER" --since "$BUILD_SINCE" --until "$BUILD_UNTIL" --only "$BUILD_ONLY"
