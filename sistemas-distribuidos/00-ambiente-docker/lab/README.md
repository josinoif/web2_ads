# Lab mínimo — ambiente de experimentação

Três nós HTTP idênticos + Redis. Detalhes e roteiro: [../README.md](../README.md).

```bash
docker compose up -d --build
curl -s http://localhost:8001/
docker compose exec node-a wget -qO- http://node-b:8000/
docker compose stop node-b
docker compose down -v
```
