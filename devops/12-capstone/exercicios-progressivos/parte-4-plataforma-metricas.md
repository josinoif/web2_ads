# Marco 4 — Plataforma interna e métricas

**Tag alvo:** `v0.4.0-platform-ready`.
**Tempo sugerido:** ~1-2 semanas.
**Fase correspondente:** [Fase 4](../bloco-4/04-fase-plataforma.md) + [armadilhas](../bloco-4/04-armadilhas-e-dicas.md).

---

## Objetivo

Fechar o sistema como **produto**: catálogo vivo, golden path reprodutível, métricas DORA/NPS reais, roadmap pós-capstone. Sem este marco, o sistema "existe e opera", mas não é **plataforma**.

---

## Entregáveis

### Plataforma
- [ ] Software Catalog publicado (Backstage OU variante leve com MkDocs + YAMLs + script).
- [ ] Catálogo com ≥ 6 entidades: Component (API), Component (worker), Resource (DB), Resource (Queue), Resource (Cache), System, Domain, Group.
- [ ] Ownership, tags, lifecycle, tier coerentes.
- [ ] TechDocs navegável.
- [ ] Golden path template em `platform/templates/`.
- [ ] Golden path **usado**: gerar um segundo serviço do repositório (ex.: `worker-notificacao-sms`) via template.

### Métricas
- [ ] `docs/dora-report.md` com classificação calculada a partir dos dados reais do capstone.
- [ ] NPS interno simulado (n ≥ 3) em `docs/survey-capstone.md`.
- [ ] Plano de ação baseado no survey em `docs/platform-roadmap.md`.

### Documentação
- [ ] ≥ 1 ADR revisado/supersedes no histórico (prova de amadurecimento).
- [ ] Roadmap pós-capstone em `docs/roadmap-pos.md` com top 3 priorizado.

### Evidências
- [ ] Retrospectiva em `docs/retro/marco4.md`.
- [ ] `CHANGELOG.md` com `v0.4.0`.
- [ ] Tag `v0.4.0-platform-ready`.

---

## Demonstração esperada

Em ≤ 4 min você mostra:

1. Abrir Backstage/catálogo → achar CivicaBR → ver owner, APIs, deps.
2. Usar golden path para criar novo componente **ao vivo** (ou rodar `cookiecutter`).
3. Ver o componente recém-criado no catálogo após sync.
4. Abrir `dora-report.md` — explicar classificação atual.

---

## Critérios de avaliação deste marco

| Item | Peso local |
|------|------------|
| Catálogo populado com ownership/tiers | 20% |
| Golden path executável + serviço gerado | 25% |
| DORA com dados reais + leitura crítica | 20% |
| NPS coletado + plano de ação | 15% |
| Roadmap pós-capstone priorizado | 10% |
| ADR evoluída (supersedes) | 5% |
| Retrospectiva | 5% |

---

## Armadilhas comuns

- Catálogo com 1 componente apenas.
- Golden path que não gera nada executável.
- DORA inventado (banca pergunta a fonte; se é planilha imaginária, reprova).
- NPS colhido só do próprio aluno (n=1).
- Roadmap genérico ("melhorar monitoramento") sem prioridade ou métrica.

---

## Antes de fechar o marco

1. Um amigo/colega que nunca viu o projeto consegue navegar pelo catálogo e entender o sistema em 5 min? Peça para testar.
2. Rode o golden path do zero em 10 min — **cronometre**. Se ultrapassou, investigue: o template tem fricção.
3. Abra o roadmap — consegue defender por que **esses 3** e não outros? Se resposta "é o que me ocorreu", revise.

Se tudo bate, o Marco 4 está pronto — só falta a banca.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marco 3 — Sistema observável e resiliente](parte-3-operacao-resiliencia.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Marco 5 — Defesa com incidente ao vivo](parte-5-banca-final.md) |

<!-- nav:end -->
