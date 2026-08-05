# Parte 3 — Feature Flags e Estratégia de Release

> **Duração:** 1 hora.
> **Objetivo:** implementar **feature flags** no serviço Tracking e **escolher** uma estratégia de release documentada.

---

## Contexto

O pipeline da Parte 2 leva o artefato à produção. Falta agora **controlar o que o usuário vê** — e permitir **rollback por flag** sem novo deploy. Este é o momento de concretizar a lição do Bloco 3: **deploy ≠ release**.

---

## Tarefas

### 1. Copiar `features.py` do Bloco 3

Leia o [Bloco 3, seção 5.1](../bloco-3/03-estrategias-release.md#51-implementação-simples-em-python). Copie o módulo `features.py` para `src/tracking/features.py` — com as 4 flags do catálogo.

Adicione **uma flag nova**, específica para a sua visão do domínio. Sugestões:

- `notificacao_sms_em_lote` (OPS)
- `endpoint_v2_rastreio` (RELEASE)
- `cache_agressivo_consulta` (OPS)
- outra que você justifique

### 2. Expor as flags via endpoint de debug

Adicione a `src/tracking/api.py`:

```python
from tracking.features import catalogo, is_enabled


@app.get("/debug/flags")
def debug_flags():
    """Expõe o estado atual das flags — útil para diagnóstico."""
    return {
        f.name: {
            "default": f.default,
            "tipo": f.tipo.value,
            "atual": is_enabled(f),
            "expira_em": f.expira_em,
        }
        for f in catalogo()
    }
```

**Atenção de segurança:** em produção real, esse endpoint seria **protegido** por auth e com scope interno (ex.: só VPC privada). Documente essa ressalva no seu README.

### 3. Usar pelo menos 2 flags no código real

Escolha **duas flags** que ativam comportamentos distintos. Exemplos:

**Exemplo A — flag de RELEASE para endpoint novo:**

```python
from tracking.features import is_enabled, ENDPOINT_V2_RASTREIO


@app.get("/rastreio/{codigo}")
def rastrear_v1(codigo: str):
    # versão antiga — sempre responde
    return {"codigo": codigo, "status": "EM_ROTA"}


@app.get("/v2/rastreio/{codigo}")
def rastrear_v2(codigo: str, cliente_id: str = ""):
    if not is_enabled(ENDPOINT_V2_RASTREIO, subject=cliente_id):
        raise HTTPException(status_code=404, detail="endpoint indisponível")
    return {
        "codigo": codigo,
        "status": "EM_ROTA",
        "estimativa_minutos": 120,
        "telemetria": {"ultima_posicao": [-23.5, -46.6]},
    }
```

**Exemplo B — flag OPS como kill switch:**

```python
from tracking.features import is_enabled, CACHE_AGRESSIVO_CONSULTA


@app.get("/consulta/{codigo}")
def consulta(codigo: str):
    if is_enabled(CACHE_AGRESSIVO_CONSULTA):
        dados = buscar_do_cache(codigo)  # TTL de 60s
        if dados is not None:
            return dados
    return buscar_do_banco(codigo)
```

### 4. Testes determinísticos para as flags

Copie os testes do Bloco 3 ([seção 5.2](../bloco-3/03-estrategias-release.md#52-testando-feature-flags)) para `tests/unit/test_features.py` e adapte para **suas flags** (nome).

Garanta os 5 casos base para cada flag:

- Default sem env.
- Override via env bool.
- Percent 0 → todos OFF.
- Percent 100 → todos ON.
- Percent 50 → distribuição ~50% (1000 subjects).

### 5. Documentar a estratégia de release

Crie `docs/estrategia-release.md` (2 páginas) com os seguintes tópicos:

#### a) Qual estratégia escolheu e por quê

- Blue-Green? Canary? Rolling? Feature flag como canary simulado? Combinação?
- Argumente usando trade-offs do Bloco 3 — **custo de infra**, **velocidade de rollback**, **exigência de retrocompat**, **detecção de bugs estatísticos**.

#### b) Diagrama Mermaid do fluxo

Da aprovação em produção até "feature liberada para 100%". Inclua **feature flags** no fluxo.

#### c) Critérios objetivos de promoção

Ex.: "flag a 10% por 1 dia, se CFR < 2%, sobe para 25%". Use os critérios do [Bloco 3 — Exercício 5](../bloco-3/03-exercicios-resolvidos.md#exerc%C3%ADcio-5--crit%C3%A9rios-de-promo%C3%A7%C3%A3o-canary).

#### d) Critérios de rollback por flag

Ex.: "5xx > 1% sustentado por 2 min → `FLAG_X=0`". **NÃO é novo deploy** — é mudança de variável de ambiente.

#### e) ADR 001 — justificativa da escolha

Em `docs/adr/001-artefato-imutavel.md` já existe (Parte 2 ou Entrega Avaliativa). Agora crie **ADR 002** em `docs/adr/002-estrategia-release.md`:

```markdown
# ADR 002 — Estratégia de Release

## Status
Aceita — 2026-04-21

## Contexto
A LogiTrack precisa liberar features novas no serviço Tracking API com capacidade de **rollback em minutos** e detecção precoce de regressões. Não temos ainda proxy L7 para canary real em infraestrutura.

## Decisão
Adotar **Rolling update** para o deploy (padrão do provedor de K8s que adotaremos no Módulo 7) combinado com **feature flag percentual** para release gradual. Essa combinação nos dá:

- Deploy do artefato independente da liberação da feature.
- Rollback de feature em segundos (flag=0) sem novo deploy.
- Detecção estatística (ao liberar 10%) antes de afetar todos.

## Consequências
### Positivas
- MTTR projetado < 15 min para incidentes de feature.
- Permite experimentos (A/B) com o mesmo mecanismo.

### Negativas / riscos
- Débito de flags: precisamos remover quando estabilizam (política de 2 meses).
- Testes precisam cobrir ambos os caminhos (on/off).

## Alternativas descartadas
- Blue-Green em 100% dos serviços: dobra custo de infra. Consideramos apenas para Billing.
- Canary em proxy L7: aguarda Módulo 7 (Kubernetes).
```

### 6. Simular liberação progressiva

Documente em `docs/simulacao-release.md` um **passo-a-passo** de liberação da **flag nova** que você adicionou:

```markdown
# Simulação — liberação da flag `endpoint_v2_rastreio`

Dia 1 (deploy do artefato, feature OFF globalmente):
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO=false

Dia 2 (canary 10%):
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO_PERCENT=10
  (monitorar 5xx, p95; baseline OK → continuar)

Dia 3 (25%):
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO_PERCENT=25

Dia 5 (50%):
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO_PERCENT=50

Dia 7 (100%):
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO_PERCENT=100

Dia 14 (feature estabilizada, voltar para bool):
  unset LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO_PERCENT
  export LOGITRACK_FLAG_ENDPOINT_V2_RASTREIO=true

Dia 30 (remover flag do código):
  (PR removendo a flag, expirando conforme `expira_em`)
```

---

## Entregáveis

```
logitrack-tracking/
├── src/tracking/
│   ├── api.py               # com endpoints que usam flags
│   └── features.py          # catálogo com pelo menos 5 flags
├── tests/unit/
│   └── test_features.py     # 8+ testes, todos passando
├── docs/
│   ├── estrategia-release.md
│   ├── simulacao-release.md
│   └── adr/
│       ├── 001-artefato-imutavel.md
│       └── 002-estrategia-release.md
```

---

## Critérios de sucesso

- [ ] `features.py` com **pelo menos 5 flags**, uma adicionada por você com justificativa.
- [ ] Endpoint `/debug/flags` funcionando.
- [ ] **Pelo menos 2 flags** usadas no código real (não apenas no `debug_flags`).
- [ ] Testes determinísticos — **todos passando** (mostrar saída de `pytest`).
- [ ] `estrategia-release.md` cobrindo os 5 tópicos (estratégia, diagrama, promoção, rollback, ADR 002).
- [ ] ADR 002 escrito no formato do template.
- [ ] `simulacao-release.md` mostrando liberação de 0% → 100% com comandos.

---

## Dicas

- **Não escolha Blue-Green só porque é mais simples de explicar.** Justifique com os trade-offs da LogiTrack.
- A **escolha combinada** (Rolling + Flag) é o padrão moderno — e é defendível para este caso.
- **Cuidado com testes flaky** do `percent 50 ~= 50%` — use faixa 420-580 (delta ±8%) para 1000 amostras.
- O endpoint `/debug/flags` é **útil para demonstrar** em avaliação — capture screenshot mostrando `curl .../debug/flags`.

---

## Próximo passo

[Parte 4 — Rollback e Migration Expand/Contract](parte-4-rollback-migration.md). Agora o sistema libera features; vamos garantir que desfaz quando precisa.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 2 — Pipeline Multi-estágio com Artefato Único](parte-2-pipeline-multi-estagio.md) | **↑ Índice**<br>[Módulo 4 — Entrega contínua](../README.md) | **Próximo →**<br>[Parte 4 — Rollback e Migration Expand/Contract](parte-4-rollback-migration.md) |

<!-- nav:end -->
