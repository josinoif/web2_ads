# Fase 4 — Armadilhas, dicas e orientações de banca

> Complemento à [Fase 4 — Plataforma e apresentação final](./04-fase-plataforma.md).

---

## 1. O que a banca realmente avalia na defesa

Nesta fase a avaliação muda de natureza. Até a Fase 3, estávamos olhando artefatos estáticos. Na banca, olhamos **a pessoa operando** o que construiu.

Três qualidades **não-técnicas** pesam aqui:

### 1.1 Clareza mental sob pressão

Quando a banca injetar uma falha, o **primeiro sinal** é o que você diz nos 10 segundos iniciais. Bons candidatos:

- *"Ok, alerta X está tocando. Vou abrir o dashboard Y."*

Candidatos que ainda não amadureceram:

- *"Hmm, deixa eu pensar..."* (silêncio).

Treino resolve. Ensaie em voz alta.

### 1.2 Honestidade sobre limites

A banca valoriza *"esse cenário específico eu não ensaiei — vou raciocinar em voz alta e seguir o runbook"* **mais** do que um falso controle. Fingir domínio é o erro que mais custa.

### 1.3 Capacidade de fazer trade-off

Quase toda pergunta boa da banca termina com *"e se fosse diferente?"*. Resposta madura: *"Se contexto fosse X, escolheria Y por razão Z. Registrarei em novo ADR."*

---

## 2. O que mostrar ao vivo — prioridade

Se tiver 20 min na banca, divida:

| Tempo | Atividade |
|-------|-----------|
| 5-8 min | Pitch estruturado (Fase 4 §4.6.1). |
| 5-8 min | Incidente simulado + mitigação + explicação. |
| 4-6 min | Q&A sobre ADRs. |

Nunca gaste todo tempo no pitch — a parte **operacional** é o diferencial.

---

## 3. Perguntas inevitáveis e respostas-modelo

### 3.1 *"Se você tivesse mais 3 meses, o que faria primeiro?"*

Resposta ruim: *"Melhoraria o frontend."*
Resposta boa: *"Migraria o DB para replica síncrona — atacando o RPO medido de 15 min, que é o gap mais caro do SLA contratual; segundo passo, feature flag provider real; terceiro, chargeback automatizado."*

### 3.2 *"Qual foi sua maior surpresa no projeto?"*

Resposta ruim: *"Tudo funcionou como esperado."* (improvável; sugere superficialidade).
Resposta boa: *"Chaos Engineering — descobri que meu readiness probe estava muito relaxado; alertas não disparavam durante 30s de indisponibilidade real. Corrigi em ADR-0011."*

### 3.3 *"Qual seu maior risco hoje?"*

Resposta ruim: *"Não há riscos; está tudo OK."*
Resposta boa: *"Dependência de um único cluster. Se falhar catastroficamente, tenho DR playbook mas RTO ainda é 2h — acima do SLA. Mitigação planejada: multi-AZ no 2º trimestre."*

### 3.4 *"Um postmortem seu: conte do começo ao fim."*

Resposta ruim: narrativa sobre "o erro do dev".
Resposta boa: **sistema falhou porque X + Y + Z**; ação **N** implementada; métrica **M** valida se eficaz em 30 dias.

---

## 4. Anti-padrões da defesa

- **Slides densos** projetados enquanto você fala a mesma coisa. A banca **lê ou ouve**, não ambos.
- **Roteiro decorado**. Soa falso quando desviado. Prefira 5 marcos mentais + improviso natural.
- **Mostrar cada ferramenta** (Trivy, Syft, Cosign...). Menos = mais. 3 capacidades bem defendidas > 20 mencionadas.
- **Ignorar a câmera/banca** e focar no terminal. Olhe para quem avalia **metade do tempo**.
- **Debochar do próprio projeto** ("isso aqui é tosco mas..."). Vende menos. Se algo é limitação, **reconheça + aponte roadmap**.

---

## 5. Dicas de ensaio

### 5.1 Ensaio solo

1. Grave-se com câmera no celular (2 tomadas).
2. Reveja em 1.25x — olhe **tiques** (uhm, deixa, né).
3. Repita o cenário de incidente **cronometrado**.
4. Escreva 3 respostas que deseja melhorar — ensaie.

### 5.2 Ensaio com alguém

Pegue um colega que **não leu** seu repo. Peça:

1. Leia meu README por 5 min.
2. Monte 3 perguntas que te intrigaram.
3. Faça estas perguntas como banca.

Você descobre lacunas que o autor do projeto nunca vê.

### 5.3 Ensaio com incidente

Peça ao mesmo colega para, **sem avisar**:

- Escolher **1 entre 3** cenários que você preparou.
- Rodar o comando de injeção de falha.

Simule a banca integral. Uma única prática disso muda o dia real.

---

## 6. Erros que reprovam na banca

- Ambiente não sobe em 10 min → já perdeu 20% antes de falar.
- Dashboards mostram dados estáticos de 3 dias atrás → observability é teatro.
- Mata um Pod manualmente como "demo de chaos" em vez de usar Chaos Mesh.
- Postmortem culpa pessoa.
- Incapacidade de ler um dashboard simples que você mesmo criou.
- Git push de segredo durante a defesa (já aconteceu — verifique `.gitignore` e hooks).

---

## 7. Pós-banca

Independente do resultado, nas 48h seguintes:

1. **Tag final**: `git tag v1.0.0-capstone-defended`.
2. **Retrospective pessoal** (1 página): o que surpreendeu, o que mudaria, o que estou orgulhoso.
3. **Postar** um resumo técnico (blog, Dev.to, LinkedIn) — o exercício de **escrever para desconhecido** consolida aprendizado e serve para entrevistas futuras.
4. **Atualizar CV** com 3 bullets orientados a impacto:
   - *"Projetei e operei plataforma civic-tech multi-tenant com SLOs formais e Error Budget Policy; RTO medido 2h em DR drill."*
   - *"Entreguei CI/CD com supply chain (SBOM + Cosign) e admission control Kyverno exigindo imagens assinadas."*
   - *"Reduzi time-to-deploy via golden path reprodutível e catálogo Backstage; DORA High sustentado por 4 semanas."*

A melhor parte do capstone é **poder falar dele com profundidade** por anos depois.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Fase 4 — Plataforma interna, métricas e apresentação final](04-fase-plataforma.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Marcos do Capstone — roteiro de 5 partes](../exercicios-progressivos/README.md) |

<!-- nav:end -->
