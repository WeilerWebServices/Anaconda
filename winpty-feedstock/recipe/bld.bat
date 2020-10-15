@echo off

setlocal
cd %~dp0

set GYP_ARGS=
IF "%PROCESSOR_ARCHITECTURE%"=="x86" (set MSVC_PLATFORM=Win32) else (set MSVC_PLATFORM=x64)

if "%ARCH%" == "32" (set PLATFORM=x86) else (set PLATFORM=x64)
call "%VS140COMNTOOLS%\..\..\VC\vcvarsall.bat" %PLATFORM%
set DISTUTILS_USE_SDK=1
set MSSdk=1

REM -------------------------------------------------------------------------
REM -- Copy CMakeLists.txt to src

REM curl -outf CMakeLists.txt https://raw.githubusercontent.com/conda-forge/winpty-feedstock/master/recipe/CMakeLists.txt
REM copy CMakeLists.txt src\CMakeLists.txt


REM -------------------------------------------------------------------------
REM -- Run cmake to generate MSVC project files.

cd src
curl https://raw.githubusercontent.com/conda-forge/winpty-feedstock/master/recipe/CMakeLists.txt -o CMakeLists.txt
dir

%LIBRARY_BIN%\cmake -G "NMake Makefiles" -DCMAKE_INSTALL_PREFIX:PATH="%LIBRARY_PREFIX%" -DCMAKE_BUILD_TYPE:STRING=Release
if errorlevel 1 (
    echo error: cmake failed
    exit /b 1
)

REM -------------------------------------------------------------------------
REM -- Compile the project.

nmake || (
    echo error: nmake failed
    exit /b 1
)

REM -------------------------------------------------------------------------
REM -- Install the project.

rem nmake install

copy include\winpty.h %LIBRARY_INC%
copy include\winpty_constants.h %LIBRARY_INC%

copy lib\winpty.lib %LIBRARY_LIB%
copy lib\winpty.dll %LIBRARY_BIN%
copy bin\winpty-agent.exe %LIBRARY_BIN%
copy bin\winpty-debugserver.exe %LIBRARY_BIN%
