# Lab mínimo — ambiente de experimentação

Três nós HTTP idênticos + Redis. Detalhes e roteiro: [../README.md](../README.md).

```text
docker compose up -d --build
curl.exe -s http://localhost:8001/
docker compose exec -T node-a wget -qO- http://node-b:8000/
docker compose stop node-b
docker compose down -v
```

No Linux/macOS: `curl -s` em vez de `curl.exe -s`. Detalhes: [../README.md](../README.md) · [linux-e-windows](../../ferramentas/linux-e-windows.md).
