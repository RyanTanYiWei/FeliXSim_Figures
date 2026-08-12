@echo off
setlocal enabledelayedexpansion
REM Batch file to run generate_setup_files.py

cd /d "%~dp0"
call "..\config.bat"

echo ========================================
echo  Generate Vensim Sensitivity Files
echo ========================================
echo.

REM Build list of CSV files
set count=0
for %%f in (*.csv) do (
    set /a count+=1
    set "file[!count!]=%%~nxf"
)

if %count%==0 (
    echo No CSV files found!
    echo.
    pause
    exit /b 1
)

REM Display numbered list
echo Available CSV files:
echo.
for /l %%i in (1,1,%count%) do (
    echo   %%i. !file[%%i]!
)
echo.
echo You can enter multiple numbers separated by commas (e.g., 1,2,3)
set /p choice="Enter file number(s) to process (default=all): "
echo.

set /p numexp="Enter the number of experiments (default: 10): "

if "%numexp%"=="" (
    set numexp=10
)

echo.

if "%choice%"=="" (
    REM Process all files
    "%PYTHON_ENV_PATH%" generate_setup_files.py --all --experiments %numexp%
) else (
    REM Process selected files
    "%PYTHON_ENV_PATH%" generate_setup_files.py --numbers "%choice%" --experiments %numexp%
)

echo.
pause
