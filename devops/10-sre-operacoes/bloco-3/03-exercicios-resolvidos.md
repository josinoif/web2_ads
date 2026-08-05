# Bloco 3 — Exercícios resolvidos

> Leia [03-disaster-recovery.md](./03-disaster-recovery.md) antes.

---

## Exercício 1 — Definir RPO/RTO

**Enunciado.** Para 3 sistemas da PagoraPay, proponha RPO e RTO com justificativa baseada em impacto regulatório/negócio/experiência:

- (a) `pix-core` (envio de PIX)
- (b) `relatorios-bi` (dashboards internos para decisores)
- (c) `logs-auditoria` (LGPD, BCB)

**Respostas.**

| Sistema | RPO | RTO | Justificativa |
|---------|-----|-----|---------------|
| (a) pix-core | **0 min** (nenhuma perda) | **15 min** | Operação crítica; BACEN exige; cliente perde dinheiro em cada minuto. Exige replicação síncrona + standby quente. |
| (b) relatorios-bi | **24 h** | **4 h** | Não afeta cliente; decisores podem usar dados do dia anterior. Backup diário via Velero. |
| (c) logs-auditoria | **0 min** | **1 h** | Requisito regulatório explícito. Perda é **violação** (não-compliance). Escrever com WORM/immutable; replicação contínua para storage externo. RTO pode ser mais folgado (ninguém consulta em tempo real), mas perda é inaceitável. |

Nota: RPO=0 com RTO curto de `pix-core` implica **Warm Standby** (replica síncrona + failover automático). Isso custa caro — e é razoável porque o custo do **não**-ter é maior.

---

## Exercício 2 — Escolher padrão de DR

**Enunciado.** Recomende (Backup/Pilot/Warm/Active) para cada caso:

1. Blog corporativo estático, tráfego 1 k visitas/dia.
2. E-commerce brasileiro médio, 50 k pedidos/dia, caiu por 4h custa ~R$ 200k.
3. Trading system de alta frequência, cada 100 ms de indisponibilidade custa milhões.
4. Sistema de RH interno, 500 funcionários, usa uma vez por mês.

**Respostas.**

1. **Backup & Restore**. É estático; a pior perda é algumas horas. Cloudflare/S3 + dump no Git resolve.
2. **Warm Standby**. 4h custa R$ 200k; Warm custa mensalmente ~R$ 15-40k; o investimento se paga em 1-2 incidentes. Pilot Light também seria opção se RTO aceitável for ~1h.
3. **Multi-Site Active/Active**. Qualquer coisa menos do que "zero interrupção" custa caro demais. Arquitetura específica: hedge funds/exchanges.
4. **Backup & Restore**. Usado raramente; RTO de horas é aceitável; custo de standby não se justifica.

Conclusão: **DR é proporcional ao valor** da disponibilidade. Não há "DR certo" universal.

---

## Exercício 3 — Velero backup + restore

**Enunciado.** Execute (ou simule): criar namespace `pagora`, deployar um app (`nginx`), criar um backup com Velero, **deletar** o namespace, e restaurar. Reporte o RTO observado.

**Passos:**

```bash
kubectl create ns pagora
kubectl -n pagora create deployment hello --image=nginx:1.27-alpine
kubectl -n pagora create configmap config-demo --from-literal=env=prod

# Backup
velero backup create pagora-demo --include-namespaces pagora --wait
velero backup describe pagora-demo --details

# Simular desastre
kubectl delete ns pagora

# Marcar T0
T0=$(date +%s)

# Restore
velero restore create --from-backup pagora-demo --wait

# Validar
kubectl -n pagora get deploy,cm
kubectl -n pagora rollout status deploy/hello

# T1
T1=$(date +%s)
echo "RTO observado: $((T1 - T0)) segundos"
```

**Reporte (exemplo):**

- RTO observado: ~35 segundos (restore incluiu namespace, deployment, configmap).
- Observação crítica: **dados em PVC** só voltariam se `--default-volumes-to-fs-backup` estava ativo **no momento do backup**. Sem isso, o restore traz manifests mas volumes vazios → aplicação sobe mas dados foram.

---

## Exercício 4 — Validar com `dr_simulator.py`

**Enunciado.** Crie um `cenarios.yaml` com 2 cenários próprios (p.ex. "region down" e "db corruption") e execute `dr_simulator.py` com alvos RPO=5 RTO=30. Interprete.

**Exemplo `cenarios.yaml`:**

```yaml
cenarios:
  - nome: "db-corruption-DROP"
    rpo_fonte_min: 1        # WAL archiving a cada minuto
    etapas:
      - { nome: "detectar via alert", minutos: 2 }
      - { nome: "diagnostico + decisao", minutos: 8 }
      - { nome: "restore PITR (DB 50GB)", minutos: 22 }
      - { nome: "validar checksums", minutos: 5 }

  - nome: "region-down"
    rpo_fonte_min: 5
    etapas:
      - { nome: "detectar", minutos: 5 }
      - { nome: "decidir failover", minutos: 10 }
      - { nome: "ativar warm standby", minutos: 15 }
      - { nome: "DNS failover (TTL 300)", minutos: 6 }
      - { nome: "aquecer cache", minutos: 10 }
```

**Saída:**

