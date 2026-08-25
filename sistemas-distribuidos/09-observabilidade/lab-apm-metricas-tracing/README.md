# Lab B — APM (métricas + tracing + logs)

Gateway **:8110** · Grafana **:3110** · Prometheus **:9091** · Tempo **:3200** · Loki **:3102**

~4–6 GB RAM · `down -v` no lab A antes.

**Núcleo**

```bash
./scripts/up.sh
./scripts/enviar.sh
./scripts/provar-delay.sh 2000
./scripts/provar-erro.sh
```

**Aprofundamento**

```bash
./scripts/quiz-cardinalidade.sh
./scripts/quiz-sampling.sh 1000 1
./scripts/provar-sampling-otel.sh 0.2 40
./scripts/provar-retry.sh
```

Tutorial: [../tutorial-apm-metricas-tracing.md](../tutorial-apm-metricas-tracing.md)
