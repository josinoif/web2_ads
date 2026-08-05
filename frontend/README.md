# Front-end: conteúdos e módulos

Este diretório reúne material de **front-end** (HTML, CSS, JavaScript no navegador, frameworks). O foco aqui é a **aplicação** no navegador; a **linguagem JavaScript** (fundamentos, assincronismo, event loop, estruturas de dados) é tratada no módulo **javascript**, na raiz do repositório.

---

## Módulos por tema

| Tema | Pasta / arquivos | Descrição |
|------|------------------|-----------|
| **Layouts (CSS)** | [page-layouts/](page-layouts/) | Flexbox, Grid, usabilidade, decisão, desafios. |
| **Frameworks CSS** | [frameworks-css/](frameworks-css/) | Bootstrap, Tailwind, Bulma, decisão de uso. |
| **JavaScript no navegador** | Ver tabela abaixo | DOM, eventos, requisições HTTP (Fetch, Axios). |
| **React / Next.js / Angular** | [reactjs/](reactjs/), [nextjs/](nextjs/), [angular/](angular/) | Frameworks e bibliotecas de interface. |

---

## JavaScript no navegador

Estes conteúdos aplicam a **linguagem** JavaScript no ambiente do navegador (DOM, BOM, eventos, rede). Para **fundamentos da linguagem** (tipos, `let`/`const`, Promises, async/await, event loop, estruturas de dados), use o módulo **[../javascript/](../javascript/)**.

| Conteúdo | Arquivo | Pré-requisito sugerido |
|----------|---------|-------------------------|
| **Manipulação do DOM** | [dom.md](dom.md) | Conceitos de JavaScript (variáveis, funções, eventos básicos) — [../javascript/](../javascript/). |
| **Eventos no navegador** | [events_js.md](events_js.md) | DOM e fundamentos da linguagem. |
| **Requisições HTTP (Fetch)** | [http_requests_fetch_api.md](http_requests_fetch_api.md) | Promises e async/await — [../javascript/03-assincronismo-event-loop.md](../javascript/03-assincronismo-event-loop.md). |
| **Requisições HTTP (Axios)** | [http_requests_axios.md](http_requests_axios.md) | Idem (Fetch ou Axios). |
| **Exercícios HTTP + DOM + eventos** | [exercicio_fixacao_http_dom.md](exercicio_fixacao_http_dom.md) | DOM, eventos e Fetch (ou Axios). |
| **Web APIs (conteúdo em profundidade)** | [web_apis.md](web_apis.md) | Fundamentos da linguagem; conceito de APIs do navegador (geolocation, câmera, notificações, clipboard, storage, etc.) e exemplos problema+solução. |

**Ordem sugerida:** 1) Módulo [../javascript/](../javascript/) (fundamentação e linguagem). 2) [dom.md](dom.md) e [events_js.md](events_js.md). 3) [http_requests_fetch_api.md](http_requests_fetch_api.md) (e/ou [http_requests_axios.md](http_requests_axios.md)). 4) [exercicio_fixacao_http_dom.md](exercicio_fixacao_http_dom.md).

---

## Outros arquivos

- **Front-end com HTML/CSS/JS (CRUD e Express):** [frontend_html_js.md](frontend_html_js.md) — servidor Express servindo arquivos estáticos e script que consome API externa.
- **Tutoriais:** [pokemon/](pokemon/), [nextjs/](nextjs/), [reactjs/](reactjs/), [angular/](angular/) — projetos que usam JavaScript/TypeScript no cliente (e em alguns casos no servidor com Next.js/Node).

---

*Material alinhado ao ensino superior em Desenvolvimento de Software, com foco em prática, pensamento crítico e link com o mercado.*
