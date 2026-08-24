# Glossário — Coordenação e locks

**Módulo:** [04 — Coordenação/locks](README.md)

| Termo | Definição curta |
|-------|-----------------|
| **Exclusão mútua** | Garantir que **apenas um** writer altere um recurso crítico por vez. |
| **Coordenação distribuída** | Acordar ordem/acesso entre processos **sem memória compartilhada**. |
| **Read-modify-write (RMW)** | Ler valor, decidir, escrever — **vulnerável** a corrida se não for atômico. |
| **Lost update** | Duas escritas; a segunda **sobrescreve** a primeira sem ver o estado atual. |
| **Overbooking** | Mais matrículas/reservas do que vagas — bug clássico sem exclusão mútua. |
| **Lock in-process** | `threading.Lock` — vale **só** dentro de um processo. |
| **Row lock** | Postgres trava linha (`FOR UPDATE`) até fim da transação. |
| **Advisory lock** | Lock lógico Postgres (`pg_advisory_xact_lock`) por ID de recurso. |
| **Optimistic locking** | UPDATE com `version` — falha se outro commitou antes. |
| **Operação atômica** | Executada **indivisível** no servidor (ex.: `findOneAndUpdate`). |
| **Compare-and-set (CAS)** | Escreve **só se** valor/versão ainda é o esperado. |
| **Lock distribuído** | Lock em store compartilhado (Redis) visível a **todas** as instâncias. |
| **`SET NX EX`** | Redis: cria chave **só se não existe**, com TTL em segundos. |
| **Lock órfão** | Processo morre com lock; ou **revive** após TTL e escreve indevidamente. |
| **TTL (lock)** | Tempo máximo de posse — evita deadlock eterno. |
| **Fencing token** | Contador monotônico; storage **rejeita** escrita com token antigo. |
| **Contention** | Muitos writers competindo pelo mesmo lock — latência sobe. |
| **Hot key** | Recurso muito disputado (ex.: última vaga SD-101) — gargalo. |
| **Leader election** | Escolher **um** nó líder para coordenar (etcd, Raft). |
| **Single consumer** | Alternativa ao lock: **uma** fila, **um** worker processa ([01](../01-comunicacao/)). |
| **Lock ≠ CAP** | Lock serializa **quem** escreve; CAP fala **o que** garantir sob partição. Um fluxo pode ser CP **e** precisar de lock. |

Ver também: [glossário do módulo 03](../03-consistencia-cap/glossario.md) (CAP, sync, concerns).
