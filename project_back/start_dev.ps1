# 启动开发服务器脚本
# 使用方法: .\start_dev.ps1

Write-Host "正在启动开发服务器..." -ForegroundColor Green

# 检查虚拟环境是否存在
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "虚拟环境未找到，正在创建..." -ForegroundColor Yellow
    python -m venv .venv
    
    Write-Host "正在安装依赖..." -ForegroundColor Yellow
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install --only-binary :all: -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
}

# 检查 .env 文件是否存在
if (-not (Test-Path ".env")) {
    Write-Host "未找到 .env 文件，从模板复制..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "已创建 .env 文件，请编辑配置后重新运行此脚本" -ForegroundColor Yellow
    Write-Host "需要修改: DATABASE_URL, JWT_SECRET_KEY" -ForegroundColor Cyan
    exit
}

Write-Host "启动服务: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API文档: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "按 Ctrl+C 停止服务" -ForegroundColor Yellow

# 启动服务
.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
