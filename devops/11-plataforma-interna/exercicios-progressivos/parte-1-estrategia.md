# Parte 1 — Estratégia, personas e Team Topologies

**Objetivo.** Antes de qualquer código, fundar **a intenção da plataforma**: quem são os clientes, quais problemas resolve, como se organiza o time, quais são os caminhos "pavimentados" e quais não serão.

**Pré-requisitos.** Leitura do Bloco 1.

**Entregáveis em `orbita-idp/docs/`:**

1. `platform-strategy.md` — estratégia geral (ver template abaixo).
2. `personas.md` — 3 personas com JTBD.
3. `team-topologies.md` — declaração do tipo (Platform Team) e modos de interação.
4. `anti-golden-paths.md` — o que **não** é suportado.
5. `roadmap.md` — próximas 3 sprints (12 semanas), com decisões-alvo.

---

## 1.1 `platform-strategy.md`

**Template mínimo.**

```markdown
# Estrategia da plataforma OrbitaTech

## Missao
Reduzir tempo do commit a producao de 9 dias (atual) para <= 1 dia, sem sacrificar
qualidade (change failure rate <= 15%), oferecendo um produto interno
que squads usem por **escolha**.

## Publico-alvo
~420 engenheiros em 28 squads.

## Problemas-chave
1. Onboarding lento (3-6 semanas).
2. 47 pipelines distintos; 8 dialetos de Helm.
3. Shadow IT (3 ArgoCDs paralelos).
4. Custo cloud crescendo 12%/mes sem ownership.
5. Inconsistencia de segurança (apenas 11 de 47 services com cosign).

## Hipoteses
H1. Um golden path `python-fastapi` bem feito sera adotado por >= 3 squads
    em 2 sprints.
H2. TechDocs versionada com template eleva adocao de docs para > 80%.
H3. Contratos de capability (tiers) reduzem discussao caso-a-caso em 50%.

## Nao-objetivos (nesta fase)
- Nao oferecer substituicao de Kafka (plataforma consome o existente).
- Nao oferecer CI para stacks fora do mainstream (Ruby, Perl).
- Nao operar servicos de produto (squad continua dono operacional).

## Modelo de relacionamento
X-as-a-Service com Platform Team. Enabling Team (temporario) para
onboarding assistido em primeiros 2 trimestres.

## Plataforma como produto
- PM informal: @platform-lead
- Cadence: survey trimestral; roadmap publico; office hours semanais.
- Metrica norte: NPS interno > +20 ate final do ano; DORA High.
```

## 1.2 `personas.md`

Três personas obrigatórias:

1. **Engenheiro novo** (primeiros 30 dias).
2. **Tech lead experiente** (líder de squad produto).
3. **Platform Engineer** (dentro do seu time).

Para cada: contexto, dor atual, JTBD, sinal de sucesso.

## 1.3 `team-topologies.md`

- Declarar: você é **Platform Team**.
- Listar outros times relevantes (stream-aligned, enabling, complicated-subsystem).
- Indicar **modos de interação** com cada um (collaboration, X-as-a-Service, facilitation).
- Diagrama Mermaid do ecossistema.

## 1.4 `anti-golden-paths.md`

Lista **explícita** do que a plataforma **não** suporta:

- Ruby novo (legado continua).
- MongoDB (Postgres é o padrão).
- Python 3.9 ou menor.
- Servico sem SLO declarado.
- Deploy sem observability padrão.

Por quê cada decisão.

## 1.5 `roadmap.md`

Próximas 3 sprints (6 semanas cada? 2 semanas cada?). Cada uma com:
- Metas.
- Riscos.
- Dependências.
- Métrica que confirma sucesso.

---

## Critérios de aceitação da Parte 1

- [ ] Documentos versionados em `docs/`.
- [ ] `platform-strategy.md` contém missao, problemas, hipoteses, nao-objetivos.
- [ ] `personas.md` com ≥ 3 personas, cada uma com JTBD real (não genérico).
- [ ] `team-topologies.md` com diagrama Mermaid.
- [ ] `anti-golden-paths.md` com ≥ 5 itens.
- [ ] `roadmap.md` cobre ≥ 3 sprints com metas mensuráveis.
- [ ] Um PR único; commit message descreve o marco.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Exercícios progressivos — Módulo 11 (Plataforma Interna)](README.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Parte 2 — Backstage e Software Catalog](parte-2-backstage-catalogo.md) |

<!-- nav:end -->
