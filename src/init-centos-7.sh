#!/usr/bin/env bash
# init script for quay.io/pypa/manylinux2014_x86_64 (CentOS 7 based)


# ====== MIRROR ======

sed -e 's|^mirrorlist=|#mirrorlist=|g' -e 's|^#baseurl=http://mirror.centos.org/centos|baseurl=https://mirrors.sustech.edu.cn/centos|g' -i.bak /etc/yum.repos.d/CentOS-*.repo
yum update
yum install -y dnf
sed -e 's!^metalink=!#metalink=!g' -e 's!^#baseurl=!baseurl=!g' -e 's!https\?://download\.fedoraproject\.org/pub/epel!https://mirrors.sustech.edu.cn/epel!g' -e 's!https\?://download\.example/pub/epel!https://mirrors.sustech.edu.cn/epel!g' -i /etc/yum.repos.d/epel*.repo
/opt/python/cp312-cp312/bin/python3 -m pip config set global.index-url https://mirrors.sustech.edu.cn/pypi/web/simple
/opt/python/cp312-cp312/bin/python3 -m pip config set global.extra-index-url https://pypy.kmtea.eu/cdn

# adduser kuma
# passwd kuma
# chown -R kuma:kuma /home/kuma

# ====== TOOLS ======

dnf install -y wget nano curl sudo
usermod -aG wheel kuma
echo "kuma ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/kuma

cd /etc/yum.repos.d/
wget https://download.opensuse.org/repositories/shells:fish:release:3/CentOS_7/shells:fish:release:3.repo
cd ~
dnf update
dnf install -y fish
chsh -s /usr/bin/fish
# sudo -u kuma chsh -s /usr/bin/fish

# ====== ENV ======

sudo chown -R kuma:kuma /home/kuma
mkdir -p /root/.config/fish
sudo -u kuma mkdir -p /home/kuma/.config/fish
sudo -u kuma cat << EOF >> /home/kuma/.config/fish/config.fish
if status is-interactive
    cd ~
end

source /opt/rh/devtoolset-10/enable.fish
export PATH="/home/kuma/.cargo/bin:\$PATH"

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
ln -sf /home/kuma/.config/fish/config.fish .config/fish/config.fish

cat << EOF >> .bashrc
source /opt/rh/devtoolset-10/enable
export PATH="/home/kuma/.cargo/bin:$PATH"
EOF

sudo -i
rm -f /opt/rh/devtoolset-10/enable.fish
cat << EOF >> /opt/rh/devtoolset-10/enable.fish
export PATH=/opt/rh/devtoolset-10/root/usr/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
export MANPATH=/opt/rh/devtoolset-10/root/usr/share/man
export INFOPATH=/opt/rh/devtoolset-10/root/usr/share/info
export PCP_DIR=/opt/rh/devtoolset-10/root
export C_INCLUDE_PATH="\$C_INCLUDE_PATH:/opt/openblas/include"
export CPATH="\$CPATH:/opt/openblas/include"
export LIBRARY_PATH="\$LIBRARY_PATH:/opt/openblas/lib"
export LD_LIBRARY_PATH="\$LD_LIBRARY_PATH:/opt/openblas/lib:/opt/rh/devtoolset-10/root/usr/lib64/dyninst:/opt/rh/devtoolset-10/root/usr/lib/dyninst:/opt/rh/devtoolset-10/root/usr/lib/dyn:/opt/rh/devtoolset-10/root/usr/lib64:/opt/rh/devtoolset-10/root/usr/lib"
export PKG_CONFIG_PATH=/opt/openblas/lib/pkgconfig:/opt/rh/devtoolset-10/root/usr/lib64/pkgconfig:/usr/local/lib/pkgconfig
EOF

# ====== BUILD DEPS ======

sudo dnf install -y autogen bash ca-certificates centos-release-scl cmake curl gettext git libffi-devel libjpeg-devel nano ninja-build openssl-devel wget xz zlib-devel

# Pillow
cd /tmp
wget https://sourceforge.net/projects/libpng/files/libpng16/1.6.40/libpng-1.6.40.tar.xz/download -O libpng-1.6.40.tar.xz
tar -xJf libpng-1.6.40.tar.xz
cd libpng-1.6.40
./configure --enable-shared
make
sudo make install
cd ..
rm -rvf libpng-1.6.40 libpng-1.6.40.tar.xz

# others
sudo dnf install -y postgresql-devel libxml2-devel libxslt-devel unixODBC-devel freetds-devel

# 
# error "confluent-kafka-python requires librdkafka v2.3.0 or later.
cd /tmp
wget https://gh.kmtea.eu/https://github.com/confluentinc/librdkafka/archive/refs/tags/v2.3.0.tar.gz
tar xvzf v2.3.0.tar.gz
cd librdkafka-2.3.0
sudo ln -s /opt/python/cp312-cp312/bin/python3 /usr/bin/python3
./configure
make
sudo make install
cd ..
rm -rvf librdkafka-2.3.0 v2.3.0.tar.gz

