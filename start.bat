@echo off

set COOKIES=
set PASSWORD=
set PORT=25100

cd src
python -m uvicorn app:app --port %PORT%
