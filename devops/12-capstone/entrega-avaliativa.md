# Entrega avaliativa — Módulo 12 (Capstone)

**Peso:** equivale a ≥ 30% da nota final do curso (ajuste conforme plano pedagógico).
**Formato:** repositório Git (monorepo ou multi-repo orquestrado), ambiente local reproduzível, defesa ao vivo em banca.
**Prazo sugerido:** 10-12 semanas.

---

## O que é avaliado

Três pilares, com pesos:

| Pilar | Peso | O que mede |
|-------|------|------------|
| **Execução técnica** | 55 | Qualidade objetiva do sistema: CI/CD, containers, IaC, K8s, obs, segurança, SRE, plataforma |
| **Decisão e documentação** | 25 | ADRs, RFCs, README, runbooks, postmortem |
| **Defesa ao vivo** | 20 | Conduzir incidente simulado, responder perguntas com profundidade |

---

## Rubrica detalhada (100 pts)

### 1. Execução técnica (55 pts)

#### 1.1 CI/CD (10 pts)

- Pipeline roda em < 15 min para PRs típicas (2).
- Lint, teste, coverage ≥ 70%, SAST, SCA, secrets scan (3).
- Build reprodutível + SBOM + Cosign (2).
- Deploy automático para staging; manual gate para prod (2).
- Estratégia de release documentada (blue-green ou canary) (1).

#### 1.2 Containers e K8s (10 pts)

- Imagens distroless/Chainguard, nonroot, sem CVE Critical em main (3).
- Deployment/Service/Ingress/HPA/PDB/NetworkPolicy presentes (3).
- Probes e recursos (requests/limits) configurados (2).
- RBAC mínimo, ServiceAccount dedicado (2).

#### 1.3 IaC (7 pts)

- Tudo versionado; ambientes dev/staging/prod separados (3).
- Remote state (ou alternativa documentada) (1).
- Policy-as-code no CI (Checkov, Kyverno) (3).

#### 1.4 Observability (10 pts)

- Métricas, logs estruturados, traces — todos instrumentados (4).
- SLIs/SLOs declarados e publicados (2).
- ≥ 3 dashboards com golden signals e saúde geral (2).
- ≥ 3 alertas SLO-based roteados (2).

#### 1.5 Segurança (8 pts)

- Threat model STRIDE documentado (2).
- Admission control (Kyverno) ativo com ≥ 2 políticas (2).
- Image signing + SBOM verificável (2).
- Análise LGPD com mapeamento e controles (2).

#### 1.6 SRE (10 pts)

- Error Budget Policy com ações (2).
- ≥ 1 experimento de chaos com hipótese/steady state/resultado (2).
- Backup Velero agendado + teste de restore documentado (2).
- DR playbook com RPO/RTO medidos (2).
- ≥ 3 runbooks; política de on-call declarada (2).

---

### 2. Decisão e documentação (25 pts)

#### 2.1 ADRs (8 pts)

- ≥ 8 ADRs, cobrindo decisões significativas (4).
- Formato consistente (contexto, decisão, consequências, alternativas) (2).
- Pelo menos 1 ADR refatorado/atualizado ao longo do projeto (2).

#### 2.2 RFCs (4 pts)

- ≥ 2 RFCs antes de mudanças grandes (2).
- Inclui alternativas consideradas e rejeitadas (2).

#### 2.3 README e navegação (6 pts)

- README raiz explica produto, arquitetura, como rodar, onde ir (3).
- Diagrama Mermaid da arquitetura (1).
- Links vivos para docs/runbooks/dashboards (2).

#### 2.4 Runbooks (4 pts)

- ≥ 3 runbooks operacionais (2).
- Formato padronizado; testados (2).

#### 2.5 Postmortem (3 pts)

- Template blameless (1).
- ≥ 1 postmortem real/simulado, com timeline, contributing factors e ações (2).

---

### 3. Defesa ao vivo (20 pts)

#### 3.1 Pitch arquitetural (5 pts)

- Apresentação ≤ 8 min cobrindo problema, solução, trade-offs (3).
- Materiais claros (slides ou dashboard live) (2).

