#!/usr/bin/env bash

# When using cross-compilers, they are installed into the build prefix, which isn't
# the same as ${PREFIX} (which is the host prefix). The activate scripts do not set
# *any* -L or -I flags (but perhaps they should, checking for cross or not?).
# Finally, the Python _sysconfig module does contain prefix-replacement values such
# as -L/opt/anaconda1anaconda2anaconda3/lib, but again, those get replaced with the
# build prefix as that is where they get installed.
# Here, we add these flags before any existing CFLAGS so that host headers and libs
# get found before build headers and libs though I have not verified that distutils
# doesn't put its values first. Cross-compilation is workable but with rough edges.
# I need a plan to file those down.
CFLAGS="-I${PREFIX}/include -L${PREFIX}/lib "${CFLAGS} \
  ${PYTHON} setup.py install --single-version-externally-managed --record record.txt
