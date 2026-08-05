# Fase 3 — Armadilhas, dicas e orientações de banca

> Complemento à [Fase 3 — Operação e resiliência](./03-fase-operacao.md).

---

## 1. O que a banca testa aqui

1. *"Eu acabei de matar 2 Pods. Em qual dashboard você me mostra o impacto?"* — Nome do painel + quanto tempo até normalizar.
2. *"Mostre como um log se conecta a um trace."* — Você precisa ter `trace_id` em logs e saber **buscar** em Loki + abrir em Tempo.
3. *"Qual é o seu error budget este mês?"* — Você precisa ter número vivo.
4. *"Um cidadão pede eliminação dos dados (LGPD). Como você atende?"* — Você precisa ter **processo**, não intenção.
5. *"Eu desligo o cluster agora. Em quanto tempo você restaura e com qual perda?"* — RTO/RPO medidos, não inventados.

---

## 2. Sinais de observability real (vs teatro)

| Teatro | Real |
|--------|------|
| "Prometheus instalado" | Métricas específicas da aplicação, instrumentadas |
| "Dashboards existem" | Você os usa para tomar decisões semanais |
| "Temos SLOs" | Você sabe de cor quanto budget falta |
| "Alertas configurados" | Alertas **disparam** quando você força falha |
| "Traces ligados" | Um request específico rastreado do Ingress ao DB |

Se sua observability é teatro, a banca descobre na segunda pergunta.

---

## 3. Dicas operacionais

### 3.1 Teste seus alertas

Crie um **alerta de teste** propositalmente quebrado a cada trimestre; mede tempo entre quebra real e detecção humana. É a única forma de saber se o toque chega.

### 3.2 Error budget como moeda

Quando defender trade-offs, use *"restam 12 min de budget neste mês; vou gastar 5 em um canary experimental"*. Essa linguagem mostra maturidade.

### 3.3 Runbook como código

- Adicione link `runbook_url` em **toda alert rule**.
- Runbook idealmente em `docs/runbooks/` no mesmo repo — versionado com código.
- Teste runbook antes do incidente real — "game day" é o laboratório.

### 3.4 Threat model "vivo"

O threat model nunca está "pronto". Toda feature nova = 30 min de revisão STRIDE incluída na definição de ready. Mostre na banca uma **evolução** do threat model (com commits).

### 3.5 LGPD pragmático

Foco 80/20 para o capstone:

1. **Inventário** com categorias e retenção.
2. **Consentimento explícito** registrado no BD.
3. **Endpoint** `/v1/dpo/request` aceita pedido (ack) — processamento manual aceitável.
4. **Anonimização** implementada (função que substitui nome por `CIDADAO-<hash>`).
5. **Logs** sem PII (hash de e-mail; nunca CPF em plaintext).

---

## 4. Perguntas que a banca faz

### 4.1 Observability

- *"Por que histograma e não gauge para latência?"* → percentis exigem buckets; p95 não sai de gauge.
- *"Cardinalidade alta em que métrica?"* → você deve saber (ex.: `path` com ID de usuário — proibido). Use `tenant_id` agregado, não IDs individuais.
- *"Retenção de métricas/logs/traces?"* → métricas 30d; logs bronze 7d / gold 30d; traces 7d com sampling.

### 4.2 Security

- *"Por que keyless Cosign e não chave longa?"* → keyless delega ao OIDC (GitHub) → sem segredo para vazar; rotação automática.
- *"Kyverno audit vs enforce?"* → audit em rollout; enforce quando policy amadurece. Política crítica nasce enforce.
- *"Quais CVEs seriam aceitáveis?"* → CRITICAL com exceção documentada (VEX); HIGH com plano de correção em 7d; MEDIUM tolerado.

### 4.3 SRE

- *"Diferença entre MTTR e MTTM?"* → MTTR (resolve = estado OK); MTTM (mitigate = sintoma cessa). Um site pode estar mitigado e ainda em investigação.
- *"Como decide entre rollback e fix-forward?"* → regra explícita no EBP: Sev-1 = rollback sempre; Sev-2 = rollback se possível em 15 min, senão forward; Sev-3 = forward.
- *"RPO 15 min significa?"* → em desastre, perdemos no máximo os últimos 15 min de dados. Exige WAL streaming/replica síncrona.

---

## 5. Fórmulas úteis

### 5.1 Budget em minutos/mês

```
30d * 24h * 60min = 43 200 min
Budget para 99.9%: 43 200 * 0.001 = 43.2 min
Budget para 99.95%: 21.6 min
Budget para 99.99%: 4.32 min
```

### 5.2 Burn rate alerta fast/slow

```
Fast burn:  1h window, threshold 14.4x budget  (~1% budget em 1h)
Slow burn:  6h window, threshold 6x           (~10% budget em 6h)
Ambos disparam juntos = sinal genuino
```

### 5.3 Cardinalidade alvo

- < 100 séries por métrica se label inclui `tenant_id` (até ~100 tenants).
- < 1000 séries total por aplicação.
- Monitor: `prometheus_tsdb_symbol_table_size_bytes`.

---

## 6. Erros que reprovam

- Logs com PII em texto claro (e-mail, CPF).
- `Secret` como `ConfigMap`.
- Dashboard com "TODO" como título de painel.
- Alerta sem runbook associado.
- Postmortem com o nome de um "culpado" como causa raiz.
- Backup sem teste de restore.
- `kubectl edit` usado em prod sem GitOps.

---

## 7. Ferramentas úteis

- **`k9s`** para navegar cluster rápido.
- **`stern`** para tail de logs multi-pod.
- **`kubectl-neat`** / **`kubectl-tree`** para ver recursos de verdade.
- **`OpenCost`** se quiser mostrar FinOps.
- **`Falco`** para runtime detection (bônus).
- **`Polaris`** / **`kubescape`** para scoring de segurança K8s.
- **Chaos Mesh dashboard** para experimentos e Game Day.

---

## 8. Sinais de que você está pronto para a Fase 4

- Você consegue contar um *incidente de 10 min* coerente de memória (como aconteceu, como detectou, como mitigou).
- Sobrevive a `kubectl delete pod -l app=api --all` sem perder disponibilidade mensurável.
- Sabe quantos minutos de budget restam este mês.
- Pode dar 30 min para o professor "brincar" com seu ambiente sem entrar em pânico.

Se tudo acima bate, `git tag v0.3.0-operable` e siga para a Fase 4.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 3 — Operação e resiliência](03-fase-operacao.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Fase 4 — Plataforma interna, métricas e apresentação final](../bloco-4/04-fase-plataforma.md) |

<!-- nav:end -->
