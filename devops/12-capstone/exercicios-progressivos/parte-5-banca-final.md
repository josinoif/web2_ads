# Marco 5 — Defesa com incidente ao vivo

**Tag alvo:** `v1.0.0-capstone-defended` (após a banca).
**Tempo sugerido:** 1 semana de ensaio + dia da defesa.
**Fase correspondente:** [Fase 4 — final](../bloco-4/04-fase-plataforma.md) + [armadilhas](../bloco-4/04-armadilhas-e-dicas.md).

---

## Objetivo

Defender o capstone em banca, incluindo:

1. **Pitch** arquitetural (5-8 min).
2. **Incidente ao vivo** injetado pela banca, conduzido com runbook + observabilidade.
3. **Q&A** sobre decisões (ADRs, alternativas, próximos passos).

Aqui se verifica se você é **engenheiro**, não apenas operador de repositório.

---

## Entregáveis antes da banca

### Preparação
- [ ] `scripts/capstone_checklist.py` retornando verde nos itens **obrigatórios**.
- [ ] `docs/apresentacao.md` com roteiro do pitch.
- [ ] `docs/banca-cenarios.md` com 3 cenários ensaiados:
  - Cenário A: pod kill / node drain.
  - Cenário B: NetworkChaos entre API e DB.
  - Cenário C: alerta LGPD / secret leak / CVE crítica.
- [ ] `make demo-up` que sobe ambiente de demonstração em ≤ 5 min.
- [ ] Dashboards pré-carregados em abas do navegador.
- [ ] Gravação de backup caso o ambiente exploda na hora (≤ 3 min).

### Pós-banca
- [ ] Tag `v1.0.0-capstone-defended`.
- [ ] `docs/retro/marco5.md` com retrospectiva final (o que deu certo, o que faria diferente).
- [ ] README raiz com seção "Resultado do capstone" linkando a defesa (ou vídeo).
- [ ] Blog post (curto) ou LinkedIn post compartilhando 1 lição técnica.

---

## O dia da banca

### Antes
- Teste `make demo-up` 30 min antes.
- Feche aplicativos desnecessários; evite notificações.
- Tenha água.
- Verifique conexão de rede (backup: hotspot do celular).

### Durante
- Respire fundo nos primeiros 10s.
- Repita a pergunta da banca para dar tempo de pensar.
- **Pense em voz alta** quando não souber — é aceito e valorizado.
- Nunca culpe ferramenta/professor/aluno. Leve o problema ao sistema.

### Depois
- Agradeça a banca.
- Anote **imediatamente** as 3 perguntas mais difíceis — viram ADR/RFC futuras.
- Tome um café.

---

## Roteiro sugerido do pitch (8 min)

| min | Tópico | Apoio visual |
|-----|--------|--------------|
| 0-1 | CivicaBR em 1 parágrafo; SLA contratual com municípios | Slide 1 |
| 1-2 | Arquitetura em 3 camadas | Diagrama Mermaid |
| 2-4 | 3 ADRs que definem o sistema | Slide 3 links |
| 4-5 | DORA atual + EBP exemplo | Dashboard live |
| 5-6 | Último postmortem + lição | Postmortem aberto |
| 6-7 | Roadmap top-3 | Slide |
| 7-8 | Convite: "onde querem que injete falha?" | Terminal live |

---

## Script do incidente ao vivo — cenário A (exemplo)

Banca pede: *"Mate 1 Pod da API."*

```bash
# Você mostra ação (narra em voz alta)
kubectl get pods -n staging -l app=api
kubectl delete pod -n staging api-5f9c...  # um dos 2

# Em paralelo, abre dashboard
# Narração esperada:
# "Observe o painel 'golden signals api'. Em ~20s o HPA mantém a réplica viva.
#  Readiness probe em 5s; o novo Pod entra em rotação em ~30s.
#  Se 2xx cair abaixo do SLO, alerta fast-burn dispara em até 5 min."

# Se alerta dispara:
# "Abro o runbook api-5xx.md; ele orienta verificar rollout; rollout OK.
#  Mitigação automática; sem ação humana necessária.
#  Postmortem não obrigatório (Sev-3 ou inferior)."
```

Se a banca insistir em algo que você **não** ensaiou:

```
"Esse cenário não estava no meu script. Vou raciocinar em voz alta:
 (1) abrir dashboard; (2) identificar métrica afetada; (3) ir ao runbook
 relacionado; (4) agir; (5) documentar se novo.
 Isso, para mim, é mais honesto do que improvisar sem método."
```

Essa frase, dita com calma, vale **pontos**.

---

## Script Python para autoavaliação

Rode antes de marcar a banca:

```bash
python ../scripts/capstone_checklist.py .
```

Se sair amarelo/vermelho em algum **obrigatório**, atrase a defesa.

Ver [`../scripts/capstone_checklist.py`](../scripts/capstone_checklist.py) (descrito na [seção scripts](#scripts)).

---

## Critérios de avaliação na banca

Ver [`../entrega-avaliativa.md`](../entrega-avaliativa.md) § 3 (Defesa ao vivo).

---

## Armadilhas no dia

- Mudar config de último minuto e quebrar.
- Subir ambiente pela primeira vez na frente da banca.
- Tentar impressionar com jargão (backfires).
- Ler slides em vez de conversar.
- "Essa pergunta não foi combinada" — nunca diga isso.

---

## Depois do capstone

Você terminou um curso de DevOps com um **projeto defensável**. O que fazer com isso:

1. **Atualizar CV** — 3 bullets orientados a impacto.
2. **Repositório público** — com README excelente, serve de portfólio anos.
3. **Compartilhar aprendizado** — blog post, talk em meetup.
4. **Aplicar em trabalhos reais** — cada decisão registrada no capstone vira ADR futuro onde trabalhar.

---

## Pergunta de fechamento

> *"Daqui a 2 anos, se alguém perguntar sobre o seu capstone, o que você quer conseguir dizer sobre ele?"*

Esse é o critério real. A banca é só um checkpoint.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Marco 4 — Plataforma interna e métricas](parte-4-plataforma-metricas.md) | **↑ Índice**<br>[Módulo 12 — Capstone integrador](../README.md) | **Próximo →**<br>[Entrega avaliativa — Módulo 12 (Capstone)](../entrega-avaliativa.md) |

<!-- nav:end -->
