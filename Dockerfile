FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

WORKDIR /app/src

EXPOSE 25100

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "25100"]