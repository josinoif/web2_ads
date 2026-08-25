# Lab D — Notificação: fila única vs filas por canal

**Módulo:** [11 — System Design](../README.md) · **Tutorial:** [tutorial-notificacao-canais.md](../tutorial-notificacao-canais.md)

**Pergunta:** e-mail lento segura o push?

> Aproximação didática: Redis lista + delay no worker de e-mail. **Não** é SMTP/FCM real.

| Modo | Porta | O que sobe |
|------|-------|------------|
| Fila única | `8170` | 1 publisher + 1 worker (`EMAIL_DELAY=2s`) |
| Filas por canal | `8171` | publisher + workers push/email/sms |
| Redis | `6395` | DB 0 = unico; DB 1 = canais |

```bash
./scripts/up.sh
./scripts/enviar.sh canais
./scripts/provar-isolamento.sh
```

`docker compose down -v` ao terminar. Ver [troubleshooting](../troubleshooting.md).
