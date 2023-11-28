#!/usr/bin/env bash

# docker run -it --name deps fedora

sed -e 's|^metalink=|#metalink=|g' -e 's|^#baseurl=http://download.example/pub/fedora/linux|baseurl=https://mirrors.sustech.edu.cn/fedora|g' -i.bak /etc/yum.repos.d/*

dnf install -y pypy-devel
# find / | grep Python.h
tar -cvzf /dev/shm/pypy-7.3.tar.gz /usr/lib64/pypy-7.3

exit

# docker cp deps:/tmp/pypy-7.3.tar.gz /dev/shm/
# cd /dev/shm/
# python3 -m http.server 8080
# download it, apparently

# docker stop deps
# docker rm deps
