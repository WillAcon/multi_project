FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# RQ escuchará la cola "batch_jobs"
# CMD ["rq", "worker", "batch_jobs", "--url", "redis://redis:6379/0"]


CMD ["python", "-u", "tasks.py"]