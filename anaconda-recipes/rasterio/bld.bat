%PYTHON% setup.py build_ext -I%LIBRARY_INC% -L%LIBRARY_LIB% -lgdal_i
if errorlevel 1 exit 1

%PYTHON% setup.py install
if errorlevel 1 exit 1

if %PY3K%==1 (
    rd /s /q %SP_DIR%\numpy
)
