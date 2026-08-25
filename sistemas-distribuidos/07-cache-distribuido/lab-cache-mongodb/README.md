# Lab — Cache avisos (MongoDB + Redis, 2 APIs)

**Módulo:** [07 — Cache distribuído](../README.md)  
**Tutorial:** [tutorial-cache-mongodb.md](../tutorial-cache-mongodb.md)

| Serviço | Host |
|---------|------|
| API 1 | `http://127.0.0.1:8095` |
| API 2 | `http://127.0.0.1:8096` |
| Mongo | `27122` |
| Redis | `6382` |

```bash
./scripts/up.sh
./scripts/comparar-local-vs-redis.sh   # Exp. 1 — rode a partir desta pasta
./scripts/benchmark.sh 15
```

Scripts: `comparar-local-vs-redis.sh` · `benchmark.sh` · `provar-stale-ttl.sh` · `publicar.sh` · `set-backend.sh` · `flush.sh`