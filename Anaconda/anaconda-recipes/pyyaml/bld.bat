set INCLUDE=%LIBRARY_INC%
set LIBPATH=%LIBRARY_LIB%
set LIB=%LIBRARY_LIB%

%PYTHON% setup.py install
if errorlevel 1 exit 1

copy %LIBRARY_BIN%\yaml.dll %SP_DIR%\
if errorlevel 1 exit 1
