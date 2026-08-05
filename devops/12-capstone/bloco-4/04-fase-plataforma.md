# Fase 4 — Plataforma interna, métricas e apresentação final

> **Propósito.** Fechar o ciclo: o sistema existe, roda, se defende — agora ele é **produto**. Você publica catálogo, golden path, mede DORA, ensaia a defesa e prepara o incidente ao vivo da banca.

**Duração sugerida:** 10-15h em ~1-2 semanas, mais tempo dedicado a ensaio.

---

## 4.1 Objetivos da fase

- **Software Catalog** publicado (Backstage ou variante leve) com CivicaBR e dependências.
- **Golden path mínimo**: template que gera um serviço filho (ex.: "worker de notificação SMS") com CI/obs/sec/K8s — evidência de que a plataforma é **produto**.
- **DORA medido** com dados reais do capstone (mesmo que curto).
- **NPS simulado** (pode ser a autoavaliação ou com 2-3 colegas) e plano de ação.
- **Incident script** preparado para banca (scenarios que você domina).
- **Pitch final** em 5-8 min.
- **Postmortem** blameless de ao menos 1 incidente real ou simulado.
- **Roadmap pós-capstone**: os próximos 3 passos claros.

Produto da fase: o **portfólio de defesa**.

---

## 4.2 Por que plataforma mesmo em projeto solo

Você é, ao mesmo tempo, **produtor** e **consumidor** da plataforma. Dividir mentalmente os dois papéis:

- **Como squad de produto**: o que eu preciso para adicionar um novo serviço rapidamente?
- **Como platform team**: o que eu ofereço e como versiono?

Esse exercício prova compreensão do Módulo 11 e protege você de resolver tudo com hacks ad-hoc.

---

## 4.3 Software Catalog — versão leve aceita

Você pode adotar:

### 4.3.1 Backstage completo

Como no Módulo 11: `npx @backstage/create-app` + carregar `catalog-info.yaml` da sua API e worker, com TechDocs ativo.

### 4.3.2 Alternativa mínima

Se tempo é restrito, aceita-se:

- Repositório `platform/` com arquivos `catalog/*.yaml` no mesmo formato de Backstage.
- Um script Python (`platform/catalog_render.py`) que lê e gera um HTML estático navegável.
- TechDocs substituído por MkDocs material publicado como GitHub Pages.

Qualquer forma precisa ter:

- Component (API), Component (worker), Resources (DB, Redis, Queue), System (civicabr), Domain (civico), Group (platform-solo), Group (produto-solo).
- **Ownership** declarada (mesmo que seja o mesmo autor).
- **Relations** (dependsOn, providesApi).
- **TechDocs** (README + arquitetura + runbooks renderizados).

---

## 4.4 Golden path mínimo

Template que gera um novo serviço completo. Mesmo simples, prova que a plataforma é **reprodutível**.

### 4.4.1 Template (Backstage Scaffolder ou Cookiecutter)

Conteúdo mínimo:

```
platform/templates/worker-python/
├── template.yaml     (se Backstage) OU cookiecutter.json
└── skeleton/
    ├── catalog-info.yaml
    ├── pyproject.toml
    ├── src/app/worker.py
    ├── tests/test_worker.py
    ├── Dockerfile
    ├── .github/workflows/ci.yml
    └── k8s/deployment.yaml
```

Campos do template: `name`, `owner`, `queue_name`, `tier`.

### 4.4.2 Execução

Executar o template para gerar um segundo serviço real do capstone (ex.: `worker-notificacao-sms`) — mesmo que não tenha lógica de negócio completa. O fato de **gerar e deploy-ar** é o que comprova o valor.

---

## 4.5 Medir DORA e NPS

### 4.5.1 DORA

Use `devops/11-plataforma-interna/bloco-4/platform_metrics.py` ou o `devops/04-entrega-continua/bloco-1/calc_dora.py` com seus dados reais de CI (mesmo 2 semanas bastam).

```csv
# data/deployments.csv
data,squad,status
2026-09-10,capstone,success
2026-09-11,capstone,success
2026-09-12,capstone,failed
...
```

Publique em `docs/dora-report.md` com:

- Classificação atual.
- O que precisa para subir uma categoria.
- Meta do pós-capstone.

