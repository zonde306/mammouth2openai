@echo off

REM ���cookie������ð�Ƕ��ŷָ���cookie����Ϊauth_session����¼���ȡ
set COOKIES=���cookie������

REM �����õ�����
set PASSWORD=

REM �˿ں�
set PORT=25100

cd src
python -m uvicorn app:app --port %PORT%
