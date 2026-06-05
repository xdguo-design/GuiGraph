@echo off
chcp 65001 >nul 2>&1
title GuiGraph - Frontend

echo ============================================================
echo    GuiGraph 前端服务启动
echo    http://localhost:10010
echo ============================================================
echo.

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo [INFO] 安装前端依赖...
    npm install
)

echo [INFO] 启动前端服务 (port 10010)...
npm run dev
