@echo off

# ���cookie������ð�Ƕ��ŷָ���cookie����Ϊauth_session����¼���ȡ
export COOKIES=

# �����õ�����
export PASSWORD=

REM �˿ں�
set PORT=25100

python -m uvicorn app:app --port %PORT%
