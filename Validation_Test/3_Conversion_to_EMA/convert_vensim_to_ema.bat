@echo off
setlocal enabledelayedexpansion
REM Batch file to convert Vensim CSV output to EMA format

cd /d "%~dp0"
call "..\config.bat"

echo ========================================
echo  Convert Vensim Output to EMA Format
echo ========================================
echo.

REM Check if Vensim_Exported_Results directory exists
if not exist "Vensim_Exported_Results" (
    echo Error: Vensim_Exported_Results directory not found!
    echo.
    pause
    exit /b 1
)

REM Build list of CSV files
set count=0
for %%f in (Vensim_Exported_Results\*.csv) do (
    set /a count+=1
    set "file[!count!]=%%~nxf"
)

if %count%==0 (
    echo No CSV files found in Vensim_Exported_Results!
    echo.
    pause
    exit /b 1
)

REM Display numbered list
echo Available CSV files in Vensim_Exported_Results:
echo.
for /l %%i in (1,1,%count%) do (
    echo   %%i. !file[%%i]!
)
echo.
echo You can enter multiple numbers separated by commas (e.g., 1,2,3)
set /p choice="Enter file number(s) to convert (default=all): "
echo.

if "%choice%"=="" (
    REM Convert all files
    "%PYTHON_ENV_PATH%" convert_vensim_to_ema.py --all
) else (
    REM Convert selected files
    "%PYTHON_ENV_PATH%" convert_vensim_to_ema.py --numbers "%choice%"
)

echo.
pause
