:: source to VS Build Tools

%comspec% /k "E:\Tools\VS\VC\Auxiliary\Build\vcvars64.bat"

:: conda create --prefix "E:\Cache\pypy\conda" python=3.12

conda activate "E:\Cache\pypy\conda"

:: conda install tqdm requests
:: conda install mkl mkl-include
:: conda install rust
:: conda install zlib libjpeg-turbo libpng

cd /d "D:\GitHub\pypy-wheels\src"

:: python build_win.py --ver 3.10