### 4.5.2 NPS interno simulado

Envie survey para 3-5 colegas/orientadores que leram seu repo. Mesmo que n=3, é dado **real**.

Perguntas (Módulo 11 §4.4.2). Calcule NPS e escreva plano:

- 2-3 melhorias priorizadas.
- O que não vai atacar e por quê (anti-escopo).

---

## 4.6 Preparação da banca

### 4.6.1 Estrutura do pitch (5-8 min)

```markdown
1. [60s] Problema
   - Quem e CivicaBR? Que dor resolve?
   - Metrica norte (ex.: notificacoes <= 5 min; SLA com prefeituras).

2. [90s] Arquitetura em 3 niveis
   - Cidadao -> API -> Worker -> DB/Queue/Cache.
   - Obs + Sec + SRE atravessando.
   - Diagrama Mermaid ao vivo OU slide.

3. [90s] Decisoes que importam
   - 3 ADRs escolhidos previamente (nao os mesmos que a banca pode escolher).
   - Trade-off e consequencia consciente.

4. [60s] Operacao real
   - DORA atual.
   - Error budget consumo.
   - Ultimo postmortem + licao.

5. [60s] Proximos 2 passos
   - Priorizado; justificativa rapida.

6. [Abre para incidente ao vivo]
```

### 4.6.2 Preparar o ambiente

- Ambiente **local pré-carregado** com dados de exemplo (seeders).
- Dashboards **já abertos** em janelas separadas.
- Runbooks **indexados** (favoritos do navegador).
- Script `make demo-up` sobe tudo em ≤ 5 min.

### 4.6.3 Incident script — três cenários que você domina

Escreva em `docs/banca-cenarios.md` três cenários com:

- O que a banca faz.
- Qual alerta você espera ver.
- Qual runbook abre.
- Comando exato para mitigar.
- Postmortem subsequente.

Ensaie cada um **2x cronometrado**. O objetivo não é "parecer intocável" — é **saber onde fica cada coisa** sob pressão.

Exemplos:

1. **Pod kill** → HPA restaura; runbook `api-5xx.md` se escalar.
2. **NetworkChaos entre API e DB** → alerta DB conn exhausted; runbook `db-conexoes-esgotadas.md`.
3. **Secret leak simulado** → Gitleaks no commit falhou (proteção); demo ação de rotação.

---

## 4.7 Roadmap pós-capstone

Em `docs/roadmap-pos.md`:

```markdown
# Roadmap pos-capstone (proximos 90 dias, se este fosse produto)

## Priorizado (top 3)
1. **Migrar DB para replica sincrona** - reduz RPO de 15 min para ~30s.
   - Custo: +R$ X/mes; +complexidade de operacao.
   - Desbloqueia: contratos com municipios maiores (SLA 99.95%).

2. **Feature flag provider real** (LaunchDarkly OSS/Unleash) - substitui flags manuais no codigo.
   - Custo: 1 dia de migracao; infra leve.
   - Desbloqueia: canary real e experimentos A/B.

3. **Automação de right-sizing** com OpenCost + VPA dry-run.
   - Custo: 2 dias.
   - Desbloqueia: visibilidade de custo por tenant para chargeback.

## Considerado, nao agora
- Multi-regiao geografica (> 6 meses).
- Mobile nativo (depende de demanda).
- i18n (depende de expansao).
- ML para classificacao automatica de categoria (nao prova ROI).

## Metrica de sucesso do trimestre
- DORA High -> Elite.
- NPS interno +15 -> +30.
- Zero incident de LGPD.
```

---

## 4.8 Postmortem final (obrigatório)

Mesmo que simulado, redija um postmortem completo.

Template em `docs/postmortems/_TEMPLATE.md`:

