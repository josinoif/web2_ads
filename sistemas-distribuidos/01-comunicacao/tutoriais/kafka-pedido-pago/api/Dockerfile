FROM python:3.12-alpine

WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY comum/rastro.py ./
COPY api/app.py .
COPY scripts/lab.py .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "app.py"]
