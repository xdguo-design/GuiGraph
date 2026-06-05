@echo off
chcp 65001 >nul 2>&1
title GuiGraph - 版本变更管理系统

echo ============================================================
echo    GuiGraph - 版本变更管理系统 启动脚本
echo ============================================================
echo.

REM ===== 检查 Python =====
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM ===== 检查 Node.js =====
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] 未找到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [1/4] 初始化后端虚拟环境...
if not exist "backend\.venv\Scripts\activate.bat" (
    echo        创建 Python 虚拟环境...
    cd backend
    python -m venv .venv
    cd ..
)
echo        [OK] 虚拟环境已就绪

echo.
echo [2/4] 安装后端依赖...
call backend\.venv\Scripts\activate.bat
pip install -r backend\requirements\base.txt -q
echo        [OK] 后端依赖已安装

echo.
echo [3/4] 安装前端依赖...
if not exist "frontend\node_modules" (
    echo        运行 npm install...
    cd frontend
    call npm install
    cd ..
) else (
    echo        [OK] 前端依赖已存在
)

echo.
echo [4/4] 启动服务...
echo.
echo ============================================================
echo    后端服务: http://localhost:10011
echo    后端文档: http://localhost:10011/docs
echo    前端服务: http://localhost:10010
echo ============================================================
echo.
echo    按 Ctrl+C 停止所有服务
echo.

REM ===== 启动后端 =====
start "GuiGraph-Backend" cmd /c "cd /d backend && call .venv\Scripts\activate.bat && python -m uvicorn app.main:app --host 0.0.0.0 --port 10011 --reload"

REM ===== 等待后端启动 =====
timeout /t 3 /nobreak >nul

REM ===== 启动前端 =====
start "GuiGraph-Frontend" cmd /c "cd /d frontend && npm run dev"

echo.
echo [OK] 所有服务已启动!
echo      后端窗口: GuiGraph-Backend
echo      前端窗口: GuiGraph-Frontend
echo.
echo      关闭此窗口不会停止服务，请关闭对应的命令行窗口来停止服务。
echo.
pause
