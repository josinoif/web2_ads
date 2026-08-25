# Gabarito enxuto — decisões (módulo 06)

> **Só depois** do workshop em [decisoes.md](decisoes.md). Abrir cedo reduz o aprendizado.

Use para calibrar — são critérios, não redação única.

---

## Cenário 1 — Matrícula

1. Sem unique: N matrículas do mesmo aluno (overbooking / duplicata de negócio).  
2. Com unique: 2ª tentativa tende a **409**; usuário pode ver erro mesmo já matriculado; **e-mails/auditoria** sobem sem chave.  
3. Exp. 3: **deste aluno** `matriculas=1`, `auditoria>1`. Exp. 4 + **4b**: `idempotent_replay`, auditoria estável.  
4. Preferir **503 / “consulte status”** (CP na borda) a inventar sucesso.  
5. 500× retries amplificam RPS no Postgres (Exp. 6 / módulo 05) — jitter + limite + CB.

## Cenário 2 — Timeout no sync (03)

1. Sem chave: **não** é seguro (incerteza de commit).  
2. UI: “não confirmado — atualize / consulte matrículas”, não “falhou com certeza”.  
3. Mesma honestidade do 503 sob partição sync no 03.

## Cenário 3 — Avisos

1. Sem id estável: feed com o mesmo aviso N vezes.  
2. Upsert por `aviso_id` resolve o efeito; unique é o **invariante**, upsert o **padrão de escrita**.  
3. Lab: unique=0 → docs>1; unique=1 → 1 doc.

## Cenário 4 — Boletim lento

1. Timeout curto na leitura ajuda a UI, mas **sem deadline interno** workers ainda podem ficar ocupados (ver `provar-deadline.sh`).  
2. CB quando taxa de erro/latência do boletim explode.  
3. Bulkhead isola melhor a cascata; timeout+CB sozinhos não separam pools.  
4. Sem capacidade ([05]), só resiliência empurra o gargalo.

## Cenário 5 — PG vs Mongo

1. Unique/upsert no documento costuma ser “barato”; chave + tabela de resposta cobre UX/side effects.  
2. Em 1 nó, majority ≈ local; sob réplicas/partição (03) aumenta chance de demora/erro → mais timeouts.  
3. Se o teto é RPS/CPU/conexões → 05; se é política sob falha → 06.

## Cenário 6 — Pagamento

1. Cobrança duplicada tem custo financeiro/legal — key obrigatória no gateway.  
2. Mesmo padrão da matrícula; blast radius maior (dinheiro > e-mail).

---

## Frase-modelo de fechamento

> “Em escritas críticas do portal, nós usamos timeout orçado, retry limitado com backoff/jitter só em erros transientes, Idempotency-Key + unique no efeito, e 503 honesto com CB quando o dependente satura.”
