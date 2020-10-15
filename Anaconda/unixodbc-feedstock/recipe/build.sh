#!/bin/bash

set -e
set -x

autoreconf -vfi

./configure --prefix=${PREFIX}  \
            --build=${BUILD} \
            --enable-editline=yes \
            --sysconfdir=/etc
make -j${CPU_COUNT} ${VERBOSE_AT}
make install