# hdf5
# Exception: This version of h5py requires HDF5 >= 1.10.4 (got version (1, 8, 12) from environment variable or library)
cd /tmp
wget https://gh.kmtea.eu/https://github.com/HDFGroup/hdf5/releases/download/hdf5-1_12_3/hdf5-1_12_3.tar.gz
tar xvzf hdf5-1_12_3.tar.gz
cd hdfsrc
./configure --prefix=/opt/hdf5 --enable-fortran --enable-cxx
make
sudo dnf -y install gcc-c++ gcc-gfortran
sudo make install
sudo dnf -y remove gcc-c++ gcc-gfortran
cd ..
rm -rvf hdfsrc hdf5-1_12_3.tar.gz

# llvm
# RuntimeError: Building llvmlite requires LLVM 11.x.x, got '14.0.5'
sudo dnf -y install llvm11-devel
sudo ln -sf /usr/bin/llvm-config-11-64 /usr/bin/llvm-config

# openblas
# https://github.com/bgeneto/build-install-compile-openblas
export OPENBLAS_DIR=/opt/openblas
sudo mkdir $OPENBLAS_DIR
cd /tmp
wget https://gh.kmtea.eu/https://github.com/OpenMathLib/OpenBLAS/releases/download/v0.3.25/OpenBLAS-0.3.25.tar.gz
tar xvzf OpenBLAS-0.3.25.tar.gz
cd OpenBLAS-0.3.25
export USE_THREAD=1
export NUM_THREADS=64
export DYNAMIC_ARCH=0
export NO_WARMUP=1
export BUILD_RELAPACK=0
export COMMON_OPT="-O2 -march=native"
export CFLAGS="-O2 -march=native"
export FCOMMON_OPT="-O2 -march=native"
export FCFLAGS="-O2 -march=native"
make -j DYNAMIC_ARCH=0 CC=gcc FC=gfortran HOSTCC=gcc BINARY=64 INTERFACE=64 USE_OPENMP=1 LIBNAMESUFFIX=openmp
sudo make PREFIX=$OPENBLAS_DIR LIBNAMESUFFIX=openmp install
cd ..
rm -rvf OpenBLAS-0.3.25 OpenBLAS-0.3.25.tar.gz
# numpy
sudo ln -s /opt/openblas/lib/libopenblas_openmp.a /opt/openblas/lib/libopenblas.a
sudo ln -s /opt/openblas/lib/libopenblas_openmp.so /opt/openblas/lib/libopenblas.so
sudo ln -s /opt/openblas/lib/libopenblas_openmp.so.0 /opt/openblas/lib/libopenblas.so.0

# GEOS
# https://github.com/libgeos/geos/blob/main/INSTALL.md
cd /tmp
wget https://gh.kmtea.eu/https://github.com/libgeos/geos/releases/download/3.12.1/geos-3.12.1.tar.bz2
tar xvjf geos-3.12.1.tar.bz2
cd geos-3.12.1
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build .
sudo cmake --build . --target install
cd ..
rm -rvf geos-3.12.1 geos-3.12.1.tar.bz2

# arrow
# https://arrow.apache.org/install/
sudo yum install -y epel-release || sudo yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1).noarch.rpm
sudo yum install -y https://apache.jfrog.io/artifactory/arrow/centos/$(cut -d: -f5 /etc/system-release-cpe | cut -d. -f1)/apache-arrow-release-latest.rpm
sudo yum install -y --enablerepo=epel arrow-devel arrow-glib-devel

# cryptography 1
# su kuma
curl https://sh.rustup.rs -sSf | sh
# exit

# cryptography 2
# dnf remove openssl openssl-devel
wget https://www.openssl.org/source/openssl-1.1.1w.tar.gz
tar xvzf openssl-1.1.1w.tar.gz
cd openssl-1.1.1w
./config --prefix=/usr --openssldir=/etc/ssl
make
sudo make install
cd ..
rm -rvf openssl-1.1.1w.tar.gz openssl-1.1.1w
openssl version

# ====== PYTHON HEADERS ======

sudo -i
cd /tmp
wget https://gh.kmtea.eu/https://github.com/KumaTea/pypy-wheels/releases/download/2311/pypy3.10.tar.gz
wget https://gh.kmtea.eu/https://github.com/KumaTea/pypy-wheels/releases/download/2311/pypy3.9.tar.gz
wget https://gh.kmtea.eu/https://github.com/KumaTea/pypy-wheels/releases/download/2311/pypy3.8.tar.gz
tar xvzf pypy3.10.tar.gz
tar xvzf pypy3.9.tar.gz
tar xvzf pypy3.8.tar.gz
cp -rvf ./usr/* /usr/
rm -rvf usr pypy3.10.tar.gz pypy3.9.tar.gz pypy3.8.tar.gz
# rm -vf /lib64/libpypy*

sudo ldconfig
