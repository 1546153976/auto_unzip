@echo off
chcp 65001 >nul
title 构建U15萝莉自动解压工具

echo 正在构建U15萝莉自动解压工具...
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.7或更高版本
    pause
    exit /b 1
)

REM 安装PyInstaller
echo 检查PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 错误: PyInstaller安装失败
        pause
        exit /b 1
    )
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo 错误: 依赖包安装失败
    pause
    exit /b 1
)

REM 构建exe
echo 开始构建exe文件...
pyinstaller --onefile --windowed --name="U15萝莉自动解压工具" --add-data="7z;7z" main.py

if errorlevel 1 (
    echo 错误: 构建失败
    pause
    exit /b 1
)

echo.
echo 构建完成！
echo exe文件位置: dist\U15萝莉自动解压工具.exe
echo.

pause 