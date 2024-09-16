# SOP Checklist

## Build

## Upload

1. (pypy docker) `python3 copy_whls.py`
2. (pypy docker) `python3 build_many.py`
3. (pypy host) `cp -rvf whl /mnt/hdd/Temp/`
4. (PVE server) `chmod -R 777 /mnt/hdd/Temp/`
5. (Windows) Copy `Z:\Temp\whl` ino `E:\Cache\linux\`
6. Run `pick_uploads.py`
7. Upload wheels in `E:\Cache\linux\whl\upload` to GitHub release
8. Run `gen_whl.py`
9. Run `gen_index.py` to check PyPI conflicts
10. Run `check_dup.py`
11. `git cm` & `git push`
12. Wait for GitHub Actions to finish
13. Run `check_sha.py` to check corrupted files
