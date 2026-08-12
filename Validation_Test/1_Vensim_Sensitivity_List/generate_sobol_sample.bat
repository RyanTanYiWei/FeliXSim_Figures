@echo off
setlocal enabledelayedexpansion
REM Batch file to run the Sobol sample generation script

cd /d "%~dp0"
call "..\config.bat"

echo ========================================
echo  Generate Sobol Samples
echo ========================================
echo.
echo NOTE: Sobol sampling generates N x (D+2) samples total,
echo where N is your input and D is the number of parameters.
echo Example: 1000 samples with 13 parameters = 15000 total samples
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

set /p numsamples="Enter base N for Sobol samples (default: 1024): "

if "%numsamples%"=="" (
    set numsamples=1024
)

echo.

if "%choice%"=="" (
    REM Process all files
    "%PYTHON_ENV_PATH%" generate_sobol_sample.py --all --samples %numsamples%
) else (
    REM Process selected files
    "%PYTHON_ENV_PATH%" generate_sobol_sample.py --numbers "%choice%" --samples %numsamples%
)

echo.
pause
