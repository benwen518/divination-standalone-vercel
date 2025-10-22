@echo off
echo 启动AI算卦服务...
echo.

REM 检查是否设置了API密钥
if "%SILICONFLOW_API_KEY%"=="" (
    echo 警告：未设置SILICONFLOW_API_KEY环境变量
    echo 请先设置API密钥：
    echo set SILICONFLOW_API_KEY=your-api-key-here
    echo.
    pause
    exit /b 1
)

REM 启动服务
python app.py

pause