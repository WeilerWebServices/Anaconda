"%PYTHON%" setup.py install
if errorlevel 1 exit 1

set MAIN_DIR=%RECIPE_DIR%\..

mkdir                              "%PREFIX%\etc\jupyter\custom"
xcopy /Y /E %MAIN_DIR%\custom\*    "%PREFIX%\etc\jupyter\custom"
