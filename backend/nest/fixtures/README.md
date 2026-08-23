# Fixtures de lab

| Arquivo | Uso |
|---------|-----|
| `caneca.jpg` | Upload P (cap. 9) — JPEG mínimo 1×1 |

No curl (a partir de `loja-api/` ou copie o arquivo):

```bash
curl ... -F "file=@../fixtures/caneca.jpg"
# ou, se copiou para loja-api/fixtures/:
# curl ... -F "file=@./fixtures/caneca.jpg"
```
