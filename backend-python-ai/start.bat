@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: MEK-AI Python服务启动脚本 (Windows)

:: 颜色定义
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

:: 打印带颜色的消息
echo %BLUE%[INFO]%NC% 启动 MEK-AI Python 服务...

:: 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%[ERROR]%NC% Python未安装或不在PATH中
    pause
    exit /b 1
)

:: 检查虚拟环境
if "%VIRTUAL_ENV%"=="" (
    echo %YELLOW%[WARNING]%NC% 不在虚拟环境中
    echo.
    set /p choice="是否要创建并激活虚拟环境？(y/n): "
    
    if /i "!choice!"=="y" (
        echo %BLUE%[INFO]%NC% 创建虚拟环境...
        python -m venv venv
        
        echo %BLUE%[INFO]%NC% 激活虚拟环境...
        call venv\Scripts\activate.bat
        
        echo %GREEN%[SUCCESS]%NC% 虚拟环境已激活
    ) else (
        echo %YELLOW%[WARNING]%NC% 继续使用系统Python环境
    )
) else (
    echo %GREEN%[SUCCESS]%NC% 已在虚拟环境中: %VIRTUAL_ENV%
)

:: 安装依赖
echo %BLUE%[INFO]%NC% 检查并安装依赖...

if not exist "requirements.txt" (
    echo %RED%[ERROR]%NC% requirements.txt 文件不存在
    pause
    exit /b 1
)

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo %GREEN%[SUCCESS]%NC% 依赖安装完成

:: 检查环境变量
echo %BLUE%[INFO]%NC% 检查环境变量...

if not exist ".env" (
    echo %YELLOW%[WARNING]%NC% .env 文件不存在，从模板创建
    
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo %BLUE%[INFO]%NC% 请编辑 .env 文件配置API密钥和其他设置
        echo %YELLOW%[WARNING]%NC% 需要配置 OPENAI_API_KEY 等关键设置
        pause
        exit /b 0
    ) else (
        echo %RED%[ERROR]%NC% .env.example 文件不存在
        pause
        exit /b 1
    )
) else (
    echo %GREEN%[SUCCESS]%NC% 环境变量文件存在
)

:: 创建必要目录
echo %BLUE%[INFO]%NC% 创建必要的目录...

if not exist "data\uploads" mkdir "data\uploads"
if not exist "data\vector_db" mkdir "data\vector_db"
if not exist "logs" mkdir "logs"

echo %GREEN%[SUCCESS]%NC% 目录创建完成

:: 启动服务
echo %BLUE%[INFO]%NC% 启动 MEK-AI Python 服务...
echo.

:: 设置环境变量
set "PYTHONPATH=%CD%;%PYTHONPATH%"

:: 启动服务
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --log-level info

:: 如果服务退出，显示错误
if errorlevel 1 (
    echo %RED%[ERROR]%NC% 服务启动失败
    pause
    exit /b 1
)

endlocal