FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && pip install --no-cache-dir -r requirements-dev.txt
ENV PYTHONUNBUFFERED=1
EXPOSE 5000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "ai.server_fastapi:app", "-b", "0.0.0.0:5000", "--workers", "1"]
