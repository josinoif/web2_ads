FROM python:3.12-alpine

WORKDIR /app
COPY worker/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY comum/status_store.py comum/rabbit.py ./
COPY worker/worker.py .

CMD ["python", "worker.py"]
