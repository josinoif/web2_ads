FROM python:3.12-alpine
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY common.py app.py ./
ENV PORT=8000
EXPOSE 8000
CMD ["python", "app.py"]
