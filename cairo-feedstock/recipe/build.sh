#!/bin/bash
if [[ ${target_platform} == osx-64 ]]; then
  rm -rf "${PREFIX}"/lib/libuuid.la "${PREFIX}"/lib/libuuid.a
  XWIN_ARGS=--without-x
else
  XWIN_ARGS=--with-x
fi
if [ $(uname -m) == x86_64 ]; then
    export ax_cv_c_float_words_bigendian="no"
fi
bash autogen.sh

find $PREFIX -name '*.la' -delete
./configure \
    --prefix="${PREFIX}" \
    --enable-warnings \
    --enable-ft \
    --enable-ps \
    --enable-pdf \
    --enable-svg \
    --disable-gtk-doc \
    $XWIN_ARGS

make -j${CPU_COUNT}
# FAIL: check-link on OS X
# Hangs for > 10 minutes on Linux
#make check -j${CPU_COUNT}
make install -j${CPU_COUNT}
find $PREFIX -name '*.la' -delete
