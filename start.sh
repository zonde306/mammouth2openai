#!/bin/bash

# 你的cookie，多个用半角逗号分隔，cookie名字为auth_session，登录后获取
export COOKIES=

# 连接用的密码
export PASSWORD=

# 端口号
export PORT=25100

python3 -m uvicorn src.app:app --port ${PORT}
