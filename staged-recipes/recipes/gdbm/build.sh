#!/bin/bash

./configure --prefix=${PREFIX}       \
            --host=${HOST}           \
            --disable-static         \
            --enable-libgdbm-compat
make
make check
make install
