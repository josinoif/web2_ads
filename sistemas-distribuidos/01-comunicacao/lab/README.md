# Lab — Correção de provas (fila)

Tutorial: [../tutorial-correcao-prova.md](../tutorial-correcao-prova.md)

```bash
docker compose up -d --build
curl -s http://localhost:8080/health
./scripts/enviar-lote.sh 10
docker compose down -v
```
