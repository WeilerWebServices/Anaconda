mkdir build
cd build

set "CFLAGS=%CFLAGS% /DUNITY_EXCLUDE_STDINT_H /DUNITY_POINTER_WIDTH=64"
set "CXXFLAGS=%CXXFLAGS% /DUNITY_EXCLUDE_STDINT_H /DUNITY_POINTER_WIDTH=64"

cmake -G "NMake Makefiles" -D ENABLE_DRAFTS=OFF -D WITH_PERF_TOOL=OFF -D ZMQ_BUILD_TESTS=ON -D ENABLE_CPACK=OFF -D CMAKE_BUILD_TYPE=Release -D CMAKE_INSTALL_PREFIX=%LIBRARY_PREFIX% -DWITH_LIBSODIUM=ON ..
if errorlevel 1 exit 1
nmake install
if errorlevel 1 exit 1

:: Copy of dll and import library on windows (required by pyzmq)
copy /y %LIBRARY_BIN%\libzmq-mt-4*.dll /b %LIBRARY_BIN%\libzmq.dll
if errorlevel 1 exit 1
copy /y %LIBRARY_LIB%\libzmq-mt-4*.lib /b %LIBRARY_LIB%\libzmq.lib
if errorlevel 1 exit 1

ctest -C Release -V
if errorlevel 1 exit 1
