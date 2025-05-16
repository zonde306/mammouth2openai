@echo off

REM 你的cookie，多个用半角逗号分隔，cookie名字为auth_session，登录后获取
export COOKIES=

REM 连接用的密码
export PASSWORD=

REM 端口号
set PORT=25100

python -m uvicorn src.app:app --port %PORT%
