@echo off
REM ============================================================
REM GuiGraph 环境切换脚本
REM 用法: switch_env.bat [dev|test|prod]
REM ============================================================

if "%1"=="" (
    echo 用法: switch_env.bat ^<dev^|^test^|^prod^>
    echo 当前环境: %APP_ENV%
    exit /b 1
)

set ENV_NAME=%1

if "%ENV_NAME%"=="dev" (
    copy .env.dev .env
    echo [OK] 已切换到开发环境 (dev) -> .env.dev
) else if "%ENV_NAME%"=="test" (
    copy .env.test .env
    echo [OK] 已切换到测试环境 (test) -> .env.test
) else if "%ENV_NAME%"=="prod" (
    copy .env.prod .env
    echo [OK] 已切换到生产环境 (prod) -> .env.prod
) else (
    echo [ERROR] 未知环境: %ENV_NAME%
    echo 可选: dev, test, prod
    exit /b 1
)

echo [OK] 当前 .env 文件已更新，请重启应用使配置生效
