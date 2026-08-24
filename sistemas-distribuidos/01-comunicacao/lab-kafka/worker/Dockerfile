FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY worker.py replay_once.py status_store.py .
CMD ["python", "worker.py"]