```markdown
# Postmortem: <titulo>

- Data do incidente: YYYY-MM-DD HH:MM
- Severidade: Sev-X
- Duracao: HH:MM
- Detectado por: <fonte>
- IC: <papel>
- Scribe: <papel>

## Impacto
Usuarios afetados, transacoes perdidas, SLA impactado, custo regulatorio.

## Timeline
- HH:MM [detectado] <o que>
- HH:MM [mitigado] <o que>
- HH:MM [resolvido] <o que>

## Causas contribuintes
> Linguagem blameless: causas sao **sistemas e condicoes**, nao pessoas.

- Caso-1: ...
- Caso-2: ...
- Caso-3: ...

## O que funcionou bem
- ...

## O que nao funcionou bem
- ...

## Sorte
- Fatos que poderiam ter piorado e nao pioraram.

## Acoes (com dono e prazo)
| # | Acao | Dono | Prazo | Ticket |
|---|------|------|-------|--------|
| 1 | ... | @autor | 2026-10-15 | #123 |
```

---

## 4.9 Apresentação consolidada

`docs/apresentacao.md` — deck mínimo ou roteiro em markdown.

### 4.9.1 Slides essenciais

| # | Slide | Tempo |
|---|-------|-------|
| 1 | Capa: CivicaBR em 1 frase | 5s |
| 2 | Problema e métrica norte | 45s |
| 3 | Arquitetura (diagrama) | 60s |
| 4 | 3 ADRs que definem o sistema | 90s |
| 5 | DORA + Error Budget | 60s |
| 6 | Último postmortem + lição | 60s |
| 7 | Próximos 2 passos | 45s |
| 8 | Pergunta: "onde quer que eu injete falha?" | 15s |

Não passe de 8 slides. Uso de dashboards ao vivo > slides estáticos.

---

## 4.10 Autoavaliação antes da banca

Use a rubrica completa de [entrega-avaliativa.md](../entrega-avaliativa.md) como self-check:

```bash
python scripts/capstone_checklist.py .
```

(Ver `exercicios-progressivos/parte-5-banca-final.md` para o script.)

O script deve retornar verde nos itens **obrigatórios** da rubrica.

---

## 4.11 Checklist de aceitação da Fase 4

### Plataforma
- [ ] Software Catalog publicado (Backstage ou leve) com ownership.
- [ ] Golden path template + 1 serviço gerado via template.
- [ ] TechDocs / docs navegáveis (MkDocs ou Backstage plugin).

### Métricas
- [ ] DORA calculado com dados reais do capstone.
- [ ] NPS coletado (n ≥ 3).
- [ ] Plano de ação baseado nos dados.

### Documentação
- [ ] ADRs atualizados (ao menos 1 revisado/superseded por contexto evoluído).
- [ ] Postmortem blameless preenchido.
- [ ] Roadmap pós-capstone priorizado.

### Banca
- [ ] `make demo-up` sobe em ≤ 5 min.
- [ ] 3 cenários de incidente ensaiados 2× cada.
- [ ] Pitch em 5-8 min, ensaiado.
- [ ] Dashboards prontos em abas separadas.

---

## 4.12 Armadilhas comuns

- **Platform teatral**: Backstage com catálogo de 1 componente. Se for minimalista, ao menos **seja honesto** — documente como "nível provisional (CNCF)".
- **DORA com dados plantados.** Se inventar, a banca descobre perguntando o input. Use dados reais, mesmo escassos.
- **Postmortem com `root cause = bug do dev`.** Postmortem blameless analisa sistema: *por que a release deixou passar?*
- **Não ensaiar o incidente.** Chegar na banca esperando "dar certo" é o erro mais comum.
- **Roadmap ambicioso demais.** Banca pergunta "por que esses 3?"; você precisa **defender** a escolha contra alternativas.
- **Dashboards com dados de 1 hora atrás** porque o ambiente não ficou ligado. Ensaiar live é mandatório.

---

## 4.13 Encerramento

No dia da banca:

1. Chegue com ambiente **já de pé** (não suba na frente).
2. Leve 1 plano B (ambiente em cloud leve ou gravação do demo) caso algo exploda.
3. Ao perder controle, **reconheça**: *"esse cenário não ensaiei; vou abrir o runbook X e seguir"*. Honestidade > blefagem.
4. No final, **feche** com o roadmap — mostra que você sabe onde o projeto **iria**.

Bom capstone. Você está mais próximo do engenheiro DevOps sênior do que quando começou o curso.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 3 — Armadilhas, dicas e orientações de banca](../bloco-3/03-armadilhas-e-dicas.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Fase 4 — Armadilhas, dicas e orientações de banca](04-armadilhas-e-dicas.md) |

<!-- nav:end -->
