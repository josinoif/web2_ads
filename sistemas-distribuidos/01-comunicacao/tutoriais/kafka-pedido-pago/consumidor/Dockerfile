FROM python:3.12-alpine

WORKDIR /app
COPY consumidor/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY comum/rastro.py ./
COPY consumidor/consumidor.py .

ENV PORT=8000
EXPOSE 8000

CMD ["python", "consumidor.py"]