```
Cenario: db-corruption-DROP
etapa                     minutos
detectar via alert        2
diagnostico + decisao     8
restore PITR (DB 50GB)    22
validar checksums         5
TOTAL RTO                 37

RPO esperado: 1min (alvo 5) -> OK
RTO esperado: 37min (alvo 30) -> EXCEDE (+7min)

Cenario: region-down
etapa                     minutos
detectar                  5
decidir failover          10
ativar warm standby       15
DNS failover (TTL 300)    6
aquecer cache             10
TOTAL RTO                 46

RPO esperado: 5min (alvo 5) -> OK
RTO esperado: 46min (alvo 30) -> EXCEDE (+16min)
```

**Interpretação:**

- Ambos excedem RTO. Ações:
  - **db-corruption**: o gargalo é `restore PITR (22min)`. Opções — aumentar CPU da instância de restore; ter PITR replica pronta (pilot light para o DB); aceitar RTO 40min e ajustar alvo (honestidade > aspiração).
  - **region-down**: reduzir TTL de DNS para 60s, manter warm standby já rodando (Active-Passive permanente), corta ~10 min. Alvo passa a ser viável.

**Lição**: SLO/RTO aspiracional sem cobertura financeira é ficção. `dr_simulator.py` expõe a fantasia.

---

## Exercício 5 — Runbook mínimo

**Enunciado.** Escreva um runbook de 1 página para o cenário "`pix-core` não sobe após restore Velero". Siga a estrutura do bloco.

**Resposta.**

```markdown
# Runbook: pix-core nao sobe apos restore Velero

## Pre-condicoes
- Restore Velero concluido (`velero restore describe` = Completed).
- kubectl apontando para o cluster de destino.

## Passo 1 - Ver status
    kubectl -n pagora get pods -l app=pix-core

Esperado: 3 pods Ready.
Se CrashLoopBackOff -> Passo 2. Se ImagePullBackOff -> Passo 4.

## Passo 2 - Ver logs
    kubectl -n pagora logs -l app=pix-core --tail=50

Procurar:
- "connection refused postgres"   -> Passo 3
- "migration schema mismatch"     -> Passo 5

## Passo 3 - Conectividade DB
    kubectl -n pagora run -it --rm psql-debug --image=postgres:15 -- \
        psql "postgresql://app@ledger-db.pagora.svc:5432/app" -c "select 1;"

Se falhar:
- Verificar Service: `kubectl -n pagora get svc ledger-db`
- Verificar NetworkPolicy (Modulo 9 `default-deny` pode bloquear)
- Reaplicar NP: `kubectl apply -k infra/k8s/network-policies/`

## Passo 4 - Imagem
    kubectl -n pagora describe pod -l app=pix-core | grep -A3 Events

Se "no such image" em registry -> registry pode estar offline; usar espelho:
    kubectl -n pagora set image deploy/pix-core pix-core=mirror.pagora/pix-core:v1.4.2

## Passo 5 - Migrations
    kubectl -n pagora run migrate --rm -it --image=ledger:v1.4.2 -- \
        python -m alembic upgrade head

## Criterio de sucesso
    curl -f https://pagora.example/pix/healthz
    # "status": "ok"

## Plano B
Se nenhum passo resolver em 20 min, escalar para IC on-call.

## Ultima execucao
2026-04-01 16:30 - sucesso; problema estava em NetworkPolicy default-deny ainda nao reaplicada.
```

---

## Exercício 6 — Armadilhas comuns

**Enunciado.** Para cada afirmação, aponte a falha e sugira correção:

1. *"Fazemos backup toda noite, temos 5 backups guardados."*
2. *"Nosso RTO é 15 minutos."* (nunca testaram)
3. *"Velero também está no cluster prod; se ele cair, restore rápido."*
4. *"Para DR, usamos a mesma região cloud em outra zona."*

**Respostas.**

1. **Sem restore testado = backup não é backup.** Correção: rodar **restore mensal** em cluster/namespace isolado, validar healthcheck, checksum de tabelas.
2. **RTO sem medição é palpite.** Correção: fazer DR Game Day, medir RTO observado, reportar **ambos** (alvo e medido) no dashboard.
3. **DR depende da própria coisa que está caindo.** Velero e seu storage (MinIO/S3) precisam estar fora ou replicados. Correção: bucket Velero em provider/região **diferente**; cluster de restore **separado**.
4. **Zona ≠ Região.** Zonas compartilham destino em falhas regionais (rede, energia). DR sério requer **região diferente**, idealmente país diferente para alguns cenários regulatórios. Correção: planejar multi-region — custo maior, mas compatível com o risco real.

---

## Autoavaliação

- [ ] Diferencio BC, DR, RPO e RTO.
- [ ] Proponho RPO/RTO com justificativa de custo.
- [ ] Escolho padrão (Backup/Pilot/Warm/Active) adequado.
- [ ] Opero Velero com backup agendado e restore.
- [ ] Complemento Velero com estratégia de DB (PITR, WAL).
- [ ] Valido cenários com `dr_simulator.py`.
- [ ] Escrevo runbooks com critério de sucesso e plano B.
- [ ] Reconheço armadilhas ("backup não testado", "DR no mesmo cluster").

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 3 — Disaster Recovery: a capacidade que você só descobre se tem ao usar](03-disaster-recovery.md) | **↑ Índice**<br>[Módulo 10 — SRE e operações](../README.md) | **Próximo →**<br>[Bloco 4 — Gestão de Incidentes em Escala: papéis, comunicação e aprendizado](../bloco-4/04-incidentes-escala.md) |

<!-- nav:end -->
