@echo off
chcp 65001 >nul
echo ========================================
echo Demo3 网页采集系统 - 打包脚本
echo ========================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.11+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo ✓ Python环境正常
echo.

REM 安装依赖
echo 正在安装依赖...
pip install -r ..\requirements.txt -q
if errorlevel 1 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)
echo ✓ 依赖安装完成
echo.

REM 打包
echo 正在打包为EXE...
cd ..
pyinstaller --onefile --name "网页采集工具" --add-data "modules;modules" --add-data "config;config" --hidden-import requests --hidden-import bs4 --hidden-import pandas --hidden-import openpyxl --console scripts/process.py
if errorlevel 1 (
    echo ❌ 打包失败
    pause
    exit /b 1
)

REM 准备交付包
echo.
echo 正在准备交付包...
mkdir 交付包 2>nul
copy dist\网页采集工具.exe 交付包\ >nul
mkdir 交付包\config 2>nul
mkdir 交付包\output 2>nul
copy config\sites.json 交付包\config\ >nul

echo.
echo ========================================
echo ✅ 打包完成！
echo ========================================
echo.
echo 交付包位置: 交付包\
echo.
echo 使用说明:
echo 1. 编辑config/sites.json配置要采集的网站
echo 2. 双击运行"网页采集工具.exe"
echo 3. 结果自动保存到output目录
echo.
pause
