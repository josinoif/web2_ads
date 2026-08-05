# JavaScript: linguagem e ambientes (navegador e Node.js)

**Público:** Ensino superior (Desenvolvimento de Software)  
**Objetivo:** Fundamentação teórica e prática da **linguagem JavaScript**, com foco em conceitos que sustentam o desenvolvimento front-end e back-end: tipos, escopo, assincronismo, event loop, estruturas de dados e gerenciamento de memória. O material conecta teoria ao mercado, estimula pensamento crítico e tomada de decisão e inclui desafios técnicos para resolver problemas reais.

---

## O que você vai levar dessa aula

- **Fundamentação:** O que é JavaScript, onde roda (navegador e Node.js), por que a linguagem é central no mercado (front-end, back-end, full-stack) e como isso se reflete em vagas e entrevistas.
- **Linguagem:** Conceitos fundamentais — tipos, `let`/`const`/`var`, estruturas de dados (Array, Object, Map, Set), funções, escopo, closures — e como eles aparecem no dia a dia.
- **Assincronismo:** Callbacks, Promises, `async/await`, event loop, diferença entre processamento assíncrono e paralelo e impacto em desempenho e legibilidade.
- **Ambientes:** Quais recursos o JavaScript acessa no **navegador** (DOM, BOM, Fetch, etc.) e no **Node.js** (módulos, `fs`, `http`, etc.), com links para o material de front-end que já cobre DOM, eventos e HTTP.
- **Decisão técnica:** Quando usar Promise vs `async/await`, qual estrutura de dados escolher, como pensar em desempenho e manutenção.
- **Mãos na massa:** Desafios e exercícios de fixação que aplicam a linguagem a problemas reais (APIs, fluxos assíncronos, estruturas de dados).

---

## Estrutura do material

| Ordem | Conteúdo | Arquivo |
|-------|----------|---------|
| 1 | Fundamentação teórica e link com o mercado | [01-fundamentacao-teorica.md](01-fundamentacao-teorica.md) |
| 2 | Linguagem: tipos, let/const, estruturas de dados, escopo, closures | [02-linguagem-fundamentos.md](02-linguagem-fundamentos.md) |
| 3 | Assincronismo: Promises, async/await, event loop, paralelo vs assíncrono | [03-assincronismo-event-loop.md](03-assincronismo-event-loop.md) |
| 4 | JavaScript no navegador e no Node.js — recursos e diferenças | [04-js-navegador-node.md](04-js-navegador-node.md) |
| 5 | Decisão e prática: quando usar o quê | [05-decisao-e-pratica.md](05-decisao-e-pratica.md) |
| 6 | Desafios técnicos | [06-desafios-tecnicos.md](06-desafios-tecnicos.md) |
| 7 | Exercícios de fixação (com respostas) | [07-exercicios-fixacao.md](07-exercicios-fixacao.md) |

---

## Ligação com o material de front-end

O conteúdo de **JavaScript no navegador** (DOM, eventos, requisições HTTP) está no diretório **frontend** e é referenciado neste módulo:

- **Manipulação do DOM:** [../frontend/dom.md](../frontend/dom.md) — conceitos e exercícios.
- **Eventos no navegador:** [../frontend/events_js.md](../frontend/events_js.md) — tipos de eventos, `addEventListener`, exercícios.
- **Requisições HTTP (Fetch e Axios):** [../frontend/http_requests_fetch_api.md](../frontend/http_requests_fetch_api.md) e [../frontend/http_requests_axios.md](../frontend/http_requests_axios.md) — uso de Promises e assincronismo na prática.
- **Exercícios de fixação (HTTP + DOM + eventos):** [../frontend/exercicio_fixacao_http_dom.md](../frontend/exercicio_fixacao_http_dom.md).

Recomendação: estudar primeiro a **fundamentação da linguagem** (arquivos 01 a 03) e depois aplicar no navegador com DOM, eventos e HTTP; o arquivo [04-js-navegador-node.md](04-js-navegador-node.md) faz a ponte entre linguagem e ambientes.

---

## Como usar

1. **Siga a ordem** — A fundamentação e os fundamentos da linguagem sustentam assincronismo e ambientes; decisão e desafios aplicam tudo.
2. **Pratique no console e em pequenos scripts** — Use Node.js e o DevTools do navegador para testar tipos, Promises e estruturas de dados.
3. **Faça os exercícios de fixação** após cada bloco conceitual; use os desafios para integrar linguagem + ambiente (navegador ou Node).
4. **Discuta em grupo** — “Por que async/await em vez de callbacks?” e “Quando usar Map em vez de Object?” são perguntas típicas de entrevista e de revisão de código.

---

*Material alinhado a boas práticas de ensino para adultos: relevância para o mercado, aplicação prática e estímulo ao pensamento crítico e à tomada de decisão.*
