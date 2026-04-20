@echo off
REM Quick setup script for GPU training environment

echo ================================================================
echo GPU Training Environment Setup
echo ================================================================
echo.
echo This script will help you set up Python 3.10/3.11 for GPU training
echo.
echo REQUIREMENTS:
echo - Python 3.10.x or 3.11.x installed at C:\Python310 or C:\Python311
echo - NVIDIA GPU drivers installed (you have RTX 2080 Ti)
echo - ~15 GB free disk space
echo.
echo ================================================================
echo.

REM Check if Python 3.10 exists
where python310 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python 3.10 found!
    set PYTHON_CMD=python310
    goto :setup
)

REM Check if Python 3.11 exists
where python311 >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python 3.11 found!
    set PYTHON_CMD=python311
    goto :setup
)

REM Check standard python command
python --version 2>&1 | find "3.10" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python 3.10 found via python command
    set PYTHON_CMD=python
    goto :setup
)

python --version 2>&1 | find "3.11" >nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] Python 3.11 found via python command
    set PYTHON_CMD=python
    goto :setup
)

echo [ERROR] Python 3.10 or 3.11 not found!
echo.
echo Please install Python 3.10 or 3.11 from:
echo https://www.python.org/downloads/
echo.
echo After installation, run this script again.
echo.
pause
exit /b 1

:setup
echo.
echo Creating virtual environment with %PYTHON_CMD%...
%PYTHON_CMD% -m venv venv_gpu

echo Activating virtual environment...
call venv_gpu\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing PyTorch with CUDA 12.1 support...
python -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo.
echo Installing other dependencies...
python -m pip install numpy pandas matplotlib tqdm einops huggingface_hub safetensors pyyaml

echo.
echo ================================================================
echo Verifying GPU setup...
echo ================================================================
python -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('GPU:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"

echo.
echo ================================================================
echo Setup Complete!
echo ================================================================
echo.
echo To start GPU training, run:
echo   call venv_gpu\Scripts\activate.bat
echo   python train_sequential.py --config configs/config_step3_test.yaml
echo.
echo Or use torchrun:
echo   torchrun --standalone --nproc_per_node=1 train_sequential.py --config configs/config_step3_test.yaml
echo.
pause
