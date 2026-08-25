# Glossário — Cache distribuído

**Módulo:** [07 — Cache distribuído](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **Cache** | Cópia rápida de um dado/resposta para evitar ir sempre à fonte. |
| **Fonte da verdade (SoT)** | Store autoritativo (Postgres/Mongo nos labs); o cache **não** substitui. |
| **Cache local** | Memória do processo (dict); não compartilhado entre réplicas de API. |
| **Cache distribuído / compartilhado** | Serviço externo (Redis) acessível por várias APIs. |
| **Cache-aside** | App consulta o cache; no miss, lê a fonte e preenche o cache. |
| **Write-through** | Escrita atualiza fonte e cache juntos (conceito). |
| **Write-behind** | Escrita no cache primeiro; propaga à fonte depois (conceito). |
| **Hit** | Chave encontrada no cache — não consultou a fonte. |
| **Miss** | Chave ausente/expirada — precisa ir à fonte. |
| **fonte_dados** | SoT do valor (postgres/mongodb) — independente de hit/miss. |
| **servido_de** | De onde **esta** resposta saiu (`redis` / `local` / store). |
| **servido_por** | Qual réplica de API atendeu (lab Mongo: `api1` / `api2`). |
| **Hit rate** | Proporção de hits sobre (hits + misses). |
| **Stale** | Valor no cache **desatualizado** em relação à fonte. |
| **TTL** | Tempo de vida da chave; após expirar, próximo acesso é miss. |
| **Invalidação** | Remover (ou marcar inválida) a chave após escrita — tipicamente `DEL`. |
| **Invalidate-on-write** | Política: toda escrita bem-sucedida apaga a chave relacionada. |
| **Read-your-writes** | Quem escreveu vê o valor novo nas leituras seguintes (invalidate ajuda). |
| **Stampede / thundering herd** | Muitos misses simultâneos na mesma chave saturam a fonte. |
| **TTL jitter** | Variação aleatória no TTL para dessincronizar expires. |
| **Single-flight** | Só um miss busca na fonte; demais esperam o preenchimento. |
| **Hot key** | Chave muito acessada — ponto de contenção no cache e no miss. |
| **CDN** | Cache na borda de rede (estáticos/páginas); fora do foco deste lab. |

Ver também: [glossário CAP](../03-consistencia-cap/glossario.md) (eventual, strong, CP/AP).
