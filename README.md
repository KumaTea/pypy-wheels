# pypy-wheels
Prebuilt PyPy wheels of the most popular packages

[![Coverage](https://shields.io/badge/python-3.7%20%7C%203.8%20%7C%203.9%20%7C%203.10-blue)](https://github.com/KumaTea/pypy-wheels/releases)

## How to use

```bash
pip install <package> --prefer-binary --extra-index-url https://pypy.kmtea.eu/simple
```

The `--prefer-binary` option is to ensure that
once the source updates, the binary will still be used.
You may dismiss it at your will.

An alternative way is to use the `--find-links` option,
which is not recommended because the size of the index is large:

```bash
pip install <package> --prefer-binary --find-links https://pypy.kmtea.eu/wheels.html
```

If you have trouble accessing GitHub Pages,
you may try the CDN hosted by CloudFlare:

```bash
pip install <package> --prefer-binary --find-links https://pypy.kmtea.eu/wheels-cdn.html
```

## Other info

I'm personally impressed by the conception and the speed of PyPy.

However, PyPy works best with pure Python but not C extensions,
making it lacks some prebuilt wheels of the most popular packages.

I have made [prebuilt wheels before](https://github.com/KumaTea/ext-whl),
so this project is not too hard for me.

## Credit

* The most popular packages index is generated by **[hugovk/top-pypi-packages](https://github.com/hugovk/top-pypi-packages)**
* Including **[Christoph Gohlke's Windows Binaries](https://www.lfd.uci.edu/~gohlke/pythonlibs/)**
* The wheels above are downloaded automatically using **[jaapvandervelde/gohlkegrabber](https://github.com/jaapvandervelde/gohlkegrabber)**'s script
