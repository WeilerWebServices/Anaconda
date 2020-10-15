#!/bin/bash

# NO_GETTEXT disables internationalization (localized message translations)
# NO_INSTALL_HARDLINKS uses symlinks which makes the package 85MB slimmer (8MB instead of 93MB!)

# pcre-feedstock recipe does not include --enable-jit
export NO_LIBPCRE1_JIT=1

# Add a place for git config files.
mkdir -p "${PREFIX}/etc"
make configure
./configure \
    --prefix="${PREFIX}" \
    --host=${HOST} \
    --with-gitattributes="${PREFIX}/etc/gitattributes" \
    --with-gitconfig="${PREFIX}/etc/gitconfig" \
    --with-libpcre1 \
    --with-iconv="${PREFIX}/lib" \
    --with-perl="${PREFIX}/bin/perl" \
    --with-tcltk="${PREFIX}/bin/tclsh"
make \
    --jobs=${CPU_COUNT} \
    NO_GETTEXT=1 \
    NO_INSTALL_HARDLINKS=1 \
    all strip install \
    ${VERBOSE_AT}

# build osxkeychain
if [[ $(uname) == "Darwin" ]]; then
  pushd contrib/credential/osxkeychain
  make -e
  cp -avf git-credential-osxkeychain $PREFIX/bin
  popd
fi

git config --system http.sslVerify true
git config --system http.sslCAPath "${PREFIX}/ssl/cacert.pem"
git config --system http.sslCAInfo "${PREFIX}/ssl/cacert.pem"

# Install completion files
mkdir -p $PREFIX/share/bash-completion/completions
cp contrib/completion/git-completion.bash $PREFIX/share/bash-completion/completions/git
