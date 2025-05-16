# 设置环境变量
$env:COOKIES = ""
$env:PASSWORD = ""
$env:PORT = "25100"

# 切换到 src 目录
Set-Location src

# 启动 Python 应用
python -m uvicorn app:app --port $env:PORT

# 暂停，等待任意键
Write-Host "按任意键继续..."
$Host.UI.RawUI.ReadKey("IncludeKeyDown") | Out-Null