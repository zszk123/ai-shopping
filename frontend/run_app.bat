@echo off
chcp 65001 >nul
echo ========================================
echo   AI智能比价助手 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] 正在检查Flutter环境...
E:\flutter\flutter\bin\flutter --version
if %errorlevel% neq 0 (
    echo ❌ Flutter环境异常！请检查路径：E:\flutter\flutter
    pause
    exit /b 1
)
echo ✅ Flutter环境正常
echo.

echo [2/3] 正在安装项目依赖...
E:\flutter\flutter\bin\flutter pub get
if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败！
    pause
    exit /b 1
)
echo ✅ 依赖安装完成
echo.

echo [3/3] 正在启动应用（Windows桌面版）...
echo.
E:\flutter\flutter\bin\flutter run -d windows

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ 应用启动成功！
    echo ========================================
) else (
    echo.
    echo ========================================
    echo   ❌ 启动失败，错误代码: %errorlevel%
    echo ========================================
)

pause

