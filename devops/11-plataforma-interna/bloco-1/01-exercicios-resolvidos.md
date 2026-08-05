# Bloco 1 — Exercícios resolvidos

> Leia [01-platform-engineering.md](./01-platform-engineering.md) antes.

---

## Exercício 1 — Classificar times (Team Topologies)

**Enunciado.** Para cada time, classifique (Stream-aligned / Platform / Complicated-subsystem / Enabling) e justifique:

1. Squad "aluguel-marketplace" (OrbitaTech): mantém o produto principal da empresa.
2. Squad "ml-score": mantém modelo de score de crédito, complexo matematicamente.
3. Platform Team (objeto do módulo).
4. Squad "devex-coaches": visita squads por 4 semanas para ajudá-los a adotar OpenTelemetry.
5. Squad "ops-24x7": resolve incidentes de todos os serviços; abre tickets para os donos.

**Respostas.**

1. **Stream-aligned.** Entrega valor direto ao cliente final (locatários e proprietários). Dono do fluxo de valor.
2. **Complicated-subsystem.** Expertise profunda (ML); encapsula complexidade para outros squads consumirem a saída (`/score?cpf=...`).
3. **Platform.** Oferece capabilities self-service para reduzir cognitive load. Modo padrão: X-as-a-Service.
4. **Enabling.** Coaches temporários; capacitam squads para fazer sozinhos. Não "dono" de sistema.
5. **Não é Team Topology saudável.** É a clássica "Ops Team" que vira bottleneck. Corrigir: responsabilidade operacional volta aos squads donos; Platform Team fornece tooling; SRE coaches (Enabling) ajudam quando squad está imaturo.

---

## Exercício 2 — Reduzir cognitive load

**Enunciado.** O squad "condominios" respondeu 5/5 em sobrecarga. Entrevista revelou:
- Mantém 8 microsserviços.
- Cada um tem pipeline CI levemente diferente.
- Mantém seu próprio chart Helm "customizado".
- Faz o próprio release notes manualmente.
- Opera seu Prometheus isolado.

Proponha 3 ações do Platform Team para reduzir cognitive load, priorizadas.

**Respostas.**

1. **Consolidar observabilidade** (prioritária): migrar Prometheus isolado do squad para o stack compartilhado da plataforma. Reduz 1 ferramenta e ~ 3h/semana de manutenção. **Alto valor, baixo risco, baixo custo**.
2. **Template de CI reutilizável**: disponibilizar GitHub Action composite que substitui boa parte do pipeline custom. Oferecer migração assistida para os 8 serviços ao longo de 3 sprints. **Remove extraneous de cada PR**.
3. **Helm chart padrão** (`orbita-service`): absorver variações em `values.yaml`. Requer investimento maior (~ 4 semanas) porque precisa cobrir casos legítimos. **Reduz dialetos; base para futuras capabilities**.

Deixadas para depois (por enquanto):
- Consolidar 8 microsserviços — isso é decisão de produto/arquitetura, não de plataforma.
- Release notes automáticos — útil mas baixo impacto em cognitive load.

**Princípio**: não remover tudo de uma vez; priorizar por **valor / esforço** e **reversibilidade**.

---

## Exercício 3 — Golden path vs. gold-plated

**Enunciado.** O Platform Team está criando template "serviço Python". Um dos membros propõe adicionar:

- Integração Prometheus (padrão).
- Integração com **serviço de fila de trabalho** que só 2 squads usam.
- Integração com **gRPC** que 3 squads usam.
- **Dashboard de health empresarial** (link ao Confluence) que 100% dos squads usam.
- **IA assistant** opcional, que ninguém pediu.

Classifique cada item como *incluir no golden path*, *incluir como opção no Scaffolder* ou *deixar fora*. Justifique.

**Respostas.**

| Item | Decisão | Justificativa |
|------|---------|---------------|
| Prometheus | **Incluir (default)** | 100% dos serviços precisam de observabilidade. Obrigatório. |
| Fila de trabalho (2 squads) | **Deixar fora** | Menos de 30% adoção; cria gold-plating. Se quiserem, oferece biblioteca separada. |
| gRPC (3 squads) | **Opção no Scaffolder** | Uso médio; oferecer checkbox "Expor gRPC?" que gera os arquivos extras quando marcado. |
| Dashboard health Confluence | **Incluir como doc inicial** | Todo mundo usa; inclui na TechDocs; zero-custo. |
| IA assistant | **Deixar fora** | Ninguém pediu; ouça usuários antes de adicionar. Voltará a ser avaliado se sair em discovery. |

**Regra**: **defaults agradam maioria; opções cobrem minoria válida; resto fica de fora.**

---

## Exercício 4 — Interpretar survey

**Enunciado.** Rode `cognitive_load_survey.py` com o CSV do bloco. Interprete: quais squads são prioridade? Quais perguntas você faria em entrevista follow-up?

**Saída esperada:**

```
Cognitive load por squad
squad                    respondentes  sobrecarga(avg)  ferramentas(avg)  servicos(avg)  status
condominios              2             5.00             13.5              8.0            ALTO
aluguel-marketplace      2             4.00             11.0              5.5            ALTO
score-inquilino          2             2.50             7.0               2.5            ok

2/3 squads acima do threshold 3.5
```

