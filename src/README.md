# SOP Checklist

1. (pypy docker) `python3 copy_whls.py`
2. (pypy docker) `python3 build_many.py`
3. (pypy host) `cp -rvf whl /mnt/hdd/Temp/`
4. (PVE server) `chmod -R 777 /mnt/hdd/Temp/`
5. (Windows) Copy `Z:\Temp\whl` ino `E:\Cache\linux\`
6. Run `pick_uploads.py`
7. Upload wheels in `E:\Cache\linux\whl\upload` to GitHub release
8. Run `gen_whl.py`
9. Run `gen_index.py` to check PyPI conflicts
10. `git cm` & `git push`
11. Wait for GitHub Actions to finish
12. Run `sha_check.py` to check corrupted files
