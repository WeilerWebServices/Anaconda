#!/bin/bash

sed -i.orig s:'@PREFIX@':"${PREFIX}":g src/fccfg.c

# So that -Wl,--as-needed works (sorted to appear before before libs)
autoreconf -vfi

# See:
# https://github.com/Homebrew/homebrew-core/blob/master/Formula/fontconfig.rb
# https://bugs.freedesktop.org/show_bug.cgi?id=105366
if [[ ${target_platform} == osx-64 ]]; then
  export UUID_CFLAGS=" "
  export UUID_LIBS=" "
  sed -i -e 's|PKGCONFIG_REQUIRES_PRIVATELY=\"\$PKGCONFIG_REQUIRES_PRIVATELY uuid\"||g' configure
  FONT_DIRS=--with-add-fonts="${PREFIX}"/fonts,/System/Library/Fonts,/Library/Fonts,~/Library/Fonts,/System/Library/Assets/com_apple_MobileAsset_Font3,/System/Library/Assets/com_apple_MobileAsset_Font4
else
  FONT_DIRS=--with-add-fonts="${PREFIX}"/fonts
fi

./configure --prefix="${PREFIX}"                \
            --enable-libxml2                    \
            --enable-static                     \
            --disable-docs                      \
            "${FONT_DIRS}"


make -j${CPU_COUNT} ${VERBOSE_AT}
make check ${VERBOSE_AT}
make install

# Remove computed cache with local fonts
rm -Rf "${PREFIX}"/var/cache/fontconfig

# Leave cache directory, in case it's needed
mkdir -p "${PREFIX}"/var/cache/fontconfig
touch "${PREFIX}"/var/cache/fontconfig/.leave
