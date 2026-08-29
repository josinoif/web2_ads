# Mini-lab — Kafka: pedido pago

Tutorial (leia **por que Kafka / o que quebra sem Kafka** antes do Compose): [tutorial.md](tutorial.md)

**Linux e Windows:** os mesmos comandos. Terminal **nesta pasta**. `-T` no `exec` evita erro de TTY no Windows. Guia geral dos outros labs: [linux-e-windows.md](../../../ferramentas/linux-e-windows.md).

## Subir e testar

```text
docker compose up -d --build
docker compose exec -T api python lab.py health
```

- Checkout: `http://localhost:8084`
- **Kafka UI:** [http://localhost:8085](http://localhost:8085) (sem senha)

```text
docker compose down -v
```

---

## Referência rápida

| Peça | Porta |
|------|--------|
| Checkout (API) | `8084` |
| Kafka UI | `8085` |

```text
docker compose exec -T api python lab.py ajuda
docker compose exec -T api python lab.py cadeia ana
docker compose stop nota
docker compose exec -T api python lab.py cadeia bruno
docker compose start nota

docker compose exec -T api python lab.py pagar clara
docker compose exec -T api python lab.py rastreio
docker compose exec -T api python lab.py lote 6
docker compose exec -T api python lab.py replay 8
```

Evidências: [tutorial.md §4](tutorial.md#evidencias).

### O que olhar no código

| Arquivo | O que ensina |
|---------|----------------|
| [`api/app.py`](api/app.py) | `executar_cadeia` (dor) vs `publicar` (fato) |
| [`consumidor/consumidor.py`](consumidor/consumidor.py) | HTTP da cadeia + consumer group |
| [`comum/rastro.py`](comum/rastro.py) | o tópico não é o GET de “já baixei estoque” |
