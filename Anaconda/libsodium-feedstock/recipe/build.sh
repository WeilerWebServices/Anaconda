#!/bin/bash

# Reduce optimization level for linux-32, otherwise consumers of the library
# segfault somewhere in crypto_generichash_blake2b__final ()
if [[ ${HOST} =~ .*linux.* ]] && [[ ${ARCH} == 32 ]]; then
    export CFLAGS="$CFLAGS -Og"
fi

./configure --prefix=${PREFIX}
make -j${CPU_COUNT} ${VERBOSE_AT}
make check
make install
