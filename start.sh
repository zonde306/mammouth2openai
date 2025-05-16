#!/bin/bash

export COOKIES=
export PASSWORD=
export PORT=25100

cd src
python3 -m uvicorn app:app --port ${PORT}
