@echo off
chcp 65001 >nul 2>&1
title GuiGraph - Backend

echo ============================================================
echo    GuiGraph 后端服务启动
echo    http://localhost:10011
echo ============================================================
echo.

cd /d "%~dp0backend"

if not exist ".venv\Scripts\activate.bat" (
    echo [INFO] 创建 Python 虚拟环境...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo [INFO] 安装依赖...
pip install -r requirements/base.txt -q -i https://pypi.tuna.tsinghua.edu.cn/simple

echo [INFO] 启动后端服务 (port 10011)...
python -m uvicorn app.main:app --host 0.0.0.0 --port 10011 --reload
