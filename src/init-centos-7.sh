#!/usr/bin/env bash
# init script for quay.io/pypa/manylinux2014_x86_64 (CentOS 7 based)


# ====== MIRROR ======

sed -e 's|^mirrorlist=|#mirrorlist=|g' -e 's|^#baseurl=http://mirror.centos.org/centos|baseurl=https://mirrors.sustech.edu.cn/centos|g' -i.bak /etc/yum.repos.
d/CentOS-*.repo
yum update
yum install -y dnf
sed -e 's!^metalink=!#metalink=!g' -e 's!^#baseurl=!baseurl=!g' -e 's!https\?://download\.fedoraproject\.org/pub/epel!https://mirrors.sustech.edu.cn/e
pel!g' -e 's!https\?://download\.example/pub/epel!https://mirrors.sustech.edu.cn/epel!g' -i /etc/yum.repos.d/epel*.repo
/opt/python/cp312-cp312/bin/python3 -m pip config set global.index-url https://mirrors.sustech.edu.cn/pypi/web/simple

# adduser kuma
# passwd kuma

# ====== TOOLS ======

dnf install wget nano curl sudo
usermod -aG wheel kuma
echo "kuma ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/kuma

cd /etc/yum.repos.d/
wget https://download.opensuse.org/repositories/shells:fish:release:3/CentOS_7/shells:fish:release:3.repo
cd ~
dnf update
dnf install fish
chsh -s /usr/bin/fish
# sudo -u kuma chsh -s /usr/bin/fish

mkdir -p

# ====== ENV ======

cat << EOF >> .config/fish/config.fish
if status is-interactive
    cd ~
end

source /opt/rh/devtoolset-10/enable.fish
export PATH="$HOME/.cargo/bin:$PATH"

alias python='/usr/local/bin/python3.12'
alias python3='/usr/local/bin/python3.12'
alias pip='/opt/python/cp312-cp312/bin/pip'
alias pip3='/opt/python/cp312-cp312/bin/pip3'
alias e='exit 0'
alias cls='clear'
alias kuma='su kuma'
alias sudo='/usr/bin/sudo'
alias apt='dnf'
EOF

cat << EOF >> .bashrc
source /opt/rh/devtoolset-10/enable
export PATH="$HOME/.cargo/bin:$PATH"
EOF

cat << EOF >> /opt/rh/devtoolset-10/enable.fish
export PATH=/opt/rh/devtoolset-10/root/usr/bin:/opt/rh/devtoolset-10/root/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export MANPATH=/opt/rh/devtoolset-10/root/usr/share/man
export INFOPATH=/opt/rh/devtoolset-10/root/usr/share/info
export PCP_DIR=/opt/rh/devtoolset-10/root
export LD_LIBRARY_PATH=/opt/rh/devtoolset-10/root/usr/lib64:/opt/rh/devtoolset-10/root/usr/lib:/opt/rh/devtoolset-10/root/usr/lib64/dyninst:/opt/rh/devtoolset-10/root/usr/lib/dyn$export PKG_CONFIG_PATH=/opt/rh/devtoolset-10/root/usr/lib64/pkgconfig:/usr/local/lib/pkgconfig
EOF

# ====== BUILD DEPS ======

dnf install autogen bash ca-certificates centos-release-scl cmake curl gettext git libffi-devel libjpeg-devel nano ninja-build openssl-devel wget xz zlib-devel

# Pillow
wget https://sourceforge.net/projects/libpng/files/libpng16/1.6.40/libpng-1.6.40.tar.xz/download -O libpng-1.6.40.tar.xz
tar -xJf libpng-1.6.40.tar.xz
rm -f libpng-1.6.40.tar.xz
cd libpng-1.6.40
./configure --enable-shared
make
make install
cd ..
rm -rvf libpng-1.6.40

# others
yes | dnf install geos-devel hdf5-devel postgresql-devel openblas-devel arrow-devel llvm14-devel
ln -s /usr/bin/llvm-config-14 /usr/bin/llvm-config

# cryptography 1
curl https://sh.rustup.rs -sSf | sh
export PATH="$HOME/.cargo/bin:$PATH"

# cryptography 2
# dnf remove openssl openssl-devel
wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz
tar xvzf openssl-1.1.1w.tar.gz
cd openssl-1.1.1w
./config --prefix=/usr --openssldir=/etc/ssl
make
make install
ldconfig
cd ..
rm -rvf openssl-1.1.1w.tar.gz openssl-1.1.1w
openssl version

# ====== PYTHON HEADERS ======

cd /dev/shm/
wget https://github.com/KumaTea/pypy-wheels/releases/download/2311/pypy-7.3.tar.gz
tar xvzf pypy-7.3.tar.gz
mv ./usr/lib64/pypy-7.3 /usr/lib64/
rm -rvf usr pypy-7.3.tar.gz