#### 3.2 Incidente simulado (10 pts)

Banca injeta 1 falha do cardápio:
- Pod killado;
- NetworkChaos entre API e DB;
- Registry indisponível;
- Registro LGPD solicitado (request de direito do titular);
- CVE crítica descoberta;
- Vazamento simulado de token.

Avaliação:
- Detecta via observability em ≤ 5 min (3).
- Abre incidente seguindo ICS (IC, Ops, Comms) — pode ser papéis simulados (2).
- Mitiga usando runbook existente (3).
- Comunica adequadamente (status, stakeholders fictícios) (2).

#### 3.3 Perguntas da banca (5 pts)

- Aluno explica 3 ADRs escolhidos pelo avaliador (2).
- Aponta limitações reconhecidas do sistema (1).
- Aponta próximos 2 passos priorizados e por quê (2).

---

## Bônus (até +10 pts)

- **Frontend funcional** com UX mínimo polido (+2).
- **Multi-tenant efetivo** (isolamento de dados por prefeitura) (+2).
- **DPIA** (Data Protection Impact Assessment) LGPD no nível de requisito (+1).
- **Cost dashboard** (FinOps mínimo) (+1).
- **Plugin Backstage K8s** funcional (+1).
- **Score.dev** usado como workload spec (+1).
- **Game Day público** (convidar colega como co-responder) registrado (+2).

---

## Critérios de reprovação automática

- Segredos versionados em texto claro.
- Imagem com CVE Critical conhecido em deploy de prod (sem exceção documentada).
- Ausência de qualquer teste automatizado.
- CI verde vazio (teste trivial apenas "asserta True").
- Ausência total de observability.
- README não explica como rodar.

---

## Formato de entrega

1. **Link do repositório** (GitHub preferível; se privado, adicionar avaliador).
2. **README raiz** com:
   - Pitch em 3 parágrafos.
   - Diagrama de arquitetura.
   - Pré-requisitos.
   - `make up` em ≤ 10 min.
   - Links para docs/runbooks/dashboards/ADRs.
3. **Vídeo pitch** (opcional, ≤ 5 min) — útil para banca assíncrona.
4. **Defesa presencial** (ou síncrona remota):
   - Pitch.
   - Incidente simulado.
   - Q&A.

---

## Checklist final antes de defender

### Infra
- [ ] `make up` sobe tudo em ≤ 10 min.
- [ ] Logs, métricas, traces **são coletados** (não apenas configurados).
- [ ] `make test` roda e está verde.
- [ ] Nenhum segredo está em texto claro no repositório.

### Observabilidade em uso
- [ ] Dashboards abrem com dados reais do ambiente local.
- [ ] Pelo menos um alerta dispara quando você força uma falha.

### Documentação
- [ ] README raiz explica em < 3 min o que o sistema faz.
- [ ] ADR/0001 a 0008+ existem e são coerentes entre si.
- [ ] ≥ 3 runbooks testáveis.
- [ ] Postmortem de ao menos 1 incidente (pode ser simulado) está escrito.

### Ensaios
- [ ] Você já "matou um Pod" e viu o sistema reagir.
- [ ] Você já restaurou um backup Velero em namespace alternativo.
- [ ] Você já rollbou um deploy em staging.
- [ ] Você já desativou uma feature flag e viu comportamento mudar.
- [ ] Você ensaiou 2× a apresentação em voz alta.

### Defesa
- [ ] Tem slides OU um roteiro claro do que mostrar no ambiente.
- [ ] Sabe os 3 ADRs que **você** considera mais importantes.
- [ ] Sabe o que faria diferente se recomeçasse.
- [ ] Sabe os 2 próximos passos de maior impacto.

Se os itens acima estão marcados, **você está pronto**. Se não estão, o módulo não terminou — respire fundo, e volte ao checklist.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marco 5 — Defesa com incidente ao vivo](exercicios-progressivos/parte-5-banca-final.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](README.md) | **Próximo →**<br>[Referências — Módulo 12 (Capstone)](referencias.md) |

<!-- nav:end -->