**Interpretação:**

- **condominios** é o mais crítico: 5 pontos, 13 ferramentas (contra 7 de score-inquilino), 8 serviços (vs 2-3). Correlação clara: muitos serviços + muitas ferramentas → sobrecarga.
- **aluguel-marketplace** em segundo lugar: 11 ferramentas, 5 serviços.
- **score-inquilino** saudável.

**Entrevistas follow-up (condominios primeiro):**

1. *"Quais dessas 13 ferramentas você realmente precisa usar por semana? Quais são 'ruído'?"*
2. *"Se desse para consolidar 3 delas em uma capability da plataforma, quais? E qual seria o ganho semanal?"*
3. *"Dos 8 serviços, quantos vocês efetivamente operam? Algum é zumbi?"* (candidato a sunset)
4. *"O comentário 'fazemos de tudo' — pode dar um exemplo concreto de um dia típico?"*
5. *"Em 3 meses, se tudo der certo com a plataforma, como seria seu dia?"* (construir visão compartilhada)

---

## Exercício 5 — Definir personas

**Enunciado.** Liste 3 personas do Platform Team na OrbitaTech, com 3-5 atributos cada.

**Resposta.**

```markdown
## Persona 1 — "Bruno, Dev Pleno recém-chegado"
- 6 anos em Python/FastAPI; chegou em fevereiro.
- Primeira vez em empresa com Kubernetes e 47 microsserviços.
- Quer entregar sua primeira feature em produção rapido.
- Frustra com "qual repo devo clonar?" "qual chart usar?".
- JTBD (Jobs-to-be-done): "Quando um novo projeto comeca, eu quero um
  jeito de criar o repositorio e a infra em minutos, para entregar em dias
  (nao semanas)."

## Persona 2 — "Carla, Tech lead de squad"
- 10 anos carreira; lidera squad de 6 engenheiros.
- Responsavel por SLO do seu produto.
- Nao quer virar especialista em Kubernetes ou Istio.
- Frustra com diferenca entre charts, com migracoes de versao dictadas
  "de cima" sem janela.
- JTBD: "Quando a plataforma evolui, eu quero entender prazo e impacto
  claramente, para planejar migracao sem atrapalhar entrega de produto."

## Persona 3 — "Diego, Platform Engineer do time"
- O autor da plataforma.
- Quer saber adocao, reclamacoes, bugs.
- Precisa decidir roadmap com base em dado.
- Frustra quando escuta squads reclamando em corredor mas nao no canal
  oficial de feedback.
- JTBD: "Quando proponho mudanca, eu quero saber quem usa o que,
  para avaliar impacto antes de anunciar."
```

**Por que 3 personas?** Platform serve tanto quem **usa** (Bruno, Carla) quanto quem **constrói** (Diego). Ignorar Diego = esquecer operação da plataforma.

---

## Exercício 6 — Posicionar maturidade

**Enunciado.** Com os dados do cenário OrbitaTech (shadow IT, onboarding 3-6 semanas, 47 pipelines distintos, 8 dialetos Helm, serviço órfão, custo crescendo 12% ao mês), posicione no CNCF Platform Maturity Model e proponha 3 marcos para avançar um nível.

**Resposta.**

**Posicionamento atual**: **Provisional** (nível 1).

- Existem ferramentas isoladas (K8s, pipelines, Helm) — mas **sem produto**.
- Shadow IT significa que **não há plataforma de referência** confiável.
- Ausência de catálogo e ownership formal sinalizam falta de governança.

**Marcos para chegar a Operational** (nível 2) no próximo trimestre:

1. **Software Catalog com ≥ 80% dos serviços** mapeados (owner, SLO, dependencies). Sem catálogo, nada mais se sustenta.
2. **1 golden path publicado e usado** por ≥ 3 squads voluntariamente. Se ninguém usa, não é plataforma; é wishful thinking.
3. **Survey inicial de cognitive load e NPS interno** realizada. Base para roadmap. Sem baseline, não se mede melhoria.

**Para Scalable (nível 3) em 12 meses:**

- ≥ 60% dos novos serviços começam via golden path.
- SLOs internos da plataforma (disponibilidade do portal, tempo de scaffolding) mensurados e publicados.
- Governança de deprecation com RFC e prazo.

---

## Autoavaliação

- [ ] Aplico Lei de Conway e o inverse Conway maneuver.
- [ ] Classifico times em Team Topologies.
- [ ] Explico cognitive load e propõo ações de redução.
- [ ] Diferencio golden path de gold-plated.
- [ ] Desenho persona e JTBD para Platform Team.
- [ ] Interpreto saída do survey.
- [ ] Posiciono uma plataforma no CNCF Platform Maturity Model.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Bloco 1 — Platform Engineering: times, cognitive load e produto interno](01-platform-engineering.md) | **↑ Índice**<br>[Módulo 11 — Plataforma interna](../README.md) | **Próximo →**<br>[Bloco 2 — Backstage e Golden Paths](../bloco-2/02-backstage-golden-paths.md) |

<!-- nav:end -->
