# Workshop de decisões — Cache distribuído

**Módulo:** [07 — Cache distribuído](README.md)  
Faça depois da [teoria](teoria.md) e, de preferência, do [lab Postgres](tutorial-cache-postgres.md).  
Termos: [glossario.md](glossario.md).

---

## Como usar

Para cada cenário:

1. Cacheia? Onde (local / Redis / nenhum)?  
2. TTL, invalidate-on-write, ou os dois?  
3. Stale aceitável? Por quanto tempo?  
4. Ponte CAP: esta leitura prioriza **responder rápido** ou **dado fresco**? (analogia — não o teorema do 03)  
5. Risco de stampede / hot key?

### Critérios de uma boa resposta

Cite: (a) **o que fica stale**, (b) **quem corrige** (TTL/DEL/bypass), (c) **uma política concreta**.

> **Não abra o gabarito agora.** Espelho enxuto só **depois**: [decisoes-gabarito.md](decisoes-gabarito.md).

---

## Cenário 1 — Dia do boletim

Portal sob tempestade de `GET /boletim`. Postgres no teto ([05](../05-escalabilidade/)). Notas mudam poucas vezes ao dia; aluno reclama se vê nota velha **depois** de a coordenação lançar a correção.

**Perguntas**

1. Cache Redis faz sentido? Local basta com N APIs?  
2. TTL 5 min vs invalidate no `PUT` — o que prioriza?  
3. Depois do lab: compare Exp. 3 (stale) vs Exp. 4 (invalidate).  
4. Isso prioriza responder rápido (stale possível) ou dado fresco após o PUT?

---

## Cenário 2 — Matrícula / vagas restantes

UI mostra “3 vagas” vindo de um cache de 60 s. Dois alunos clicam “matricular” na última vaga.

**Perguntas**

1. Deve cachear `vagas_restantes`?  
2. Relacione com [03](../03-consistencia-cap/) e [04](../04-coordenacao-locks/).  
3. O que cachear **em vez** disso (catálogo da disciplina, ementa)?

---

## Cenário 3 — Feed de avisos

Coordenação publica aviso urgente (“aula cancelada”). Produto tolera até ~30 s de atraso no feed.

**Perguntas**

1. Só TTL basta? Quando ligaria invalidate?  
2. Depois do [lab Mongo](tutorial-cache-mongodb.md): o que o Exp. stale mostrou?  
3. Compare com a política do boletim (cenário 1).

---

## Cenário 4 — Duas réplicas de API

Deploy com api1 e api2. Alguém coloca `dict` em memória “para ir mais rápido”.

**Perguntas**

1. O que quebra na consistência entre réplicas?  
2. O script `comparar-local-vs-redis.sh` (Exp. 1 do lab Mongo) prova o quê?  
3. Hot key no Redis: novo gargalo?

---

## Cenário 5 — Stampede no expire

Chave do boletim do aluno mais acessado expira no horário de pico. Hold do store = 500 ms.

**Perguntas**

1. Sem proteção, o que acontece com `store_reads`?  
2. Single-flight / jitter — quando cada um?  
3. Relacione com thundering herd de retries no [06](../06-falhas-timeout/).

---

## Cenário 6 — Write-through vs cache-aside (conceitual)

Time discute gravar a nota no Postgres **e** no Redis na mesma request vs só invalidar.

**Perguntas**

1. Prós/contras de cada um no portal.  
2. Por que o lab usa cache-aside + invalidate?

---

## Depois do workshop

1. Conferir critérios em [decisoes-gabarito.md](decisoes-gabarito.md).  
2. Cola rápida: [tecnologias-e-escolhas.md](tecnologias-e-escolhas.md).
