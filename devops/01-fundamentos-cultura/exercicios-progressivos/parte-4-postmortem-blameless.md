# Parte 4 — Template de Postmortem Blameless

**Duração:** 1 hora
**Pré-requisito:** Bloco 4 ([04-cultura-pratica-antipadroes.md](../bloco-4/04-cultura-pratica-antipadroes.md)) + Partes 1, 2, 3

---

## Objetivo

Produzir um **template de postmortem blameless customizado para a CloudStore** — e aplicá-lo a um incidente simulado, gerando um postmortem preenchido. Esse é o **anexo principal** do relatório avaliativo.

---

## Contexto

Revise:

- Seção 1 do Bloco 4 — o que é, princípios, estrutura.
- Seção 1.6 — o script `gerar_postmortem.py`.
- Seção 1.5 — técnica dos "5 Porquês".

---

## Atividades

### Atividade 1 — Customizar o template (30 min)

Use o script `gerar_postmortem.py` do Bloco 4 como **ponto de partida** e **customize** o template para a CloudStore.

**Mudanças obrigatórias** que você deve fazer:

1. **Adicionar** uma seção chamada **"Impacto financeiro estimado"** no topo, com subcampos: receita perdida, custo operacional do incidente, custo de oportunidade.
2. **Adicionar** um campo **"SLO violado"** — qual SLO foi afetado (prepara para o Módulo 10).
3. **Substituir** a tabela de linha do tempo por uma com 5 colunas: `Hora | Evento | Detecção (Manual/Alerta) | Ação realizada | Impacto observado`.
4. **Adicionar** uma seção **"Engajamento comunicacional"**: como clientes foram avisados, se houve incident page, mensagem de status, etc.
5. **Ao final**, incluir um **checklist de validação** com:
    - [ ] Nenhuma linha do documento menciona **nomes próprios** como causa.
    - [ ] Toda "Action Item" tem **dono nomeado** e **prazo**.
    - [ ] Foram feitas **pelo menos 5 iterações** dos "Por quê?".
    - [ ] Documento publicado em canal **público** para toda a engenharia.

**Formato de entrega:** um arquivo `template-postmortem-cloudstore.md` — pronto para a CloudStore copiar para cada incidente.

### Atividade 2 — Incidente simulado (30 min)

Aplique seu template **preenchendo** um postmortem de um incidente fictício da CloudStore. Use o cenário abaixo **ou** invente um próprio (mas baseado em sintomas reais do cenário da CloudStore).

#### Cenário sugerido: "Checkout 502"

> **Data:** 15/03/2026, sexta-feira, 23h48.
>
> Após o deploy semanal noturno, o serviço de checkout começou a retornar HTTP 502 intermitentes. Clientes viam erro ao finalizar compra. A taxa de erro chegou a 35% em 15 minutos.
>
> Os alertas dispararam 18 minutos após o início do problema (o alerta estava configurado para taxa de erro > 40% em janela de 10 min — o incidente ficou **logo abaixo** desse limiar por muito tempo).
>
> Não havia plantão de Dev naquela noite. Somente Ops. O engenheiro de Ops de plantão, sem acesso ao código, não conseguia entender o problema nos logs.
>
> Após 45 min de diagnóstico, o tech lead de Dev foi acordado por telefone. Ele identificou em 8 min que um novo SDK de integração com gateway de pagamento estava fazendo retry em timeout muito agressivo, saturando o pool de conexões HTTP.
>
> O rollback manual levou mais 20 min (deploy manual). Total: 85 min de degradação. Estimativa de perda: R$ 180.000 em vendas não finalizadas + impacto de marca.

**Aplique seu template** e preencha **todos os campos obrigatórios**, incluindo:

- **5 Porquês completos** até uma causa sistêmica.
- **No mínimo 5 action items**, cada um com dono e prazo.
- **Checklist final** preenchido.

### Atividade 3 — Reflexão crítica (dúvidas comuns) (10 min opcional)

Responda em no máximo 3 linhas cada:

1. O postmortem acima teria ficado mais fácil **antes** ou **depois** da transformação DevOps? Por quê?
2. Como o **on-call rotativo** (incluindo Dev) teria mudado esse incidente?
3. Qual **um** action item do seu postmortem teria **maior retorno** — previne mais futuros incidentes? Explique.

---

## Entregáveis desta parte

1. **Template customizado** `template-postmortem-cloudstore.md`.
2. **Postmortem preenchido** `postmortem-checkout-502.md` (ou cenário próprio).
3. **Reflexões** (atividade 3, se feita).

Esses arquivos são **anexo** obrigatório do relatório avaliativo.

---

## Rubrica de autoavaliação

- [ ] Meu template tem **todas as 5 mudanças obrigatórias** da atividade 1.
- [ ] Meu postmortem preenchido não menciona **nenhum nome próprio** como causa.
- [ ] **Todos os action items** têm dono + prazo.
- [ ] Apliquei **5 Porquês completos** até causa sistêmica.
- [ ] Consigo explicar **por que** um postmortem de culpa **produz** os problemas que a CloudStore já tem.

---

## Próximo passo

Siga para a **[Parte 5 — Reflexão e Plano de Ondas](parte-5-reflexao-plano.md)** — última parte.

---

<!-- nav:start -->

| &nbsp; | &nbsp; | &nbsp; |
|:--|:--:|--:|
| **← Anterior**<br>[Parte 3 — Mapeamento do Fluxo de Valor (VSM)](parte-3-mapeamento-fluxo-valor.md) | **↑ Índice**<br>[Módulo 1 — Fundamentos e cultura DevOps](../README.md) | **Próximo →**<br>[Parte 5 — Reflexão Final e Plano de Transformação em Ondas](parte-5-reflexao-plano.md) |

<!-- nav:end -->
