#!/usr/bin/env bash

# docker run -it --name deps fedora

sed -e 's|^metalink=|#metalink=|g' -e 's|^#baseurl=http://download.example/pub/fedora/linux|baseurl=https://mirrors.sustech.edu.cn/fedora|g' -i.bak /etc/yum.repos.d/*

dnf install -y pypy3.10-devel
# find / | grep Python.h
# tar -cvzf /dev/shm/pypy-7.3.tar.gz /usr/lib64/pypy-7.3
cd /tmp
mkdir -p usr/lib/
mv /usr/lib/pypy* usr/lib/
mkdir -p usr/include/
mv /usr/include/pypy* usr/include/
mkdir -p usr/lib64
# mv /usr/lib64/*pypy* usr/lib64/
tar -cvzf pypy3.10.tar.gz usr

exit

# do it again for 3.9
# use fedora:37 for 3.8


# docker cp deps:/tmp/pypy3.10.tar.gz /dev/shm/
# cd /dev/shm/
# python3 -m http.server 8080
# download it, apparently

# docker stop deps
# docker rm deps
