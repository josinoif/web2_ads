# Workshop de decisões — Timeout, retry e idempotência

**Módulo:** [06 — Falhas/timeout](README.md)  
Faça depois da [teoria](teoria.md) e, de preferência, do [lab Postgres](tutorial-timeout-postgres.md).  
Termos: [glossario.md](glossario.md).

---

## Como usar

Para cada cenário:

1. Timeout sugerido (ordem de grandeza) e **quem** aplica (cliente / API / DB).  
2. Retry? Quantas vezes? Backoff?  
3. Idempotência **obrigatória**? Como modelar?  
4. Circuit breaker faz sentido?  
5. Ponte CAP: sob estresse, você prefere **503 honesto** ou **aceitar e reconciliar**?

### Critérios de uma boa resposta

Uma resposta sólida cita: (a) **o que pode duplicar**, (b) **se retry é seguro** e por quê, (c) **uma política concreta** (números aproximados ok).

> **Não abra o gabarito agora.** Espelho enxuto só **depois** de tentar: [decisoes-gabarito.md](decisoes-gabarito.md).

---

## Cenário 1 — Matrícula na última vaga

Aluno clica “Matricular”. A API demora 8 s (store sob carga). O app mobile tem timeout de 3 s e **retry automático 5×** sem chave e **sem backoff**.

**Perguntas**

1. O que pode acontecer no banco sem `UNIQUE (disciplina, aluno)`?  
2. Com unique + sem `Idempotency-Key`, o usuário vê o quê na 2ª tentativa? E a **auditoria**/e-mail?  
3. Depois do [lab Postgres](tutorial-timeout-postgres.md): compare Exp. 3 vs Exp. 4 **por aluno** (`status.sh SD-101 <aluno>`), não o total da disciplina.  
4. Isso é mais “CP na borda” ou “AP com reconciliar depois”?  
5. Com 500 alunos retryando no mesmo segundo, o que isso faz com a **carga** no Postgres ([05](../05-escalabilidade/))? Relacione ao Exp. 6.

---

## Cenário 2 — Timeout no meio do commit sync (eco do 03)

Portal usa Postgres sync ([lab partição](../03-consistencia-cap/tutorial-particao-postgres.md)). Cliente recebe timeout; primary pode ter commitado ou não.

**Perguntas**

1. “Tente de novo” sem chave é seguro?  
2. O que a UI deve dizer (“não confirmado — consulte matrículas”)?  
3. Relacione com o 503 do lab 03 sob partição.

---

## Cenário 3 — Feed de avisos

Coordenação publica aviso. Worker/API às vezes toma 502. Produto pede “reenviar automaticamente”.

**Perguntas**

1. Sem `aviso_id` único, o que o aluno vê?  
2. Upsert resolve? Qual campo é a chave? Unique e upsert são a mesma coisa?  
3. Depois do [lab Mongo](tutorial-timeout-mongodb.md): anote contagem antes/depois do retry.

---

## Cenário 4 — Nó de boletim lento 30 s

Só a API de leitura do boletim está lenta. Outras rotas (avisos, login) compartilham o mesmo pool de workers.

**Perguntas**

1. Timeout curto na leitura basta?  
2. Quando abrir circuit breaker?  
3. **Bulkhead** (isolar pool/workers do boletim): sem lab dedicado — argumente se timeout+CB bastam ou se o isolamento evita cascata melhor ([teoria §5](teoria.md)).  
4. Relacione com “gargalo móvel” do [05](../05-escalabilidade/): resiliência sem capacidade ainda satura.

---

## Cenário 5 — Relacional vs documento

Mesma política de retry para matrícula (Postgres) e aviso (Mongo).

**Perguntas**

1. Onde a idempotência é mais “barata” de garantir?  
2. `writeConcern: majority` muda a chance de falso negativo no timeout? (lembre: 1 nó no lab)  
3. O que levaria para o [05 — escala](../05-escalabilidade/) em vez de só resiliência?

---

## Cenário 6 — Pagamento de taxa (conceitual)

Gateway de pagamento: timeout após `POST /charge`.

**Perguntas**

1. Por que idempotency key é **obrigatória** na indústria?  
2. Compare com matrícula do lab — mesmo padrão, risco maior.

---

## Fechamento

Escreva em uma frase a política do seu grupo:

> “Em escritas críticas do portal, nós …”

Leve essa frase para a próxima aula de [07 — cache](../07-cache-distribuido/) (stale ≠ inconsistência de escrita).
