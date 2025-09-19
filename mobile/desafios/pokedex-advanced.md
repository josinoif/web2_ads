# Mini-projeto: “Mini Pokédex – Caçador de Requisições”

## Objetivo

Construir um app React Native (Expo) que liste, busque e detalhe Pokémon consumindo a **PokéAPI v2** via **Fetch API**, com foco em:

- montar **URLs com query params** (paginações e filtros),
- tratar **estados de rede** (carregando, vazio, erro),
- **timeout, retry e cancelamento** de requisições,
- **paginação** (limit/offset),
- **cache local** e **modo offline** básicos,
- e **boas práticas de UX** para apps móveis.

> Pilares técnicos cobrados: uso do **Fetch** no React Native, paginação e parsing de JSON, controle de concorrência, cancelamento/timeout, retry com backoff, cache e offline com `AsyncStorage`. (RN usa Fetch como API de rede padrão. [React Native](https://reactnative.dev/docs/network?utm_source=chatgpt.com))
>  A PokéAPI é **somente GET**, **sem autenticação** e com **paginação por limit/offset**. (Ver “Information” e “Resource Lists/Pagination”). [pokeapi.co](https://pokeapi.co/docs/v2)

------

## Requisitos funcionais

1. **Lista de Pokémon (tela inicial)**

- Consumir `GET https://pokeapi.co/api/v2/pokemon?limit=20&offset=0` e exibir nome + imagem.
- **Scroll infinito**: ao chegar perto do fim, buscar próxima página (incrementar `offset`).
- Mostrar estados: **carregando**, **erro com retry**, **lista vazia**.
- **Imagens**: usar sprite/“official artwork” do Pokémon (caminhos vêm no JSON; sprites são hospedados publicamente). [pokeapi.co+1](https://pokeapi.co/docs/v2)

1. **Busca por nome (client-side com rede)**

- Campo de busca no topo (“pikachu”, “charmander”…).
- **Debounce** (ex.: 400–600ms).
- **Cancelar** requisições anteriores ao digitar (AbortController ou fallback).
- Ao limpar, volta à lista paginada.

1. **Filtro por tipo (ex.: “fire”, “water”)**

- Opção de filtro abre lista de tipos e aplica filtro usando `GET /type/{name}` (o endpoint retorna a lista de Pokémon daquele tipo).
- Implementar **carregamento incremental** dos detalhes (limitar concorrência, p.ex. 5 por vez, para não estourar a rede).
- Dica: a doc de **/type** está no grupo de “Pokémon” da API. [pokeapi.co](https://pokeapi.co/docs/v2)

1. **Detalhe do Pokémon**

- Abrir `GET /pokemon/{name}` ao tocar em um item.
- Exibir: **imagem**, **tipos**, **habilidades** e **stats**.
- (Opcional) `GET /pokemon-species/{id}` para trazer uma **flavor text** (en/pt) quando disponível. [pokeapi.co](https://pokeapi.co/docs/v2)

1. **Robustez de rede (obrigatório)**

- **Timeout** manual (p.ex. 8s) por requisição.
- **Retry com backoff exponencial + jitter** para respostas **5xx** (no máx. 3 tentativas).
- **Cancelamento** de requisições (AbortController; se não suportado no alvo, usar `Promise.race` de fallback).
- **Tratamento de erros** com mensagens amigáveis e botão **Tentar novamente**.

1. **Cache + Offline**

- **Cache em memória** + **persistência** via `AsyncStorage` (TTL sugerido: 30 min) das páginas e detalhes já visitados; ao reabrir o app, usar cache e atualizar em background.
- **Detectar conectividade** com `@react-native-community/netinfo` e exibir banner “Você está offline”; no offline, servir dados do cache. [Expo Docs](https://docs.expo.dev/versions/latest/sdk/netinfo/?utm_source=chatgpt.com)
- Dica ética: a PokéAPI recomenda **cache local** por fair use. [pokeapi.co](https://pokeapi.co/docs/v2)

> Observação: **não usar GraphQL** neste desafio (há rate limit específico de 100 calls/h na instância beta; foque no REST). [pokeapi.co](https://pokeapi.co/docs/graphql?utm_source=chatgpt.com)

------

## Requisitos não-funcionais

- **RN + Expo** (CLI) e **TypeScript**.
- **Arquitetura por módulos**: `api/`, `screens/`, `components/`, `hooks/`, `store/`.
- **Sem segredos no código** (não há auth).
- **Acessibilidade** básica (labels, hitSlop em botões de toque, contraste).
- **UX de estados**: skeletons/placeholders, feedback visual em toques.

------

## Páginas e fluxos

- **Home**: busca, filtro por tipo, lista paginada com infinite scroll.
- **Detalhe**: informações completas do Pokémon.
- **Erros e offline**: telas/overlays dedicados de erro e estado offline.

------

## Endpoints principais (REST v2)

- **Lista paginada**: `/pokemon?limit=20&offset=0` (padrão 20 por página; usar `limit` e `offset`). [pokeapi.co](https://pokeapi.co/docs/v2)
- **Detalhe**: `/pokemon/{id|name}` (contém `sprites`, `types`, `abilities`, `stats`). [pokeapi.co](https://pokeapi.co/docs/v2)
- **Espécie (opcional)**: `/pokemon-species/{id|name}` (flavor text). [pokeapi.co](https://pokeapi.co/docs/v2)
- **Por tipo**: `/type/{name}` (lista de Pokémon daquele tipo). [pokeapi.co](https://pokeapi.co/docs/v2)

------

## Exemplo de requisição (snippet)

```javascript
// utils/http.ts
export async function fetchJson<T>(input: RequestInfo, init?: RequestInit, timeoutMs = 8000): Promise<T> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const res = await fetch(input, { ...init, signal: controller.signal });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return (await res.json()) as T;
  } finally {
    clearTimeout(id);
  }
}
```

> Mostra **timeout + cancelamento** (Fetch do RN). [React Native](https://reactnative.dev/docs/network?utm_source=chatgpt.com)

------

## Critérios de aceite (funcional)

- Infinite scroll funcional, sem requisições duplicadas por página.
- Busca com debounce e **cancelamento** de requisições anteriores.
- Filtro por tipo com limitação de **concorrência** no carregamento de detalhes.
- Tela de detalhe com imagem, tipos, habilidades e stats.
- Tratamento de **erros** (HTTP e rede) com **retry** e **timeout**.
- **Offline** detectado e cache usado corretamente.

------

## Entregáveis

- Repositório com instruções de execução (README).
- Vídeo/gif curto (até 2 min) demonstrando: scroll infinito, busca, filtro, erro simulado, offline.
- Breve texto explicando as decisões de **cache**, **retry** e **concorrência**.

------

# Gabarito de avaliação (rubrica)

**Pontuação total: 100 pts**

1. **HTTP fundamentals (25 pts)**

- [10] Usa **Fetch** corretamente (método GET, headers quando necessário) e parse de JSON. [React Native](https://reactnative.dev/docs/network?utm_source=chatgpt.com)
- [5] Monta URLs com **limit/offset** e entende paginação da API. [pokeapi.co](https://pokeapi.co/docs/v2)
- [5] Respeita a natureza da PokéAPI (**apenas GET**, **sem auth**). [pokeapi.co](https://pokeapi.co/docs/v2)
- [5] Busca endpoints corretos (lista, detalhe, type/species). [pokeapi.co](https://pokeapi.co/docs/v2)

1. **Robustez de rede (20 pts)**

- [6] **Timeout** por requisição.
- [6] **Retry com backoff + jitter** para 5xx (limite de tentativas).
- [4] **Cancelamento** de requisições em busca/debounce.
- [4] Tratamento de erros com UI de “tentar novamente”.

1. **Paginação, busca e filtros (15 pts)**

- [6] Infinite scroll sem duplicação/race conditions.
- [5] Busca com debounce funcional.
- [4] Filtro por tipo + controle de concorrência (ex.: 5 fetches em paralelo).

1. **Cache e offline (15 pts)**

- [8] Cache em memória + `AsyncStorage` com **TTL**. (Fair use recomenda cache. [pokeapi.co](https://pokeapi.co/docs/v2))
- [4] Detecção de **offline** com `@react-native-community/netinfo`. [Expo Docs](https://docs.expo.dev/versions/latest/sdk/netinfo/?utm_source=chatgpt.com)
- [3] Carregamento a partir do cache + refresh em background.

1. **UX de estados (10 pts)**

- [4] Skeleton/placeholder e vazios claros.
- [3] Mensagens de erro amigáveis.
- [3] Acessibilidade básica (labels, áreas de toque).

1. **Arquitetura e código (10 pts)**

- [4] Organização por camadas (api/hooks/components/screens/store).
- [3] Tipagem TS e tipos de resposta da API.
- [3] Legibilidade (nomes, funções puras, separação de responsabilidades).

1. **Extras (opcional, até 5 pts)**

- [2] Prefetch de imagens (e.g., `Image.prefetch`) para a lista.
- [2] Persistência de favoritos (local) com UI dedicada.
- [1] Testes unitários do cliente HTTP (timeout/retry) ou do paginador.

**Faixas de nota sugeridas**

- 90–100: Excelente (pronto para produção didática; cobre todos os pilares).
- 75–89: Muito bom (pequenos ajustes).
- 60–74: Regular (entrega funcional, faltam práticas de robustez).
- <60: Insuficiente (requisitos essenciais ausentes).

------

## Dicas & pegadinhas (para deixar o desafio mais “real”)

- Não bombardear a API: **debounce**, **cache** e limitar concorrência (fair use). [pokeapi.co](https://pokeapi.co/docs/v2)
- **GraphQL beta** tem **rate limit**; use REST. [pokeapi.co](https://pokeapi.co/docs/graphql?utm_source=chatgpt.com)
- Sprites oficiais vêm de repositório público; alguns caminhos podem ser lentos: trate **timeouts** e **fallback**. [GitHub](https://github.com/PokeAPI/sprites?utm_source=chatgpt.com)