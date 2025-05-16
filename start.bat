@echo off

REM 你的cookie，多个用半角逗号分隔，cookie名字为auth_session，登录后获取
set COOKIES=你的cookie填这里

REM 连接用的密码
set PASSWORD=

REM 端口号
set PORT=25100

cd src
python -m uvicorn app:app --port %PORT%
