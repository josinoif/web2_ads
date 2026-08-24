FROM python:3.12-alpine
WORKDIR /app
RUN apk add --no-cache librdkafka 2>/dev/null || true
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py status_store.py .
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
