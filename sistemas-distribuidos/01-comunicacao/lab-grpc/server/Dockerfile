FROM python:3.12-slim

WORKDIR /app
COPY server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/provas.proto /proto/provas.proto
RUN python -m grpc_tools.protoc \
    -I/proto \
    --python_out=/app \
    --grpc_python_out=/app \
    /proto/provas.proto

COPY server/server.py .
COPY scripts/run-client.py /app/run-client.py
ENV PORT=50051
ENV GRPC_TARGET=grpc-server:50051
EXPOSE 50051
CMD ["python", "server.py"]
