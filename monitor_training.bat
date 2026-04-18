@echo off
REM Monitor GPU training progress in real-time

echo ================================================================
echo Kronos GPU Training Monitor
echo ================================================================
echo.
echo This script will monitor:
echo 1. GPU utilization (nvidia-smi)
echo 2. Training logs (last 20 lines)
echo.
echo Press Ctrl+C to stop monitoring
echo ================================================================
echo.

:loop
cls
echo [%date% %time%]
echo.
echo ==================== GPU STATUS ====================
nvidia-smi --query-gpu=index,name,temperature.gpu,utilization.gpu,memory.used,memory.total --format=csv
echo.
echo ==================== TRAINING LOG (Last 20 lines) ====================
powershell -Command "Get-Content 'outputs\finetuned_models\test_finetune_run\logs\tokenizer_training_rank_0.log' -Tail 20 -ErrorAction SilentlyContinue"
echo.
echo ================================================================
echo Auto-refreshing every 5 seconds... Press Ctrl+C to stop
echo ================================================================

timeout /t 5 /nobreak >nul
goto loop
